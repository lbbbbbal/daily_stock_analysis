from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from trading_system.core.schemas import AgentName, AgentWeight, EquityPoint, Fill, Order, Position


class StateStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    qty REAL NOT NULL,
                    order_type TEXT NOT NULL,
                    limit_price REAL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    qty REAL NOT NULL,
                    price REAL NOT NULL,
                    filled_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT PRIMARY KEY,
                    qty REAL NOT NULL,
                    avg_price REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS equity_curve (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    equity REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_weights (
                    agent TEXT PRIMARY KEY,
                    weight REAL NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_order(self, order: Order) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO orders
                (order_id, symbol, side, qty, order_type, limit_price, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.order_id,
                    order.symbol,
                    order.side.value,
                    order.qty,
                    order.order_type.value,
                    order.limit_price,
                    order.created_at.isoformat(),
                ),
            )
            conn.commit()

    def add_fill(self, fill: Fill) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO fills
                (order_id, symbol, side, qty, price, filled_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    fill.order_id,
                    fill.symbol,
                    fill.side.value,
                    fill.qty,
                    fill.price,
                    fill.filled_at.isoformat(),
                ),
            )
            conn.commit()

    def get_fills(self) -> list[Fill]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM fills ORDER BY id").fetchall()
        return [
            Fill(
                order_id=row["order_id"],
                symbol=row["symbol"],
                side=row["side"],
                qty=row["qty"],
                price=row["price"],
                filled_at=row["filled_at"],
            )
            for row in rows
        ]

    def upsert_position(self, position: Position) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO positions (symbol, qty, avg_price)
                VALUES (?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET qty=excluded.qty, avg_price=excluded.avg_price
                """,
                (position.symbol, position.qty, position.avg_price),
            )
            conn.commit()

    def add_equity_point(self, point: EquityPoint) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO equity_curve (timestamp, equity)
                VALUES (?, ?)
                """,
                (point.timestamp.isoformat(), point.equity),
            )
            conn.commit()

    def set_agent_weight(self, weight: AgentWeight) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_weights (agent, weight, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(agent) DO UPDATE SET weight=excluded.weight, updated_at=excluded.updated_at
                """,
                (weight.agent.value, weight.weight, weight.updated_at.isoformat()),
            )
            conn.commit()

    def add_log(self, level: str, message: str, created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO logs (level, message, created_at)
                VALUES (?, ?, ?)
                """,
                (level, message, created_at),
            )
            conn.commit()

    def get_orders(self) -> list[Order]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM orders").fetchall()
        return [
            Order(
                order_id=row["order_id"],
                symbol=row["symbol"],
                side=row["side"],
                qty=row["qty"],
                order_type=row["order_type"],
                limit_price=row["limit_price"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_positions(self) -> list[Position]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM positions").fetchall()
        return [Position(symbol=row["symbol"], qty=row["qty"], avg_price=row["avg_price"]) for row in rows]

    def get_equity_curve(self) -> Iterable[EquityPoint]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM equity_curve ORDER BY id").fetchall()
        return [
            EquityPoint(timestamp=row["timestamp"], equity=row["equity"]) for row in rows
        ]

    def get_agent_weights(self) -> list[AgentWeight]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM agent_weights").fetchall()
        return [
            AgentWeight(agent=AgentName(row["agent"]), weight=row["weight"], updated_at=row["updated_at"])
            for row in rows
        ]
