from __future__ import annotations

import os

from trading_system.core.schemas import MarketData


class MoomooUSMarketData:
    def __init__(self) -> None:
        self.connected = False

    def connect(self) -> None:
        if os.getenv("MOOMOO_SIM_FAIL") == "1":
            raise ConnectionError("Moomoo US data connection failed (simulated)")
        self.connected = True

    def get_snapshot(self, symbol: str, fallback_price: float) -> MarketData:
        if not self.connected:
            return MarketData(symbol=symbol, price=fallback_price)
        return MarketData(symbol=symbol, price=fallback_price)
