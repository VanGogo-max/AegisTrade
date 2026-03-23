import asyncio
import time


class StrategyManager:
    def __init__(self, risk_engine, execution, portfolio):
        self.risk_engine = risk_engine
        self.execution = execution
        self.portfolio = portfolio

        self.positions = {}
        self.locks = {}
        self.funding_engine = None

    def set_funding_engine(self, f):
        self.funding_engine = f

    def _lock(self, s):
        if s not in self.locks:
            self.locks[s] = asyncio.Lock()
        return self.locks[s]

    async def process_signal(self, signal):
        s = signal["symbol"]

        async with self._lock(s):

            if not self.risk_engine.approve_trade(signal):
                return

            atr = signal.get("atr", 0)
            if atr == 0:
                return

            capital = self.portfolio.get_total_equity()
            risk = capital * 0.01

            stop = atr * 2
            size = risk / stop

            signal["size"] = size

            t0 = time.time()
            order = await self.execution.execute_order(signal)
            latency = time.time() - t0

            entry = order["price"]
            fee = order.get("fee", 0)

            if signal["side"] == "buy":
                sl = entry - stop
                tp = entry + stop * 2
            else:
                sl = entry + stop
                tp = entry - stop * 2

            pos = {
                "id": order["id"],
                "side": signal["side"],
                "size": size,
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "fee": fee
            }

            self.positions.setdefault(s, []).append(pos)

            print(f"[OPEN] {s} latency={latency:.3f}")

    async def process_exit(self, s, pos):
        async with self._lock(s):

            order = await self.execution.close_position(
                s, pos["size"], pos["side"]
            )

            exit_price = order["price"]
            fee = order.get("fee", 0)

            if pos["side"] == "buy":
                pnl = (exit_price - pos["entry"]) * pos["size"]
            else:
                pnl = (pos["entry"] - exit_price) * pos["size"]

            funding = 0
            if self.funding_engine:
                rate = self.funding_engine.get_rate(s)
                funding = pos["size"] * pos["entry"] * rate

            pnl -= (pos["fee"] + fee + funding)

            print(f"[CLOSE] {s} PnL={pnl:.2f}")

            self.positions[s].remove(pos)

    async def monitor_positions(self, md):
        while True:
            for s, plist in list(self.positions.items()):
                price = await md.get_price(s)

                for pos in plist[:]:
                    if pos["side"] == "buy":
                        if price <= pos["sl"] or price >= pos["tp"]:
                            await self.process_exit(s, pos)
                    else:
                        if price >= pos["sl"] or price <= pos["tp"]:
                            await self.process_exit(s, pos)

            await asyncio.sleep(1)
