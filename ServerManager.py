import logging
import os
import subprocess
import threading
import time
from tkinter import messagebox


class ServerManager:
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

    @staticmethod
    def backup_server(selected_appid, backup_path):
        """
        Backup the server with the given App ID to the specified path.
        Args:
            selected_appid (str): The App ID of the selected server.
            backup_path (str): The backup path for the server.
        """
        try:
            logging.info(f"Backing up server {selected_appid} to {backup_path}")
            backup_command = f'some_backup_command {selected_appid} {backup_path}'
            process = subprocess.Popen(backup_command, shell=True)
            process.wait()
            if process.returncode == 0:
                messagebox.showinfo("Server Backup", "Server backup completed successfully.")
            else:
                raise Exception(f"Backup failed with return code {process.returncode}")
        except Exception as e:
            logging.error(f"Error during server backup: {e}")
            messagebox.showerror("Server Backup Error", f"Error during server backup: {str(e)}")

    @staticmethod
    def restore_server(selected_appid, backup_path):
        """
        Restore the server with the given App ID from the specified path.
        Args:
            selected_appid (str): The App ID of the selected server.
            backup_path (str): The backup path for the server.
        """
        try:
            logging.info(f"Restoring server {selected_appid} from {backup_path}")
            restore_command = f'some_restore_command {backup_path} {selected_appid}'
            process = subprocess.Popen(restore_command, shell=True)
            process.wait()
            if process.returncode == 0:
                messagebox.showinfo("Server Restore", "Server restore completed successfully.")
            else:
                raise Exception(f"Restore failed with return code {process.returncode}")
        except Exception as e:
            logging.error(f"Error during server restore: {e}")
            messagebox.showerror("Server Restore Error", f"Error during server restore: {str(e)}")

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
        logging.info(f"Constructed {action} command: {command}")
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
            progress['value'] += 0.03  # Increment the progress bar


# Ensure logging is configured to capture errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
