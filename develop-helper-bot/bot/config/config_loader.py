from dataclasses import dataclass
from envparse import Env


@dataclass
class Bot:
    token: str


@dataclass
class Server:
    ssh_user: str
    whitelisted_users: list[str]


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
            whitelisted_users=env.list("WHITELISTED_USERS", subcast=int),
        ),
    )
