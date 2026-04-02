import asyncio
from decimal import Decimal

from backend.execution.execution_engine import ExecutionEngine, ExecutionRequest, OrderSide, OrderType
from backend.risk.risk_engine import RiskEngine
from backend.state.state_manager import StateManager
from backend.feeds.price_feed import PriceFeed
from backend.config.config import Config


class TradingLoop:

    def __init__(self):
        self.execution_engine = ExecutionEngine()
        self.risk_engine = RiskEngine()
        self.price_feed = PriceFeed()
        self.state = StateManager()
        self.symbol = Config.SYMBOL
        self.running = True

    async def run(self):
        print("🚀 Trading loop started...")
        while self.running:
            try:
                await self.step()
                await asyncio.sleep(Config.LOOP_INTERVAL)
            except Exception as e:
                print(f"❌ ERROR: {e}")
                await asyncio.sleep(Config.LOOP_INTERVAL)

    async def step(self):
        price = await self.price_feed.get_price(self.symbol)
        if not price:
            print("⚠️ No price available")
            return

        position = self.state.get_position()
        decision = self._decide(price, position)

        print(f"💰 PRICE: {price} | POSITION: {position} | DECISION: {decision}")
        await self._execute(decision, price)

    def _decide(self, price: float, position: dict) -> dict:
        size = position.get("size_usd", 0)
        entry = position.get("entry_price", 0)

        if size == 0:
            return {"action": "open_long"}

        if size > 0 and entry > 0:
            change = (price - entry) / entry
            if change <= -0.02 or change >= 0.03:
                return {"action": "close"}

        return {"action": "hold"}

    async def _execute(self, decision: dict, price: float):
        action = decision.get("action")

        if Config.DRY_RUN:
            print(f"🟡 DRY RUN — action: {action}")

        if action == "hold":
            return

        if action == "open_long":
            if not Config.DRY_RUN:
                request = ExecutionRequest(
                    exchange=Config.DEFAULT_DEX,
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    quantity=Decimal(str(Config.TRADE_SIZE)),
                    order_type=OrderType.MARKET,
                )
                await self.execution_engine.execute(request)

            self.state.update_position({"size_usd": Config.TRADE_SIZE, "entry_price": price})
            self.state.add_trade({"type": "buy", "price": price})

        elif action == "close":
            self.state.clear_position()
            self.state.add_trade({"type": "sell", "price": price})

    def stop(self):
        self.running = False


if __name__ == "__main__":
    loop = TradingLoop()
    asyncio.run(loop.run())
