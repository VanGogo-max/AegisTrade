import asyncio


class FundingEngine:
    def __init__(self, clients):
        self.clients = clients
        self.rates = {}

    def _client(self):
        return list(self.clients.values())[0]

    async def update(self, symbols):
        c = self._client()

        for s in symbols:
            try:
                data = await c.fetch_funding_rate(s)
                self.rates[s] = data["fundingRate"]
            except:
                self.rates[s] = 0

    def get_rate(self, s):
        return self.rates.get(s, 0)

    async def run(self, symbols):
        while True:
            await self.update(symbols)
            await asyncio.sleep(300)
