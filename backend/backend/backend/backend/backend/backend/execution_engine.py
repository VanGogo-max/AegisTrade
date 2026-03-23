class ExecutionEngine:
    def __init__(self, clients):
        self.clients = clients

    def _client(self):
        return list(self.clients.values())[0]

    async def execute_order(self, signal):
        c = self._client()

        ticker = await c.fetch_ticker(signal["symbol"])
        price = ticker["last"]

        fee = price * signal["size"] * 0.001

        return {
            "id": "order_" + str(price),
            "price": price,
            "fee": fee
        }

    async def close_position(self, symbol, size, side):
        c = self._client()

        ticker = await c.fetch_ticker(symbol)
        price = ticker["last"]

        fee = price * size * 0.001

        return {
            "id": "close_" + str(price),
            "price": price,
            "fee": fee
        }
