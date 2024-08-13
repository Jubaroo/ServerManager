import asyncio
import logging
from tkinter import messagebox

import aiohttp


class ApiManager:
    def __init__(self, api_url="https://api.steampowered.com/ISteamApps/GetAppList/v2/"):
        self.api_url = api_url

    async def fetch_data(self):
        connector = aiohttp.TCPConnector(limit=10)  # Connection pooling
        timeout = aiohttp.ClientTimeout(total=60)  # Timeout for requests
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            try:
                async with session.get(self.api_url) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logging.error(f"Failed to fetch data: {e}")
                raise Exception("Failed to fetch data due to network issues")

    async def get_dedicated_servers(self, app_ids, update_server_listbox):
        try:
            data = await self.fetch_data()
            apps = data["applist"]["apps"]

            # Efficient filtering and sorting
            dedicated_servers = (
                (app["name"], app["appid"]) for app in apps if "" in app["name"].lower()
            )
            sorted_servers = sorted(dedicated_servers, key=lambda x: x[0].lower())

            # Batch update app_ids
            app_ids.update({name: appid for name, appid in sorted_servers})

            # Debounced UI update (assume `update_server_listbox` is already debounced)
            update_server_listbox()
        except Exception as e:
            logging.error(f"Error processing the API response: {e}")
            messagebox.showerror("API Error", f"There was an error processing the API response: {str(e)}")

    def get_dedicated_servers_thread(self, app_ids, update_server_listbox):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_dedicated_servers(app_ids, update_server_listbox))


if __name__ == "__main__":
    # Example usage
    api_manager = ApiManager()
    app_ids = {}  # Use a regular dict instead of OrderedDict


    def update_server_listbox():
        print("Server list updated.")


    api_manager.get_dedicated_servers_thread(app_ids, update_server_listbox)
