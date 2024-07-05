import logging
import os
import subprocess
import tempfile
import threading
import time
import zipfile
from tkinter import messagebox

import requests
from tqdm import tqdm


class SteamCmdManager:
    STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    INSTALL_DIR = "C:/SteamCMD"

    @staticmethod
    def install(progress):
        """Create a new thread to install SteamCMD."""
        stop_event = threading.Event()
        t = threading.Thread(target=SteamCmdManager._install_steamcmd, args=(progress, stop_event))
        t.start()

    @staticmethod
    def _install_steamcmd(progress, stop_event):
        """Download and install SteamCMD."""
        try:
            steamcmd_zip_path = SteamCmdManager._download_steamcmd(progress)
            SteamCmdManager._extract_steamcmd(steamcmd_zip_path)
            SteamCmdManager._run_steamcmd(progress, stop_event)
        except Exception as e:
            logging.error(f"An error occurred during SteamCMD installation: {str(e)}")
            messagebox.showerror("SteamCMD Installation", "There was an error installing SteamCMD.")

    @staticmethod
    def _download_steamcmd(progress):
        """Download the SteamCMD installation zip file."""
        steamcmd_zip_path = os.path.join(tempfile.gettempdir(), "steamcmd.zip")
        response = requests.get(SteamCmdManager.STEAMCMD_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(steamcmd_zip_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        logging.info('Downloaded the steamcmd.zip file.')
        return steamcmd_zip_path

    @staticmethod
    def _extract_steamcmd(steamcmd_zip_path):
        """Extract the contents of the downloaded zip file."""
        if not os.path.exists(SteamCmdManager.INSTALL_DIR):
            os.makedirs(SteamCmdManager.INSTALL_DIR)

        with zipfile.ZipFile(steamcmd_zip_path, 'r') as zip_ref:
            zip_ref.extractall(SteamCmdManager.INSTALL_DIR)

        logging.info('Unzipped the steamcmd.zip file.')

    @staticmethod
    def _run_steamcmd(progress, stop_event):
        """Run the SteamCMD installation."""
        os.chdir(SteamCmdManager.INSTALL_DIR)
        progress['value'] = 0
        threading.Thread(target=SteamCmdManager.progress_animation, args=(progress, 100, stop_event)).start()

        process = subprocess.Popen('steamcmd +quit', shell=True)
        process.wait()

        stop_event.set()
        progress['value'] = 100
        progress.stop()

        if process.returncode in (7, 0):
            messagebox.showinfo("SteamCMD Installation", "SteamCMD installed successfully.")
        else:
            error_message = f"There was an error installing SteamCMD. Error code: {process.returncode}"
            logging.error(error_message)
            messagebox.showerror("SteamCMD Installation", error_message)

    @staticmethod
    def progress_animation(progress, target, stop_event):
        """Animate the progress bar until it reaches the target value."""
        while progress['value'] < target and not stop_event.is_set():
            time.sleep(0.1)  # Delay between each increment
            progress['value'] += 0.2  # Increment the progress bar


# Ensure logging is configured to capture errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
