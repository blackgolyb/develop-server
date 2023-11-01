import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.control import router as control_router
from src.config import config
from src.services.ngrok import NgrokSSHConnector
from src.services.utils import try_to_run


def configure_fastapi():
    app = FastAPI(title="develop server ", debug=config.general.debug)

    app.include_router(control_router)

    origins = [
        f"http://{config.server.host}:{config.server.port}",
        f"https://{config.server.host}:{config.server.port}",
        f"ws://{config.server.host}:{config.server.port}",
        f"wss://{config.server.host}:{config.server.port}",
    ]

    app = CORSMiddleware(
        app=app,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def configure_uvicorn(fasapi_app):
    uvicorn_config = uvicorn.Config(
        fasapi_app,
        host=config.server.host,
        port=config.server.port,
        log_level="info",
    )

    return uvicorn.Server(uvicorn_config)


async def configure_ngrok():
    ngrok = NgrokSSHConnector()
    await try_to_run(
        coroutine=ngrok.create_tunnel(),
        attempts=config.general.attempts,
        sleep=config.general.attempt_sleep,
        exception=Exception,
    )


async def main():
    fastapi_app = configure_fastapi()
    server = configure_uvicorn(fastapi_app)
    await configure_ngrok()

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
