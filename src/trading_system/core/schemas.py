from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class AgentName(str, Enum):
    A1_THEME = "A1_THEME"
    A2_TECH = "A2_TECH"
    A3_EVENT = "A3_EVENT"
    A4_RISK_EXEC = "A4_RISK_EXEC"


class MarketData(BaseModel):
    symbol: str
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TradeCard(BaseModel):
    agent: AgentName
    symbol: str
    side: Side
    confidence: float = Field(ge=0.0, le=1.0)
    thesis: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    horizon_days: int = 5
    risk_tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TradeIntent(BaseModel):
    symbol: str
    side: Side
    score: float
    size: float
    reason: str
    requires_confirmation: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Order(BaseModel):
    order_id: str
    symbol: str
    side: Side
    qty: float
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Fill(BaseModel):
    order_id: str
    symbol: str
    side: Side
    qty: float
    price: float
    filled_at: datetime = Field(default_factory=datetime.utcnow)


class Position(BaseModel):
    symbol: str
    qty: float
    avg_price: float


class EquityPoint(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    equity: float


class AgentWeight(BaseModel):
    agent: AgentName
    weight: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RiskCheckResult(BaseModel):
    approved: bool
    reason: str


class DailySummary(BaseModel):
    date: str
    pnl: float
    trades: int
    notes: str
