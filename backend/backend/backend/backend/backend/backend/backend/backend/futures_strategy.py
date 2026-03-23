import numpy as np

class FuturesStrategy:
    def __init__(self, s, md, m):
        self.s = s
        self.md = md
        self.m = m

    def atr(self, c):
        return np.mean([x["high"] - x["low"] for x in c][-14:])

    async def run_cycle(self):
        c = await self.md.get_candles(self.s, 50)
        closes = np.array([x["close"] for x in c])

        if closes[-10:].mean() < closes[-30:].mean():
            await self.m.process_signal({
                "symbol": self.s,
                "side": "sell",
                "atr": self.atr(c),
                "strategy": "futures"
            })
