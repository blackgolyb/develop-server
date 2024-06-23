import aiohttp

from config import config


class FailedToGetSSHURLException(RuntimeError):
    ...

def aiohttp_session_provider(func):
    async def wrap(*args, **kwargs):
        if "session" in kwargs:
            return await func(*args, **kwargs)
        
        async with aiohttp.ClientSession() as session:
            return await func(*args, **kwargs, session=session)
        
    return wrap


@aiohttp_session_provider
async def get_ssh_host_and_port(session):
    async with session.get(f"http://{config.server.url}/get_ssh_url") as resp:
        data = await resp.json()

        if not data or data.get("status") == "failed":
            raise FailedToGetSSHURLException("Failed to get ssh url")

        return data["host"], int(data["port"])


@aiohttp_session_provider
async def start_develop_server(session):
    async with session.post(
        f"http://{config.server.url}/start_shh_tunnel",
    ) as resp:
        data = await resp.json()

        if not data or data.get("status") == "failed":
            raise FailedToGetSSHURLException("Failed to get ssh url")

        return data["host"], int(data["port"])

@aiohttp_session_provider
async def create_tunnel(port: int, proto: str, session):
    params = {"port": port, "proto": proto}
    async with session.post(
        f"http://{config.server.url}/create_tunnel", params=params
    ) as resp:
        data = await resp.json()
        return data["host"], data["port"], data["proto"]


@aiohttp_session_provider
async def get_active_tunnels(session):
    async with session.get(
        f"http://{config.server.url}/get_active_tunnels"
    ) as resp:
        return await resp.json()


@aiohttp_session_provider
async def close_http_tunnel(port: int, session):
    params = {"port": port}
    async with session.post(
        f"http://{config.server.url}/close_tunnel", params=params
    ) as resp:
        data = await resp.json()
        return data.get("status") == "ok"
