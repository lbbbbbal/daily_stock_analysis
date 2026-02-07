from __future__ import annotations

import uuid
from datetime import datetime

from trading_system.core.schemas import EquityPoint, Fill, Order, OrderType, Position, Side
from trading_system.storage.state_store import StateStore


class PaperBroker:
    def __init__(self, store: StateStore, starting_cash: float = 100000.0) -> None:
        self.store = store
        self.cash = starting_cash
        self.positions: dict[str, Position] = {p.symbol: p for p in store.get_positions()}

    def submit_order(self, symbol: str, side: Side, qty: float, price: float) -> Fill:
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            qty=qty,
            order_type=OrderType.MARKET,
        )
        self.store.add_order(order)

        fill = Fill(order_id=order.order_id, symbol=symbol, side=side, qty=qty, price=price)
        self.store.add_fill(fill)

        self._apply_fill(fill)
        self._record_equity(price)
        return fill

    def _apply_fill(self, fill: Fill) -> None:
        position = self.positions.get(fill.symbol)
        signed_qty = fill.qty if fill.side == Side.BUY else -fill.qty
        cash_delta = -fill.qty * fill.price if fill.side == Side.BUY else fill.qty * fill.price
        self.cash += cash_delta

        if position:
            new_qty = position.qty + signed_qty
            if new_qty == 0:
                self.positions.pop(fill.symbol, None)
            else:
                avg_price = (
                    (position.avg_price * position.qty + fill.price * signed_qty)
                    / new_qty
                )
                position = Position(symbol=fill.symbol, qty=new_qty, avg_price=avg_price)
                self.positions[fill.symbol] = position
        else:
            position = Position(symbol=fill.symbol, qty=signed_qty, avg_price=fill.price)
            self.positions[fill.symbol] = position

        if position:
            self.store.upsert_position(position)

    def _record_equity(self, last_price: float) -> None:
        equity = self.cash + sum(pos.qty * last_price for pos in self.positions.values())
        self.store.add_equity_point(EquityPoint(timestamp=datetime.utcnow(), equity=equity))
