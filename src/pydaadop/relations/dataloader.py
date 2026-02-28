from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional


class AsyncDataLoader:
    """Simple per-request DataLoader for batching async loads.

    Usage:
      loader = AsyncDataLoader(batch_load_fn)
      future = loader.load(key)
      result = await future

    batch_load_fn should be an async function that accepts a list of keys and
    returns a dict mapping str(key) -> value (or sequence matching keys order).
    """

    def __init__(self, batch_load_fn: Callable[[List[Any]], Awaitable[Dict[str, Any]]]):
        self.batch_load_fn = batch_load_fn
        self._cache: Dict[str, asyncio.Future] = {}
        self._queue: List[Any] = []
        self._dispatch_scheduled = False
        self._lock = asyncio.Lock()

    def load(self, key: Any) -> Awaitable:
        key_s = str(key)
        if key_s in self._cache:
            return self._cache[key_s]

        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self._cache[key_s] = fut
        self._queue.append(key)

        if not self._dispatch_scheduled:
            # schedule dispatch on next loop turn
            loop.call_soon(asyncio.create_task, self._dispatch())
            self._dispatch_scheduled = True

        return fut

    async def _dispatch(self):
        async with self._lock:
            queue = self._queue
            self._queue = []
            self._dispatch_scheduled = False

        if not queue:
            return

        try:
            result_map = await self.batch_load_fn(list(queue))
        except Exception as e:
            # set exception on all futures
            for k in queue:
                k_s = str(k)
                fut = self._cache.pop(k_s, None)
                if fut and not fut.done():
                    fut.set_exception(e)
            return

        for k in queue:
            k_s = str(k)
            fut = self._cache.get(k_s)
            val = result_map.get(k_s) if isinstance(result_map, dict) else None
            if fut and not fut.done():
                try:
                    fut.set_result(val)
                except Exception as e:
                    fut.set_exception(e)


class RequestDataLoaderRegistry:
    """Registry for per-request DataLoader instances."""

    def __init__(self):
        self._loaders: Dict[str, AsyncDataLoader] = {}

    def get_loader(
        self, key: str, batch_load_fn: Callable[[List[Any]], Awaitable[Dict[str, Any]]]
    ) -> AsyncDataLoader:
        if key not in self._loaders:
            self._loaders[key] = AsyncDataLoader(batch_load_fn)
        return self._loaders[key]
