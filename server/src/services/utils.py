from ngrok import Listener


def parse_listener(listener: Listener):
    proto = listener.proto()
    url = listener.url().replace(f"{proto}://", "")

    return {
        "proto": proto,
        "host": url.split(":")[0],
        "port": url.split(":")[1] if len(url.split(":")) > 1 else 80,
    }
