import aiohttp

from config import config


class FailedToGetSSHURLException(RuntimeError):
    ...


async def get_ssh_host_and_port():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{config.server.url}/get_ssh_url") as resp:
            data = await resp.json()

            if not data or data.get("status") == "failed":
                raise FailedToGetSSHURLException("Failed to get ssh url")

            return data["host"], int(data["port"])


async def start_develop_server():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{config.server.url}/start_shh_tunnel",
        ) as resp:
            data = await resp.json()

            if not data or data.get("status") == "failed":
                raise FailedToGetSSHURLException("Failed to get ssh url")

            return data["host"], int(data["port"])


async def create_tunnel(port: int, proto: str):
    async with aiohttp.ClientSession() as session:
        params = {"port": port, "proto": proto}
        async with session.post(
            f"http://{config.server.url}/create_tunnel", params=params
        ) as resp:
            data = await resp.json()
            return data["host"], data["port"], data["proto"]


async def get_active_tunnels():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{config.server.url}/get_active_tunnels"
        ) as resp:
            return await resp.json()


async def close_http_tunnel(port: int):
    async with aiohttp.ClientSession() as session:
        params = {"port": port}
        async with session.post(
            f"http://{config.server.url}/close_tunnel", params=params
        ) as resp:
            data = await resp.json()
            return data.get("status") == "ok"
