from __future__ import annotations

import os

from trading_system.brokers.paper import PaperBroker
from trading_system.core.schemas import Fill, Side
from trading_system.storage.state_store import StateStore


class MoomooSimBroker:
    def __init__(self, store: StateStore, fallback: PaperBroker | None = None) -> None:
        self.store = store
        self.fallback = fallback or PaperBroker(store)
        self.connected = False

    def connect(self) -> None:
        if os.getenv("MOOMOO_SIM_FAIL") == "1":
            raise ConnectionError("Moomoo SIM connection failed (simulated)")
        self.connected = True

    def submit_order(self, symbol: str, side: Side, qty: float, price: float) -> Fill:
        if not self.connected:
            return self.fallback.submit_order(symbol, side, qty, price)
        return self.fallback.submit_order(symbol, side, qty, price)
