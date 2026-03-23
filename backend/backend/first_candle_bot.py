class FirstCandleBot:
    def __init__(self, symbol, market_data, manager):
        self.symbol = symbol
        self.market_data = market_data
        self.manager = manager

    async def run_cycle(self):
        candles = await self.market_data.get_candles(self.symbol, limit=10)

        first = candles[0]
        last = candles[-1]

        atr = (first["high"] - first["low"])

        if last["close"] > first["high"]:
            await self.manager.process_signal({
                "symbol": self.symbol,
                "side": "buy",
                "atr": atr,
                "strategy": "first_candle"
            })

        elif last["close"] < first["low"]:
            await self.manager.process_signal({
                "symbol": self.symbol,
                "side": "sell",
                "atr": atr,
                "strategy": "first_candle"
            })
