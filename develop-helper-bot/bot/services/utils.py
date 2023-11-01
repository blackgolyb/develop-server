import asyncio


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


async def try_to_run(coroutine, attempts, sleep, exception):
    for _ in range(attempts):
        try:
            await coroutine
            break
        except exception:
            await asyncio.sleep(sleep)
