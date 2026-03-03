cat << 'PY' > market_data_layer.py
import asyncio
import random
import time

class MarketDataLayer:
    """
    Минимална имплементация.
    Дава fake market data, за да може системата да стартира.
    """

    def __init__(self):
        self.prices = {}

    async def connect(self):
        print("MarketDataLayer connected")

    async def get_price(self, symbol: str):
        price = self.prices.get(symbol)

        if price is None:
            price = random.uniform(100, 200)

        price += random.uniform(-1, 1)
        self.prices[symbol] = price
        return price

    async def stream_price(self, symbol: str):
        while True:
            yield await self.get_price(symbol)
            await asyncio.sleep(1)
PY
