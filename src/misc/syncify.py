from collections.abc import Callable, Awaitable
import asyncio


def syncify[*As, R](async_func: Callable[[*As], Awaitable[R]]) -> Callable[[*As], R]:
    def sync_func(*args: *As) -> R:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(async_func(*args))

    return sync_func
