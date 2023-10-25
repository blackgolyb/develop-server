import ngrok

from src.services.singleton import SingletonMeta
from config import config


class NgrokSSHConnector(metaclass=SingletonMeta):
    SSH_PORT = 22

    def __init__(self):
        self.ssh_client = None
        self.listener = None

    @property
    def url(self):
        return self.listener.url().replace("tcp://", "")

    @property
    def host(self):
        return self.url.split(":")[0]

    @property
    def port(self):
        return self.url.split(":")[1]

    async def create_tunnel(self):
        if self.listener is not None:
            return
        self.listener = await ngrok.connect(
            self.SSH_PORT, "tcp", authtoken=config.ngrok.auth_token
        )
