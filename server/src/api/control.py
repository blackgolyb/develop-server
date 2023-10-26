from fastapi.routing import APIRouter
import ngrok
from ngrok import Listener
import json

from src.services.ngrok import NgrokSSHConnector
from src.services.utils import parse_listener


router = APIRouter()


@router.get("/get_ssh_url")
async def get_ssh_url():
    connector = NgrokSSHConnector()
    if await connector.listener() is None:
        return {"status": "failed"}

    return {
        "status": "ok",
        "host": await connector.host(),
        "port": await connector.port(),
    }


@router.post("/start_shh_tunnel")
async def start_shh_tunnel():
    connector = NgrokSSHConnector()
    await connector.create_tunnel()

    return await get_ssh_url()


@router.post("/create_tunnel")
async def create_tunnel(port: int, proto: str):
    metadata = {
        "proto": proto,
        "port": port,
    }
    listener = await ngrok.connect(port, metadata=json.dumps(metadata))
    return parse_listener(listener)


@router.get("/get_active_tunnels")
async def get_active_tunnels():
    listeners: list[Listener] = await ngrok.get_listeners()
    result = []

    for listener in listeners:
        metadata = listener.metadata()
        if not metadata:
            continue

        data = json.loads(metadata)
        result.append(data)

    return result


@router.post("/close_tunnel")
async def close_http_tunnel(port: int):
    listeners: list[Listener] = await ngrok.get_listeners()

    for listener in listeners:
        metadata = listener.metadata()
        if not metadata:
            continue

        data = json.loads(metadata)

        if data.get("port", "") == port:
            await listener.close()
            return {"status": "ok"}

    return {"status": "failed"}
