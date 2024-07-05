import asyncio
import logging
from tkinter import messagebox

import aiohttp


class ApiManager:
    def __init__(self, api_url="https://api.steampowered.com/ISteamApps/GetAppList/v2/"):
        self.api_url = api_url

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                return await response.json()

    async def get_dedicated_servers(self, app_ids, server_menu, server_var, show_selected_appid):
        try:
            data = await self.fetch_data()
            apps = data["applist"]["apps"]
            dedicated_servers = [app for app in apps if "dedicated server" in app["name"].lower()]

            for dedicated_server in dedicated_servers:
                app_ids[dedicated_server["name"]] = dedicated_server["appid"]

            sorted_server_names = sorted(app_ids.keys())
            server_var.set("Choose a game server")
            server_menu["values"] = sorted_server_names
            show_selected_appid()
        except Exception as e:
            logging.error(f"Error processing the API response: {e}")
            messagebox.showerror("API Error", f"There was an error processing the API response: {str(e)}")

    def get_dedicated_servers_thread(self, app_ids, server_menu, server_var, show_selected_appid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_dedicated_servers(app_ids, server_menu, server_var, show_selected_appid))


# Ensure logging is configured to capture errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
