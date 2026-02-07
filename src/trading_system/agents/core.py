from __future__ import annotations

from trading_system.core.schemas import AgentName, MarketData, Side, TradeCard


class BaseAgent:
    name: AgentName

    def generate(self, market: MarketData) -> TradeCard:
        raise NotImplementedError


class ThemeAgent(BaseAgent):
    name = AgentName.A1_THEME

    def generate(self, market: MarketData) -> TradeCard:
        return TradeCard(
            agent=self.name,
            symbol=market.symbol,
            side=Side.BUY,
            confidence=0.55,
            thesis="Macro theme rotation (stub)",
            target_price=market.price * 1.1,
            stop_loss=market.price * 0.93,
            horizon_days=7,
            risk_tags=["theme"],
        )


class TechAgent(BaseAgent):
    name = AgentName.A2_TECH

    def generate(self, market: MarketData) -> TradeCard:
        return TradeCard(
            agent=self.name,
            symbol=market.symbol,
            side=Side.BUY,
            confidence=0.6,
            thesis="Technical breakout setup (stub)",
            target_price=market.price * 1.08,
            stop_loss=market.price * 0.94,
            horizon_days=5,
            risk_tags=["tech"],
        )


class EventAgent(BaseAgent):
    name = AgentName.A3_EVENT

    def generate(self, market: MarketData) -> TradeCard:
        return TradeCard(
            agent=self.name,
            symbol=market.symbol,
            side=Side.BUY,
            confidence=0.4,
            thesis="Event catalyst placeholder",
            target_price=market.price * 1.05,
            stop_loss=market.price * 0.95,
            horizon_days=3,
            risk_tags=["event"],
        )


class RiskExecAgent(BaseAgent):
    name = AgentName.A4_RISK_EXEC

    def generate(self, market: MarketData) -> TradeCard:
        return TradeCard(
            agent=self.name,
            symbol=market.symbol,
            side=Side.BUY,
            confidence=0.65,
            thesis="Risk-adjusted execution plan",
            target_price=market.price * 1.06,
            stop_loss=market.price * 0.92,
            horizon_days=4,
            risk_tags=["risk", "exec"],
        )
