# Dedicated Server Manager

## Overview

The Dedicated Server Manager is a tool designed to simplify the installation and management of game servers using SteamCMD. This application provides an easy-to-use interface to install, update, and manage your dedicated servers with minimal effort.

## Features

- **Server Installation**: Automatically installs servers by verifying the existence of the server in the specified directory using `appid`.
- **Server Update**: Updates servers that are already installed.
- **Progress Bar**: Visual feedback on the installation and update processes.
- **Search Functionality**: Easily find servers from a list using the search bar.
- **SteamCMD Integration**: Set and manage your SteamCMD directory with ease.

## Getting Started

### Prerequisites

- **SteamCMD**: Ensure SteamCMD is installed on your system. You can install it via this application if not already installed.

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/Jubaroo/dedicated-server-manager.git
    cd dedicated-server-manager
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python server_manager.py
    ```

### Usage

1. **Set SteamCMD Directory**:
    - From the File menu, choose `Set SteamCMD Directory` and select the directory where SteamCMD is installed. If SteamCMD is not installed, you can install it using the `Install SteamCMD` option.

2. **Search for Servers**:
    - Use the search bar to type and find the server you want to install.

3. **Select Server**:
    - From the search results, select the server you wish to install.

4. **Choose Installation Directory**:
    - Set the directory where the server should be installed.

5. **Install Server**:
    - Click the `Install Server` button to begin the installation. The progress bar will show the installation status.

6. **Update Server**:
    - If the server is already installed, the application will automatically proceed with the update process.

## How to Use

1. Set the SteamCMD directory using the File menu.
2. Install SteamCMD if it is not already installed.
3. Use the search bar to find a server.
4. Select a server from the list.
5. Choose an installation directory for the server.
6. Click the `Install Server` button to start the installation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
