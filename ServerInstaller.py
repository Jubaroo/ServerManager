import collections
import logging
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Frame, Entry, Button, Label, Progressbar

from ApiManager import ApiManager
from CenterWindow import center_window
from ServerManager import ServerManager
from SteamCmdManager import SteamCmdManager
from Tooltip import Tooltip


class ServerInstaller:
    def __init__(self):
        self.appIds = collections.OrderedDict()
        self.steamcmd_dir = ""
        self.window = tk.Tk()
        self.style = Style(theme="darkly")
        self._configure_window()
        self._create_widgets()
        self.api_manager = ApiManager()
        self.steamcmd_manager = SteamCmdManager()
        self._check_default_steamcmd_directory()
        self._load_servers()

    def _configure_window(self):
        self.window.title("Dedicated Server Manager")
        self.window.geometry("800x800")
        self.window.minsize(650, 600)
        center_window(self.window)
        self.style.theme_use('darkly')

    def _create_widgets(self):
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.columnconfigure(2, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=1)
        self.window.rowconfigure(3, weight=1)
        self.window.rowconfigure(4, weight=1)
        self.window.rowconfigure(5, weight=1)
        self.window.rowconfigure(6, weight=1)

        self.top_frame = Frame(self.window)
        self.top_frame.grid(row=0, column=1, padx=20, pady=10, sticky='ew')

        self.search_var = tk.StringVar()
        self.search_bar = Entry(self.top_frame, textvariable=self.search_var, width=30)
        self.search_bar.pack(padx=5, fill='x')
        self.search_bar.bind('<KeyRelease>', self.filter_servers)
        self.search_bar_tooltip = Tooltip(self.search_bar, "Type to search for a server.")

        self.server_list_frame = Frame(self.window)
        self.server_list_frame.grid(row=1, column=1, padx=20, pady=10, sticky='nsew')

        self.server_listbox = tk.Listbox(self.server_list_frame, width=80, height=15)
        self.server_listbox.grid(row=0, column=0, sticky='nsw')
        self.server_listbox.bind('<<ListboxSelect>>', self.update_selected_appid)

        self.server_count_label = Label(self.server_list_frame, text="Server Count: 0", anchor='e')
        self.server_count_label.grid(row=0, column=1, padx=10, sticky='ne')

        self.refresh_button = Button(self.server_list_frame, text="Refresh Server List", command=self._load_servers)
        self.refresh_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.progress = Progressbar(self.window, length=300, mode='determinate')
        self.progress.grid(row=5, column=1, pady=5)
        self.progress_tooltip = Tooltip(self.progress, "Shows the progress of the current operation.")

        self.install_button = Button(self.window, text="Install Server", command=self.install, state="disabled")
        self.install_button.grid(row=4, column=1, pady=5)
        self.install_button_tooltip = Tooltip(self.install_button, "Click to install the selected server")

        self.install_path_frame = Frame(self.window)
        self.install_path_frame.grid(row=4, column=0, columnspan=3, pady=5, padx=20, sticky='ew')

        self.install_path_var = tk.StringVar(value="Choose server installation directory")
        self.install_path_entry = Entry(self.install_path_frame, textvariable=self.install_path_var, width=50)
        self.install_path_entry.pack(side='left', fill='x', expand=True)
        self.install_path_tooltip = Tooltip(self.install_path_entry, "Enter the server installation path")

        self.browse_button = Button(self.install_path_frame, text="Browse", command=self.browse_install_path)
        self.browse_button.pack(side='left', padx=5)
        self.browse_button_tooltip = Tooltip(self.browse_button, "Click to browse and select the installation directory.")

        self.selected_appId_var = tk.StringVar(value="")
        self.selected_appId_entry = Entry(self.window, textvariable=self.selected_appId_var, width=15, justify='center')
        self.selected_appId_entry.grid(row=2, column=1, pady=5)
        self.selected_appId_tooltip = Tooltip(self.selected_appId_entry, "Displays the App ID of the selected server.")

        self.steamcmd_frame = Frame(self.window)
        self.steamcmd_frame.grid(row=6, column=1, pady=10, padx=20, sticky='ew')

        self.steamcmd_path_button = Button(self.steamcmd_frame, text="Set SteamCMD Directory", command=self.set_steamcmd_directory)
        self.steamcmd_path_button.pack(side='left', padx=5)
        self.steamcmd_path_tooltip = Tooltip(self.steamcmd_path_button, "Set the SteamCMD installation directory")

        self.install_steamcmd_button = Button(self.steamcmd_frame, text="Install SteamCMD", command=self.install_steamcmd)
        self.install_steamcmd_button.pack(side='left', padx=5)
        self.install_steamcmd_tooltip = Tooltip(self.install_steamcmd_button, "Click to install SteamCMD")

    def _load_servers(self):
        try:
            self.api_manager.get_dedicated_servers_thread(self.appIds, self.update_server_listbox)
        except Exception as e:
            logging.error(f"Error starting thread: {e}")
            messagebox.showerror("Error", f"Failed to load servers. Please try again. {str(e)}")

    def update_server_listbox(self):
        self.server_listbox.delete(0, tk.END)
        sorted_servers = sorted(self.appIds.keys(), key=lambda s: s.lower())
        for i, server in enumerate(sorted_servers, 1):
            self.server_listbox.insert(tk.END, f"{i}: {server}")
        self.update_server_count(len(sorted_servers))

    def update_server_count(self, count=None):
        if count is None:
            count = len(self.appIds)
        self.server_count_label.config(text=f"Server Count: {count}")

    def _check_default_steamcmd_directory(self):
        default_steamcmd_dir = "C:\\SteamCMD"
        steamcmd_exe_path = os.path.join(default_steamcmd_dir, "steamcmd.exe")
        if os.path.isfile(steamcmd_exe_path):
            self.steamcmd_dir = default_steamcmd_dir
            self.steamcmd_path_button.config(text="SteamCMD Directory Set", style='success.TButton')
            self.steamcmd_path_tooltip.update_text("SteamCMD has been found!")

    def filter_servers(self, event=None):
        query = self.search_var.get().lower()
        matching_servers = sorted([server for server in self.appIds.keys() if query in server.lower()], key=lambda s: s.lower())
        self.server_listbox.delete(0, tk.END)
        for i, server in enumerate(matching_servers, 1):
            self.server_listbox.insert(tk.END, f"{i}: {server}")
        self.update_server_count(len(matching_servers))

    def update_selected_appid(self, event=None):
        selection = self.server_listbox.curselection()
        if selection:
            selected_server = self.server_listbox.get(selection[0]).split(": ", 1)[1]
            app_id = self.appIds.get(selected_server, "")
            self.selected_appId_var.set(app_id)
            self.install_button.config(state=tk.NORMAL if app_id else tk.DISABLED)

    def install(self):
        selected_appid = self.selected_appId_var.get()
        install_path = os.path.normpath(self.install_path_var.get())
        if install_path and install_path != "Choose server installation directory":
            install_thread = threading.Thread(target=self.perform_installation, args=(selected_appid, install_path))
            install_thread.start()
        else:
            messagebox.showwarning("Path not chosen", "Please choose an installation path.")

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
                self.steamcmd_path_button.config(text="SteamCMD Directory Set", style='success.TButton')
                self.steamcmd_path_tooltip.update_text("SteamCMD has been found!")
            else:
                messagebox.showerror("Error", "steamcmd.exe not found in the selected directory.")

    def install_steamcmd(self):
        path = filedialog.askdirectory()
        if path:
            install_thread = threading.Thread(target=self.steamcmd_manager.install, args=(self.progress,))
            install_thread.start()

    def perform_installation(self, selected_appid, install_path):
        if self.steamcmd_dir:
            self.steamcmd_manager.INSTALL_DIR = self.steamcmd_dir
        ServerManager.install(selected_appid, install_path, self.progress)


if __name__ == "__main__":
    ServerInstaller().window.mainloop()
