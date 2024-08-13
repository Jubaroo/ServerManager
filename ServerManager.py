import glob
import logging
import os
import subprocess
import threading
import time
from tkinter import messagebox

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def thread_safe_logging(msg):
    threading.Thread(target=logging.info, args=(msg,)).start()


class ServerManager:
    @staticmethod
    def is_server_installed(install_path, target_appid):
        """
        Check if the server with the specified appid is already installed in the given path by reading the appmanifest file.
        Args:
            install_path (str): The installation path for the server.
            target_appid (str): The appid of the server we are verifying.
        Returns:
            bool: True if the server is installed, False otherwise.
        """
        # Locate all appmanifest files in the directory
        appmanifest_files = glob.glob(os.path.join(install_path, 'steamapps', 'appmanifest_*.acf'))

        # If no appmanifest files are found, return False
        if not appmanifest_files:
            return False

        # Check each appmanifest file
        for appmanifest_file in appmanifest_files:
            with open(appmanifest_file, 'r') as f:
                content = f.read()

                # Check if the appid matches the target appid
                if f'"appid"\t\t"{target_appid}"' in content:
                    # Check if "StateFlags" indicates the application is installed
                    if '"StateFlags"' in content and '"4"' in content:
                        return True

        # If no matching appmanifest file with the correct appid is found, return False
        return False

    @staticmethod
    def install_or_update_server(selected_appid, install_path, progress):
        """
        Install or update the server based on whether it is already installed.
        Args:
            selected_appid (str): The App ID of the selected server.
            install_path (str): The installation path for the server.
            progress (ttk.Progressbar): The progress bar to update.
        """
        if ServerManager.is_server_installed(install_path, selected_appid):
            thread_safe_logging("Server found. Proceeding with update.")
            ServerManager.update_server(selected_appid, install_path, progress)
        else:
            thread_safe_logging("Server not found. Proceeding with installation.")
            ServerManager.install(selected_appid, install_path, progress)

    @staticmethod
    def install(selected_appid, install_path, progress):
        """
        Install the server with the given App ID and installation path.
        Args:
            selected_appid (str): The App ID of the selected server.
            install_path (str): The installation path for the server.
            progress (ttk.Progressbar): The progress bar to update.
        """
        os.makedirs(install_path, exist_ok=True)
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 25)).start()
        progress['value'] = 0

        install_command = ServerManager.construct_command(selected_appid, install_path, "install")
        ServerManager.run_command(install_command, progress, "Server Installation", "Server installed successfully.")
        thread_safe_logging("Server installed successfully.")

    @staticmethod
    def update_server(selected_appid, install_path, progress):
        """
        Update the server with the given App ID and installation path.
        Args:
            selected_appid (str): The App ID of the selected server.
            install_path (str): The installation path for the server.
            progress (ttk.Progressbar): The progress bar to update.
        """
        update_command = ServerManager.construct_command(selected_appid, install_path, "update")
        ServerManager.run_command(update_command, progress, "Server Update", "Server updated successfully.")
        thread_safe_logging("Server updated successfully.")

    @staticmethod
    def construct_command(selected_appid, install_path, action):
        """
        Construct the SteamCMD command for installation or update.
        Args:
            selected_appid (str): The App ID of the selected server.
            install_path (str): The installation path for the server.
            action (str): The action to perform (install/update).

        Returns:
            str: The constructed command.
        """
        command = (
            f'C:/SteamCMD/steamcmd.exe +login anonymous +force_install_dir "{install_path}" '
            f'+app_update {selected_appid} validate +quit'
        )
        thread_safe_logging(f"Constructed {action} command: {command}")
        return command

    @staticmethod
    def run_command(command, progress, title, success_message):
        """
        Run the given command using subprocess and update the progress bar.
        Args:
            command (str): The command to run.
            progress (ttk.Progressbar): The progress bar to update.
            title (str): The title for the message box.
            success_message (str): The success message to display.
        """
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 50)).start()

        process = subprocess.Popen(command, shell=True)
        threading.Thread(target=ServerManager.progress_animation, args=(progress, 75)).start()
        process.wait()

        if process.returncode in (0, 1):
            progress['value'] = 100
            messagebox.showinfo(title, success_message)
        else:
            error_message = f"{title} failed with error code {process.returncode}."
            logging.error(error_message)
            messagebox.showerror(title, error_message)

    @staticmethod
    def progress_animation(progress, target):
        """
        Animate the progress bar until it reaches the target value.
        Args:
            progress (ttk.Progressbar): The progress bar to animate.
            target (int): The target value for the progress bar.
        """
        while progress['value'] < target:
            time.sleep(0.1)  # Delay between each increment
            progress['value'] += 0.02  # Increment the progress bar
