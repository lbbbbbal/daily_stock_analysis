# Trading System MVP

## 运行方式

```bash
PYTHONPATH=src python -m trading_system.cli.run_paper --symbol AAPL --price 190 --use-moomoo --auto-confirm
```

## 环境变量

- `TRADING_DB_PATH`: SQLite 数据库路径（默认 `trading_mvp.sqlite3`）。
- `MOOMOO_SIM_FAIL`: 设置为 `1` 时模拟 moomoo 连接失败并自动回退到 PaperBroker。

## SQLite StateStore

```bash
PYTHONPATH=src python - <<'PY'
from trading_system.storage.state_store import StateStore
from trading_system.core.schemas import Order, Side, OrderType

store = StateStore("/tmp/trading_mvp.sqlite3")
store.add_order(Order(order_id="demo-1", symbol="AAPL", side=Side.BUY, qty=1, order_type=OrderType.MARKET))
print(store.get_orders())
PY
```

## EventBus + PaperBroker

```bash
PYTHONPATH=src python - <<'PY'
import asyncio

from trading_system.runtime.event_bus import EventBus
from trading_system.brokers.paper import PaperBroker
from trading_system.storage.state_store import StateStore
from trading_system.core.schemas import Side

async def main():
    bus = EventBus()
    store = StateStore("/tmp/trading_mvp.sqlite3")
    broker = PaperBroker(store)

    async def on_trade(payload):
        broker.submit_order(payload["symbol"], payload["side"], payload["qty"], payload["price"])

    bus.subscribe("trade", on_trade)
    await bus.publish("trade", {"symbol": "AAPL", "side": Side.BUY, "qty": 1, "price": 190})

asyncio.run(main())
PY
```

## RiskEngine

```bash
PYTHONPATH=src python - <<'PY'
from trading_system.risk.engine import PortfolioState, RiskEngine
from trading_system.core.schemas import TradeIntent, Side

engine = RiskEngine()
state = PortfolioState(equity=100000, peak_equity=110000, exposure=20000, positions_count=3)
intent = TradeIntent(symbol="AAPL", side=Side.BUY, score=0.7, size=5000, reason="demo")
result = engine.evaluate(intent, state, stop_loss_distance=0.08)
print(result)
PY
```

## Agents + Governor

```bash
PYTHONPATH=src python - <<'PY'
from trading_system.agents import ThemeAgent, TechAgent, EventAgent, RiskExecAgent
from trading_system.core.schemas import MarketData, AgentName
from trading_system.governor import Governor

market = MarketData(symbol="AAPL", price=190)
weights = {AgentName.A1_THEME: 0.3, AgentName.A2_TECH: 0.3, AgentName.A3_EVENT: 0.2, AgentName.A4_RISK_EXEC: 0.2}
cards = [agent.generate(market) for agent in (ThemeAgent(), TechAgent(), EventAgent(), RiskExecAgent())]
intents = Governor(weights).build_intents(cards)
print(intents)
PY
```

## Kabu Skeleton

```bash
PYTHONPATH=src python - <<'PY'
from trading_system.brokers.kabu import KabuSkeletonBroker
from trading_system.storage.state_store import StateStore
from trading_system.core.schemas import Side

store = StateStore("/tmp/trading_mvp.sqlite3")
broker = KabuSkeletonBroker(store)
print(broker.create_order_draft("7203", Side.BUY, qty=1, limit_price=2500))
PY
```

## ScoringEngine

```bash
PYTHONPATH=src python - <<'PY'
from trading_system.scoring import ScoringEngine
from trading_system.storage.state_store import StateStore
from trading_system.core.schemas import AgentName

store = StateStore("/tmp/trading_mvp.sqlite3")
scoring = ScoringEngine(store)
weights = scoring.update_weekly_weights({AgentName.A1_THEME: 0.2, AgentName.A2_TECH: 0.5})
print(weights)
print(scoring.daily_summary())
PY
```

## 最小演示流程

```bash
PYTHONPATH=src python -m trading_system.cli.run_paper --symbol AAPL --price 190 --auto-confirm
```

运行后将会：
1. mock 行情（或 moomoo US snapshot）
2. 产出 TradeCards 与 TradeIntents
3. PaperBroker 模拟成交并写入 SQLite
4. 生成 daily summary 与更新 agent 权重
