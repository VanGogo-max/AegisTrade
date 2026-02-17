from .base_dex_connector import BaseDexConnector

class DydxConnector(BaseDexConnector):

    async def connect(self):
        pass

    async def place_order(self, order):
        pass

    async def cancel_order(self, order_id):
        pass

    async def fetch_positions(self):
        pass

    async def fetch_funding_rate(self, symbol):
        pass

    async def subscribe_orderbook(self, symbol):
        pass

    async def close(self):
        pass
