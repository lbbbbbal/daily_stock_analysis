from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from trading_system.core.schemas import AgentName, Side, TradeCard, TradeIntent


class Governor:
    def __init__(self, agent_weekly_weights: dict[AgentName, float]) -> None:
        self.agent_weekly_weights = agent_weekly_weights

    def _score_cards(self, cards: Iterable[TradeCard]) -> dict[tuple[str, Side], float]:
        scores: dict[tuple[str, Side], float] = defaultdict(float)
        for card in cards:
            weight = self.agent_weekly_weights.get(card.agent, 0.0)
            scores[(card.symbol, card.side)] += card.confidence * weight
        return scores

    def build_intents(self, cards: list[TradeCard]) -> list[TradeIntent]:
        scores = self._score_cards(cards)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        target_count = min(max(len(ranked), 3), 6)
        intents: list[TradeIntent] = []
        for (symbol, side), score in ranked[:target_count]:
            intent = TradeIntent(
                symbol=symbol,
                side=side,
                score=score,
                size=5000 * max(score, 0.1),
                reason="weighted agent vote",
                requires_confirmation=self._needs_confirmation(cards, symbol),
            )
            intents.append(intent)
        return intents

    def _needs_confirmation(self, cards: list[TradeCard], symbol: str) -> bool:
        relevant = [card for card in cards if card.symbol == symbol]
        for card in relevant:
            if "high-risk" in card.risk_tags or card.confidence < 0.35:
                return True
        return False

    def confirm_intents(self, intents: list[TradeIntent]) -> list[TradeIntent]:
        if not any(intent.requires_confirmation for intent in intents):
            return intents
        answer = input("High risk intents detected. Proceed? (y/n): ").strip().lower()
        if answer != "y":
            return [intent for intent in intents if not intent.requires_confirmation]
        return intents
