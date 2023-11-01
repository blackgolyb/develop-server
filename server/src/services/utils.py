import asyncio

from ngrok import Listener


def parse_listener(listener: Listener):
    proto = listener.proto()
    url = listener.url().replace(f"{proto}://", "")

    return {
        "proto": proto,
        "host": url.split(":")[0],
        "port": url.split(":")[1] if len(url.split(":")) > 1 else 80,
    }


async def try_to_run(coroutine, attempts, sleep, exception):
    for _ in range(attempts):
        try:
            await coroutine
            break
        except exception:
            await asyncio.sleep(sleep)
