from dataclasses import dataclass
from envparse import Env


@dataclass
class Server:
    host: str
    port: int


@dataclass
class Ngrok:
    auth_token: str


@dataclass
class Config:
    server: Server
    ngrok: Ngrok
    debug: bool = True


def load_config() -> Config:
    env = Env()
    env.read_envfile()

    return Config(
        server=Server(
            host=env.str("SERVER_HOST"),
            port=env.int("SERVER_PORT"),
        ),
        ngrok=Ngrok(
            auth_token=env.str("NGROK_AUTH_TOKEN"),
        ),
        debug=env.bool("DEBUG", default=True),
    )
