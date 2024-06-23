from dataclasses import dataclass
from envparse import Env
from functools import lru_cache


@dataclass
class Server:
    host: str
    port: int


@dataclass
class Ngrok:
    auth_token: str


@dataclass
class General:
    attempts: int = 100
    attempt_sleep: int = 3
    debug: bool = True


@dataclass
class Config:
    server: Server
    ngrok: Ngrok
    general: General

@lru_cache
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
        general=General(
            debug=env.bool("DEBUG", default=True),
        ),
    )
