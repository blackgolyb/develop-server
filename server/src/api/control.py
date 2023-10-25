from fastapi import Request
from fastapi.routing import APIRouter

from src.services.ngrok import NgrokSSHConnector


router = APIRouter()


@router.get("/get_ssh_url")
async def get_ssh_url(request: Request):
    connector = NgrokSSHConnector()
    return {"host": connector.host, "port": connector.port}
