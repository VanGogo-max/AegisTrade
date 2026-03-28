import asyncio

from backend.execution.engine import ExecutionEngine
from backend.analytics.pnl_engine import PnLEngine
from backend.risk.risk_engine import RiskEngine
from backend.strategy.strategy_engine import StrategyEngine


class TradingLoop:
    """
    Основен runtime loop (ботът работи 24/7)
    """

    def __init__(self):
        self.engine = ExecutionEngine()
        self.pnl_engine = PnLEngine()
        self.risk_engine = RiskEngine()
        self.strategy = StrategyEngine()

        self.symbol = "ETH"
        self.dex = "gmx"

        self.running = True

    # ---------------- MAIN LOOP ----------------

    async def run(self):
        print("🚀 Trading loop started...")

        while self.running:
            try:
                await self.step()
                await asyncio.sleep(5)  # интервал (секунди)

            except Exception as e:
                print("ERROR:", e)
                await asyncio.sleep(5)

    # ---------------- ONE STEP ----------------

    async def step(self):

        # 🔹 1. Вземи цена (multi-DEX)
        prices = await self.engine.get_multi_prices(self.symbol)

        if not prices:
            print("No prices available")
            return

        # взимаме средна цена (опростено)
        price = sum(prices.values()) / len(prices)

        # 🔹 2. Вземи позиция
        position = await self.engine.get_position(self.dex, self.symbol)

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

        # 🔹 6. EXECUTION (dry-run или реално)
        await self.execute(decision)

    # ---------------- EXECUTION ----------------

    async def execute(self, decision):

        action = decision.get("action")

        # 🔹 HOLD
        if action == "hold":
            return

        # 🔹 OPEN LONG
        if action == "open_long":
            print("➡️ Opening LONG position")

            result = await self.engine.multi_execute(
                symbol=self.symbol,
                side="buy",
                size=0.01,
                split=False
            )

            print("EXEC RESULT:", result)

        # 🔹 CLOSE
        elif action == "close":
            print("➡️ Closing position")

            # ⚠️ за GMX трябва decreasePosition (още не е имплементирано)
            print("Close logic not implemented yet")

        # 🔹 REDUCE
        elif action == "reduce":
            print("➡️ Reducing position")
            print("Reduce logic not implemented yet")

    # ---------------- STOP ----------------

    def stop(self):
        self.running = False


# ---------------- RUN ----------------

if __name__ == "__main__":
    loop = TradingLoop()
    asyncio.run(loop.run())
