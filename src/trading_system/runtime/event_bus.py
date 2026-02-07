from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable


EventHandler = Callable[[object], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, payload: object) -> None:
        handlers = list(self._subscribers.get(topic, []))
        if not handlers:
            return
        await asyncio.gather(*(handler(payload) for handler in handlers))
