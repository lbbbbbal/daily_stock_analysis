from __future__ import annotations

import uuid

from trading_system.core.schemas import Order, OrderType, Side
from trading_system.storage.state_store import StateStore


class KabuSkeletonBroker:
    def __init__(self, store: StateStore) -> None:
        self.store = store

    def create_order_draft(self, symbol: str, side: Side, qty: float, limit_price: float) -> Order:
        order = Order(
            order_id=f"kabu-{uuid.uuid4()}",
            symbol=symbol,
            side=side,
            qty=qty,
            order_type=OrderType.LIMIT,
            limit_price=limit_price,
        )
        self.store.add_order(order)
        return order
