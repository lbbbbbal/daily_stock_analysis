from __future__ import annotations

from dataclasses import dataclass

from trading_system.core.schemas import RiskCheckResult, TradeIntent


@dataclass
class PortfolioState:
    equity: float
    peak_equity: float
    exposure: float
    positions_count: int

    @property
    def drawdown(self) -> float:
        if self.peak_equity == 0:
            return 0.0
        return (self.equity - self.peak_equity) / self.peak_equity


class RiskEngine:
    def __init__(
        self,
        max_leverage: float = 2.0,
        max_drawdown: float = -0.18,
        min_positions: int = 3,
        max_positions: int = 6,
        stop_loss_min: float = 0.06,
        stop_loss_max: float = 0.12,
        risk_budget: float = 0.025,
    ) -> None:
        self.max_leverage = max_leverage
        self.max_drawdown = max_drawdown
        self.min_positions = min_positions
        self.max_positions = max_positions
        self.stop_loss_min = stop_loss_min
        self.stop_loss_max = stop_loss_max
        self.risk_budget = risk_budget

    def suggested_notional(self, equity: float, stop_loss_distance: float) -> float:
        return (equity * self.risk_budget) / max(stop_loss_distance, 1e-6)

    def evaluate(
        self,
        intent: TradeIntent,
        state: PortfolioState,
        stop_loss_distance: float,
    ) -> RiskCheckResult:
        if state.drawdown <= self.max_drawdown:
            return RiskCheckResult(approved=False, reason="max drawdown reached, block new trades")

        if not (self.stop_loss_min <= stop_loss_distance <= self.stop_loss_max):
            return RiskCheckResult(approved=False, reason="stop loss distance out of bounds")

        new_positions = state.positions_count + 1
        if new_positions < self.min_positions or new_positions > self.max_positions:
            return RiskCheckResult(approved=False, reason="positions count outside 3-6 range")

        leverage = (state.exposure + intent.size) / max(state.equity, 1e-6)
        if leverage > self.max_leverage:
            return RiskCheckResult(approved=False, reason="max leverage exceeded")

        risk_amount = intent.size * stop_loss_distance
        if risk_amount > state.equity * self.risk_budget:
            return RiskCheckResult(approved=False, reason="risk budget exceeded")

        return RiskCheckResult(approved=True, reason="approved")
