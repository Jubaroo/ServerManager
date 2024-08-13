import collections
import logging
import os
import sys
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import Menu, filedialog, messagebox

from ttkbootstrap import Style, Toplevel
from ttkbootstrap.widgets import Frame, Button, Label, Progressbar

from ApiManager import ApiManager
from CenterWindow import center_window
from Console import ConsoleText
from PlaceholderText import PlaceholderEntry
from ServerManager import ServerManager
from SteamCmdManager import SteamCmdManager
from Tooltip import Tooltip

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
VERSION = "1.0.0"


def _log_message(msg, level=logging.INFO):
    log_levels = {
        logging.INFO: logging.info,
        logging.ERROR: logging.error,
        logging.WARNING: logging.warning,
        logging.DEBUG: logging.debug
    }
    log_func = log_levels.get(level, logging.debug)
    log_func(msg)


def show_dialog(title, message):
    dialog = Toplevel()
    dialog.title(title)
    dialog.geometry("400x300")
    dialog.transient()
    dialog.grab_set()
    center_window(dialog)

    label = Label(dialog, text=message, wraplength=350)
    label.pack(pady=20, padx=20)

    ok_button = Button(dialog, text="OK", command=dialog.destroy, style='TButton')
    ok_button.pack(pady=10)

    dialog.mainloop()


def show_about():
    about_message = f"Dedicated Server Manager v{VERSION}\nCreated by Jarrod Schantz"
    show_dialog("About", about_message)


def show_usage():
    usage_message = (
        "How to Use:\n\n"
        "1. Set the SteamCMD directory using the File menu.\n"
        "2. Install SteamCMD if it is not already installed.\n"
        "3. Use the search bar to find a server.\n"
        "4. Select a server from the list.\n"
        "5. Choose an installation directory for the server.\n"
        "6. Click the 'Install Server' button to start the installation."
    )
    show_dialog("How to Use", usage_message)


class ServerInstaller:

    def __init__(self):
        self.on_closing = None
        self.default_font = None
        self.appIds = collections.OrderedDict()
        self.steamcmd_dir = ""
        self.window = tk.Tk()
        self.style = Style(theme="darkly")
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._configure_window()
        self._create_widgets()
        self.api_manager = ApiManager()
        self.steamcmd_manager = SteamCmdManager()
        self._check_default_steamcmd_directory()
        self._load_servers()
        self.window.update_idletasks()
        center_window(self.window)

        # Redirect stdout and stderr to the console widget
        self.console_text = ConsoleText(self.window, height=20, state='disabled')
        self.console_text.grid(row=7, column=0, columnspan=3, sticky='nsew')

        sys.stdout = self.console_text
        sys.stderr = self.console_text

    def thread_safe_logging(self, msg, level=logging.INFO):
        self.executor.submit(_log_message, msg, level)

    def _configure_window(self):
        self.window.title("Dedicated Server Manager")
        self.window.geometry("800x900")
        self.window.minsize(650, 600)
        self.style.theme_use('darkly')

    def _create_widgets(self):
        self._create_menu()

        for i in range(3):
            self.window.columnconfigure(i, weight=1)
        for i in range(7):
            self.window.rowconfigure(i, weight=1)

        self.default_font_size = 10
        self.default_font = ("Arial", self.default_font_size)

        self.style.configure('TButton', font=self.default_font)
        self.style.configure('TLabel', font=self.default_font)
        self.style.configure('TEntry', font=self.default_font)

        self._create_top_frame()
        self._create_server_list_frame()
        self._create_install_frame()

    def _create_menu(self):
        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        self.set_steamcmd_dir_menu = tk.BooleanVar()
        file_menu.add_checkbutton(label="Set SteamCMD Directory", command=self.set_steamcmd_directory,
                                  variable=self.set_steamcmd_dir_menu)
        file_menu.add_command(label="Install SteamCMD", command=self.install_steamcmd)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Choose Font Size", command=self.choose_font_size)

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=show_usage)
        help_menu.add_command(label="About", command=show_about)

    def _create_top_frame(self):
        top_frame = Frame(self.window)
        top_frame.grid(row=0, column=1, padx=20, pady=10, sticky='ew')

        self.search_var = tk.StringVar()
        self.search_bar = PlaceholderEntry(top_frame, textvariable=self.search_var, width=30,
                                           placeholder="Type to search for a server", active_color='white')
        self.search_bar.config(font=self.default_font)
        self.search_bar.pack(side='left', padx=5, fill='x', expand=True)
        self.search_bar.bind('<KeyRelease>', self.filter_servers)
        Tooltip(self.search_bar, "Type to search for a server.")

        # Create a clear button right next to the search bar
        clear_button = Button(top_frame, text="Clear", command=self.clear_search, style='TButton', width=8)
        clear_button.pack(side='left', padx=5)
        Tooltip(clear_button, "Click to clear the search field.")

    def _create_server_list_frame(self):
        server_list_frame = Frame(self.window)
        server_list_frame.grid(row=1, column=1, padx=20, pady=10, sticky='nsew')

        # Configure the columns and rows for centering
        server_list_frame.columnconfigure(0, weight=1)
        server_list_frame.rowconfigure(0, weight=1)
        server_list_frame.rowconfigure(1, weight=0)  # Ensure the button does not stretch too much

        self.server_listbox = tk.Listbox(server_list_frame, width=80, height=15, font=self.default_font)
        self.server_listbox.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')  # Center the listbox
        self.server_listbox.bind('<<ListboxSelect>>', self.update_selected_appid)

        refresh_button = Button(server_list_frame, text="Refresh Server List", command=self._load_servers,
                                style='TButton')
        refresh_button.grid(row=1, column=0, pady=5)  # Center the button without using sticky='ew'
        Tooltip(refresh_button, "Click to refresh the server list.")

    def _create_install_frame(self):
        self.progress = Progressbar(self.window, length=200, mode='determinate')
        self.progress.grid(row=5, column=1, pady=5, sticky='ew')
        Tooltip(self.progress, "Shows the progress of the current operation.")

        self.install_button = Button(self.window, text="Install Server", command=self.install, state="disabled",
                                     style='TButton')
        self.install_button.grid(row=4, column=1, pady=5)
        Tooltip(self.install_button, "Click to install the selected server")

        install_path_frame = Frame(self.window)
        install_path_frame.grid(row=3, column=0, columnspan=3, pady=5, padx=20, sticky='ew')

        self.install_path_var = tk.StringVar(value="")
        self.install_path_entry = PlaceholderEntry(
            install_path_frame,
            textvariable=self.install_path_var,
            width=20,
            placeholder="Choose server installation directory",
            active_color='white')
        self.install_path_entry.config(font=self.default_font)
        self.install_path_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        Tooltip(self.install_path_entry, "Enter the server installation path")

        browse_button = Button(install_path_frame, text="Browse", command=self.browse_install_path, style='TButton')
        browse_button.pack(side='left', padx=5)
        Tooltip(browse_button, "Click to browse and select the installation directory.")

        self.selected_appId_var = tk.StringVar(value="")
        self.selected_appId_entry = PlaceholderEntry(
            self.window,
            textvariable=self.selected_appId_var,
            width=15,
            placeholder="App ID",
            active_color='white',
            justify='center'
        )
        self.selected_appId_entry.config(font=self.default_font)
        self.selected_appId_entry.grid(row=2, column=1, pady=5)
        Tooltip(self.selected_appId_entry, "Displays the App ID of the selected server.")

    def adjust_font_size(self, delta):
        self.default_font_size += delta
        self.default_font = ("Arial", self.default_font_size)

        self.style.configure('TButton', font=self.default_font)
        self.style.configure('TLabel', font=self.default_font)
        self.style.configure('TEntry', font=self.default_font)

        for widget in self.window.winfo_children():
            if isinstance(widget, (tk.Entry, tk.Label, tk.Button, tk.Listbox, tk.Text)):
                widget.config(font=self.default_font)
            for child in widget.winfo_children():
                if isinstance(child, (tk.Entry, tk.Label, tk.Button, tk.Listbox, tk.Text)):
                    child.config(font=self.default_font)

        self.window.update_idletasks()

    def choose_font_size(self):
        dialog = Toplevel()
        dialog.title("Choose Font Size")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()
        center_window(dialog)

        current_font_label = Label(dialog, text=f"Current Font Size: {self.default_font_size}")
        current_font_label.pack(pady=10)

        new_font_label = Label(dialog, text="New Font Size:")
        new_font_label.pack(pady=5)

        font_size_var = tk.IntVar(value=self.default_font_size)
        font_size_spinbox = tk.Spinbox(dialog, from_=8, to=72, textvariable=font_size_var)
        font_size_spinbox.pack(pady=5)

        def apply_font_size():
            self.default_font_size = font_size_var.get()
            self.adjust_font_size(0)
            dialog.destroy()

        apply_button = Button(dialog, text="Apply", command=apply_font_size)
        apply_button.pack(pady=10)

        dialog.mainloop()

    def clear_search(self):
        self.search_var.set("")  # Clear the search field
        self.search_bar.put_placeholder()  # Reset the placeholder
        self.update_server_listbox()  # Repopulate the listbox with all servers

    def _load_servers(self):
        try:
            self.api_manager.get_dedicated_servers_thread(self.appIds, self.update_server_listbox)
        except Exception as e:
            error_msg = f"Failed to load servers. Please try again. {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.thread_safe_logging(error_msg)

    def _check_default_steamcmd_directory(self):
        # Check for default SteamCMD directory
        default_steamcmd_dir = "C:\\SteamCMD"
        steamcmd_exe_path = os.path.join(default_steamcmd_dir, "steamcmd.exe")
        if os.path.isfile(steamcmd_exe_path):
            self.steamcmd_dir = default_steamcmd_dir
            self.set_steamcmd_dir_menu.set(True)

    def filter_servers(self, event=None):
        query = self.search_var.get().lower()  # Get the text from the search field and convert it to lowercase
        matching_servers = sorted(
            [server for server in self.appIds.keys() if query in server.lower()],
            key=lambda s: s.lower()
        )
        self.server_listbox.delete(0, tk.END)
        for server in matching_servers:
            self.server_listbox.insert(tk.END, server)
        self.update_server_count(len(matching_servers))

    def update_server_listbox(self):
        # Update server listbox with sorted servers
        self.server_listbox.delete(0, tk.END)
        sorted_servers = sorted(self.appIds.keys(), key=lambda s: s.lower())
        for server in sorted_servers:
            self.server_listbox.insert(tk.END, server)  # Insert server names without numbering
        self.update_server_count(len(sorted_servers))

    def update_server_count(self, count=None):
        if count is None:
            count = len(self.appIds)
        new_title = f"Dedicated Server Manager - Server Count: {count}"
        self.window.title(new_title)

    def update_selected_appid(self, event=None):
        selection = self.server_listbox.curselection()
        if selection:
            selected_server = self.server_listbox.get(selection[0])
            app_id = self.appIds.get(selected_server, "")
            self.selected_appId_var.set(app_id)

            # Manually clear placeholder if text is set
            self.selected_appId_entry.clear_placeholder()

            self.install_button.config(state=tk.NORMAL if app_id else tk.DISABLED)

    def install(self):
        selected_appid = self.selected_appId_var.get()
        install_path = os.path.normpath(self.install_path_var.get())
        if install_path and install_path != "Choose server installation directory":
            self.executor.submit(self.perform_installation, selected_appid, install_path)
        else:
            messagebox.showwarning("Path not chosen", "Please choose an installation path.")
            self.thread_safe_logging("Please choose an installation path.")

    def browse_install_path(self):
        path = filedialog.askdirectory()
        if path:
            self.install_path_var.set(path)

    def set_steamcmd_directory(self):
        path = filedialog.askdirectory()
        if path:
            steamcmd_exe_path = os.path.join(path, "steamcmd.exe")
            if os.path.isfile(steamcmd_exe_path):
                self.steamcmd_dir = path
                self.set_steamcmd_dir_menu.set(True)
            else:
                error_msg = "steamcmd.exe not found in the selected directory."
                messagebox.showerror("Error", error_msg)
                self.thread_safe_logging(error_msg)

    def install_steamcmd(self):
        path = filedialog.askdirectory()
        if path:
            threading.Thread(target=self.steamcmd_manager.install, args=(self.progress,)).start()

    def perform_installation(self, selected_appid, install_path):
        if self.steamcmd_dir:
            self.steamcmd_manager.INSTALL_DIR = self.steamcmd_dir
        ServerManager.install_or_update_server(selected_appid, install_path, self.progress)


def on_closing(self):
    self.executor.shutdown(wait=True)
    self.window.quit()


if __name__ == "__main__":
    installer = ServerInstaller()
    installer.window.protocol("WM_DELETE_WINDOW", installer.on_closing)
    installer.window.mainloop()
