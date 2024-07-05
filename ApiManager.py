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
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch data: {response.status}")

    async def get_dedicated_servers(self, app_ids, update_server_listbox):
        try:
            data = await self.fetch_data()
            apps = data["applist"]["apps"]
            dedicated_servers = [app for app in apps if "dedicated server" in app["name"].lower()]

            for dedicated_server in dedicated_servers:
                app_ids[dedicated_server["name"]] = dedicated_server["appid"]

            update_server_listbox()
        except Exception as e:
            logging.error(f"Error processing the API response: {e}")
            messagebox.showerror("API Error", f"There was an error processing the API response: {str(e)}")

    def get_dedicated_servers_thread(self, app_ids, update_server_listbox):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_dedicated_servers(app_ids, update_server_listbox))
