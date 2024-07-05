import collections
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ApiManager import ApiManager
from SearchableCombobox import SearchableCombobox
from ServerManager import ServerManager
from SteamCmdManager import SteamCmdManager
from Tooltip import Tooltip


def center_window(window):
    # Center the window on the screen
    window.update_idletasks()  # Update "requested size" from geometry manager

    window_width = window.winfo_reqwidth()  # Get window width
    window_height = window.winfo_reqheight()  # Get window height

    screen_width = window.winfo_screenwidth()  # Get screen width
    screen_height = window.winfo_screenheight()  # Get screen height

    x = (screen_width - window_width) / 2  # Calculate x position
    y = (screen_height - window_height) / 2  # Calculate y position

    window.geometry("+%d+%d" % (x, y))  # Set window position


class ServerInstaller:
    def __init__(self):
        """Initialize the ServerInstaller application."""
        self.appIds = collections.OrderedDict()
        self.window = tk.Tk()
        self._configure_window()
        self._create_widgets()
        self.api_manager = ApiManager()
        self.steamcmd_manager = SteamCmdManager()
        self._load_servers()

    def _configure_window(self):
        """Configure the main application window."""
        self.window.title("Dedicated Server Manager")
        self.window.geometry("500x500")
        self.window.minsize(500, 400)
        center_window(self.window)

    def _create_widgets(self):
        """Create and place the widgets in the window."""
        self.server_var = tk.StringVar(value="Loading servers...")
        self.server_menu = SearchableCombobox(self.window, textvariable=self.server_var, width=60, state="readonly")
        self.server_menu.pack(pady=10)

        self.progress = ttk.Progressbar(self.window, length=300, mode='determinate')
        self.progress.pack(pady=10)

        self.install_button = ttk.Button(self.window, text="Install Server", command=self.install, state="disabled")
        self.install_button.pack(pady=10)
        self.install_button_tooltip = Tooltip(self.install_button, "")

        self.install_path_var = tk.StringVar(value="Choose server installation directory")
        self.install_path_entry = ttk.Entry(self.window, textvariable=self.install_path_var, width=50)
        self.install_path_entry.pack(pady=10)
        self.install_path_tooltip = Tooltip(self.install_path_entry, "Enter the server installation path")

        self.selected_appId_var = tk.StringVar(value="")
        self.selected_appId_entry = ttk.Entry(self.window, textvariable=self.selected_appId_var, width=50,
                                              state="readonly")
        self.selected_appId_entry.pack(pady=10)

        self.install_steamcmd_button = ttk.Button(self.window, text="Install SteamCMD", command=self.install_steamcmd)
        self.install_steamcmd_button.pack(pady=10)
        self.install_steamcmd_tooltip = Tooltip(self.install_steamcmd_button, "")

    def _load_servers(self):
        """Load the servers from the API."""
        thread = self.api_manager.get_dedicated_servers_thread(self.appIds, self.server_menu, self.server_var,
                                                               self.update_selected_appid)
        if thread is not None:
            thread.start()
        else:
            messagebox.showerror("Error", "Failed to load servers. Please try again.")

    def update_selected_appid(self):
        """Update the selected App ID based on the chosen server."""
        selected_server = self.server_var.get()
        self.selected_appId_var.set(self.appIds.get(selected_server, ""))

    def install(self):
        """Install the selected server."""
        selected_appid = self.appIds.get(self.server_var.get())
        install_path = os.path.normpath(self.install_path_var.get())
        if install_path and install_path != "Choose server installation directory":
            install_thread = threading.Thread(target=self.perform_installation, args=(selected_appid, install_path))
            install_thread.start()
        else:
            messagebox.showwarning("Path not chosen", "Please choose an installation path.")

    def install_steamcmd(self):
        """Install SteamCMD."""
        path = filedialog.askdirectory()
        if path:
            install_thread = threading.Thread(target=self.steamcmd_manager._install_steamcmd, args=(path, self.progress))
            install_thread.start()

    def perform_installation(self, selected_appid, install_path):
        """Perform the server installation in a separate thread."""
        ServerManager.install(selected_appid, install_path, self.progress)

    def perform_update(self, selected_appid, install_path):
        """Perform the server update in a separate thread."""
        ServerManager.update_server(selected_appid, install_path, self.progress)


if __name__ == "__main__":
    ServerInstaller().window.mainloop()
