from dataclasses import dataclass
from envparse import Env


@dataclass
class Bot:
    token: str


@dataclass
class Server:
    ssh_user: str
    host: str
    port: int
    whitelisted_users: list[int]

    @property
    def url(self):
        return f"{self.host}:{self.port}"


@dataclass
class Config:
    bot: Bot
    server: Server


def load_config():
    env = Env()
    env.read_envfile()

    return Config(
        bot=Bot(token=env.str("BOT_TOKEN")),
        server=Server(
            ssh_user=env.str("SSH_USER"),
            host=env.str("SERVER_HOST"),
            port=env.str("SERVER_PORT"),
            whitelisted_users=env.list("WHITELISTED_USERS", subcast=int),
        ),
    )
