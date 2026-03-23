class FirstCandleBot:
    def __init__(self, s, md, m):
        self.s = s
        self.md = md
        self.m = m

    async def run_cycle(self):
        c = await self.md.get_candles(self.s, 10)

        first = c[0]
        last = c[-1]

        atr = first["high"] - first["low"]

        if last["close"] > first["high"]:
            await self.m.process_signal({
                "symbol": self.s,
                "side": "buy",
                "atr": atr,
                "strategy": "first_candle"
            })
