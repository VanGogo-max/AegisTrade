import numpy as np


class SpotStrategy:
    def __init__(self, symbol, market_data, manager):
        self.symbol = symbol
        self.market_data = market_data
        self.manager = manager

    def compute_atr(self, candles):
        trs = []
        for i in range(1, len(candles)):
            h = candles[i]["high"]
            l = candles[i]["low"]
            pc = candles[i - 1]["close"]
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
        return np.mean(trs[-14:])

    async def run_cycle(self):
        candles = await self.market_data.get_candles(self.symbol, limit=50)
        closes = np.array([c["close"] for c in candles])

        ema_fast = closes[-10:].mean()
        ema_slow = closes[-30:].mean()

        price = closes[-1]
        atr = self.compute_atr(candles)

        if ema_fast > ema_slow and price < ema_fast:
            await self.manager.process_signal({
                "symbol": self.symbol,
                "side": "buy",
                "atr": atr,
                "strategy": "spot"
            })
