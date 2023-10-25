import aiohttp

from config import config


async def get_ssh_host_and_port():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{config.server.url}/get_ssh_url") as resp:
            data = await resp.json()

            return data["host"], int(data["port"])
