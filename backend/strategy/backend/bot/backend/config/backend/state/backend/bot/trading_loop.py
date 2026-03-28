import asyncio

from backend.execution.engine import ExecutionEngine
from backend.analytics.pnl_engine import PnLEngine
from backend.risk.risk_engine import RiskEngine
from backend.strategy.strategy_engine import StrategyEngine
from backend.state.state_manager import StateManager
from backend.config.config import Config


class TradingLoop:

    def __init__(self):
        self.engine = ExecutionEngine()
        self.pnl_engine = PnLEngine()
        self.risk_engine = RiskEngine()
        self.strategy = StrategyEngine()
        self.state = StateManager()

        self.symbol = Config.SYMBOL
        self.dex = Config.DEFAULT_DEX

        self.running = True

    # ---------------- MAIN LOOP ----------------

    async def run(self):
        print("🚀 Trading loop started...")

        while self.running:
            try:
                await self.step()
                await asyncio.sleep(Config.LOOP_INTERVAL)

            except Exception as e:
                print("ERROR:", e)
                await asyncio.sleep(Config.LOOP_INTERVAL)

    # ---------------- STEP ----------------

    async def step(self):

        # 🔹 1. ЦЕНИ
        prices = await self.engine.get_multi_prices(self.symbol)

        if not prices:
            print("No prices available")
            return

        price = sum(prices.values()) / len(prices)

        # 🔹 2. POSITION (от state, не от blockchain)
        position = self.state.get_position()

        # 🔹 3. PnL
        metrics = self.pnl_engine.calculate(position)

        # 🔹 4. Risk
        risk_decision = self.risk_engine.evaluate(metrics)

        # 🔹 5. Strategy
        decision = self.strategy.decide(price, position, risk_decision)

        print("PRICE:", price)
        print("POSITION:", position)
        print("METRICS:", metrics)
        print("DECISION:", decision)

        # 🔹 6. EXECUTION
        await self.execute(decision, price)

    # ---------------- EXECUTION ----------------

    async def execute(self, decision, price):

        action = decision.get("action")

        # 🔹 DRY RUN защита
        if Config.DRY_RUN:
            print("🟡 DRY RUN: no real trade executed")

        # 🔹 HOLD
        if action == "hold":
            return

        # 🔹 OPEN LONG
        if action == "open_long":
            print("➡️ Opening LONG position")

            if not Config.DRY_RUN:
                await self.engine.multi_execute(
                    symbol=self.symbol,
                    side="buy",
                    size=Config.TRADE_SIZE,
                    split=Config.SPLIT_ORDERS
                )

            # записваме в state
            self.state.update_position({
                "size_usd": 100,
                "entry_price": price
            })

            self.state.add_trade({
                "type": "buy",
                "price": price
            })

        # 🔹 CLOSE
        elif action == "close":
            print("➡️ Closing position")

            if not Config.DRY_RUN:
                print("Real close not implemented")

            self.state.clear_position()

            self.state.add_trade({
                "type": "sell",
                "price": price
            })

        # 🔹 REDUCE
        elif action == "reduce":
            print("➡️ Reducing position")

            pos = self.state.get_position()

            new_size = pos.get("size_usd", 0) * 0.5

            self.state.update_position({
                "size_usd": new_size,
                "entry_price": pos.get("entry_price", price)
            })

            self.state.add_trade({
                "type": "reduce",
                "price": price
            })

    # ---------------- STOP ----------------

    def stop(self):
        self.running = False


# ---------------- RUN ----------------

if __name__ == "__main__":
    loop = TradingLoop()
    asyncio.run(loop.run())
