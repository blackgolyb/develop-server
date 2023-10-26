import ngrok
from ngrok import Listener
import json


from src.services.singleton import SingletonMeta
from config import config


class NgrokSSHConnector(metaclass=SingletonMeta):
    SSH_PORT = 22

    def __init__(self):
        self.ssh_client = None
        self.listener_id: str | None = None

    async def listener(self) -> Listener | None:
        listeners: list[Listener] = await ngrok.get_listeners()

        for listener in listeners:
            if listener.id() == self.listener_id:
                return listener

        return None

    async def url(self):
        listener = await self.listener()
        return listener.url().replace("tcp://", "")

    async def host(self):
        url = await self.url()
        return url.split(":")[0]

    async def port(self):
        url = await self.url()
        return url.split(":")[1]

    async def create_tunnel(self):
        prev_listener = await self.listener()
        if prev_listener is not None:
            return

        metadata = {
            "proto": "tcp",
            "port": self.SSH_PORT,
        }
        listener = await ngrok.connect(
            self.SSH_PORT,
            "tcp",
            authtoken=config.ngrok.auth_token,
            metadata=json.dumps(metadata),
        )
        self.listener_id = listener.id()
