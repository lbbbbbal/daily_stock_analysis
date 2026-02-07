from __future__ import annotations

import math
from datetime import datetime

from trading_system.core.schemas import AgentName, AgentWeight, DailySummary, Fill
from trading_system.storage.state_store import StateStore


class ScoringEngine:
    def __init__(self, store: StateStore) -> None:
        self.store = store

    def daily_summary(self, date: str | None = None) -> DailySummary:
        fills = self.store.get_fills()
        equity = list(self.store.get_equity_curve())
        if equity:
            pnl = equity[-1].equity - equity[0].equity
        else:
            pnl = 0.0
        summary_date = date or datetime.utcnow().date().isoformat()
        return DailySummary(date=summary_date, pnl=pnl, trades=len(fills), notes="auto-generated")

    def update_weekly_weights(self, scores: dict[AgentName, float], floor: float = 0.05) -> list[AgentWeight]:
        exps = {agent: math.exp(score) for agent, score in scores.items()}
        total = sum(exps.values()) or 1.0
        weights = {agent: exps[agent] / total for agent in exps}
        floored = {agent: max(weight, floor) for agent, weight in weights.items()}
        normalize = sum(floored.values()) or 1.0
        final_weights = {agent: weight / normalize for agent, weight in floored.items()}
        stored = []
        for agent, weight in final_weights.items():
            record = AgentWeight(agent=agent, weight=weight)
            self.store.set_agent_weight(record)
            stored.append(record)
        return stored
