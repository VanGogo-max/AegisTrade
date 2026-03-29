import asyncio

from backend.execution.engine import ExecutionEngine
from backend.analytics.pnl_engine import PnLEngine
from backend.risk.risk_engine import RiskEngine
from backend.strategy.strategy_engine import StrategyEngine
from backend.state.state_manager import StateManager
from backend.config.config import Config
from backend.utils.logger import Logger


class TradingLoop:

    def __init__(self):
        self.engine = ExecutionEngine()
        self.pnl_engine = PnLEngine()
        self.risk_engine = RiskEngine()
        self.strategy = StrategyEngine()
        self.state = StateManager()
        self.logger = Logger()

        self.symbol = Config.SYMBOL
        self.dex = Config.DEFAULT_DEX

        self.running = True

    # ---------------- MAIN LOOP ----------------

    async def run(self):
        self.logger.info("🚀 Trading loop started...")

        while self.running:
            try:
                await self.step()
                await asyncio.sleep(Config.LOOP_INTERVAL)

            except Exception as e:
                self.logger.error(f"ERROR: {e}")
                await asyncio.sleep(Config.LOOP_INTERVAL)

    # ---------------- STEP ----------------

    async def step(self):

        # 🔹 1. ЦЕНИ
        prices = await self.engine.get_multi_prices(self.symbol)

        if not prices:
            self.logger.warning("No prices available")
            return

        price = sum(prices.values()) / len(prices)

        # 🔹 2. POSITION
        position = self.state.get_position()

        # 🔹 3. PnL
        metrics = self.pnl_engine.calculate(position)

        # 🔹 4. Risk
        risk_decision = self.risk_engine.evaluate(metrics)

        # 🔹 5. Strategy
        decision = self.strategy.decide(price, position, risk_decision)

        self.logger.info(f"PRICE: {price}")
        self.logger.info(f"POSITION: {position}")
        self.logger.info(f"METRICS: {metrics}")
        self.logger.info(f"DECISION: {decision}")

        # 🔹 6. EXECUTION
        await self.execute(decision, price)

    # ---------------- EXECUTION ----------------

    async def execute(self, decision, price):

        action = decision.get("action")

        if Config.DRY_RUN:
            self.logger.info("🟡 DRY RUN: no real trade executed")

        if action == "hold":
            return

        if action == "open_long":
            self.logger.info("➡️ Opening LONG position")

            if not Config.DRY_RUN:
                await self.engine.multi_execute(
                    symbol=self.symbol,
                    side="buy",
                    size=Config.TRADE_SIZE,
                    split=Config.SPLIT_ORDERS
                )

            self.state.update_position({
                "size_usd": 100,
                "entry_price": price
            })

            self.state.add_trade({
                "type": "buy",
                "price": price
            })

        elif action == "close":
            self.logger.info("➡️ Closing position")

            if not Config.DRY_RUN:
                self.logger.warning("Real close not implemented")

            self.state.clear_position()

            self.state.add_trade({
                "type": "sell",
                "price": price
            })

        elif action == "reduce":
            self.logger.info("➡️ Reducing position")

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


if __name__ == "__main__":
    loop = TradingLoop()
    asyncio.run(loop.run())
