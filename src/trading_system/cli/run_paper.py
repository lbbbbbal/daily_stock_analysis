from __future__ import annotations

import argparse
import os

from trading_system.agents import EventAgent, RiskExecAgent, TechAgent, ThemeAgent
from trading_system.brokers.moomoo import MoomooSimBroker
from trading_system.brokers.paper import PaperBroker
from trading_system.core.schemas import AgentName, MarketData, Side
from trading_system.data.marketdata.moomoo_us import MoomooUSMarketData
from trading_system.governor import Governor
from trading_system.risk.engine import PortfolioState, RiskEngine
from trading_system.scoring import ScoringEngine
from trading_system.storage.state_store import StateStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Run trading system paper MVP.")
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--price", type=float, default=190.0)
    parser.add_argument("--use-moomoo", action="store_true")
    parser.add_argument("--auto-confirm", action="store_true")
    args = parser.parse_args()

    db_path = os.getenv("TRADING_DB_PATH", "trading_mvp.sqlite3")
    store = StateStore(db_path)

    broker: PaperBroker
    market = MarketData(symbol=args.symbol, price=args.price)
    if args.use_moomoo:
        paper = PaperBroker(store)
        moomoo_broker = MoomooSimBroker(store, fallback=paper)
        data = MoomooUSMarketData()
        try:
            moomoo_broker.connect()
            data.connect()
            broker = moomoo_broker
            market = data.get_snapshot(args.symbol, args.price)
        except ConnectionError:
            broker = paper
    else:
        broker = PaperBroker(store)

    agents = [ThemeAgent(), TechAgent(), EventAgent(), RiskExecAgent()]
    cards = [agent.generate(market) for agent in agents]
    weights = {weight.agent: weight.weight for weight in store.get_agent_weights()}
    if not weights:
        weights = {AgentName.A1_THEME: 0.3, AgentName.A2_TECH: 0.3, AgentName.A3_EVENT: 0.2, AgentName.A4_RISK_EXEC: 0.2}

    governor = Governor(weights)
    intents = governor.build_intents(cards)
    if not args.auto_confirm:
        intents = governor.confirm_intents(intents)

    positions = store.get_positions()
    exposure = sum(pos.qty * market.price for pos in positions)
    state = PortfolioState(equity=100000, peak_equity=100000, exposure=exposure, positions_count=len(positions))
    risk = RiskEngine()

    for intent in intents:
        card = next((c for c in cards if c.symbol == intent.symbol), None)
        if card and card.stop_loss:
            stop_loss_distance = abs((market.price - card.stop_loss) / market.price)
        else:
            stop_loss_distance = 0.08
        result = risk.evaluate(intent, state, stop_loss_distance=stop_loss_distance)
        if result.approved:
            broker.submit_order(intent.symbol, intent.side, qty=1, price=market.price)

    scoring = ScoringEngine(store)
    summary = scoring.daily_summary()
    weekly_scores = {card.agent: card.confidence for card in cards}
    scoring.update_weekly_weights(weekly_scores)

    print("Trade cards:")
    for card in cards:
        print(card.model_dump_json(indent=2))
    print("Daily summary:")
    print(summary.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
