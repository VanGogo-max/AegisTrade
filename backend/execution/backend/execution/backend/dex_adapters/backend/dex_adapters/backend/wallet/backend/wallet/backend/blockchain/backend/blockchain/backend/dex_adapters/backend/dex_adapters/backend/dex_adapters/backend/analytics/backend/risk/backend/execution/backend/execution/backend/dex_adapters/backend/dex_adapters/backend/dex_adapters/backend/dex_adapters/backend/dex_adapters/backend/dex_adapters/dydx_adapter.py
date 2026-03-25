from backend.dex_adapters.base_adapter import BaseDexAdapter


class DYDXAdapter(BaseDexAdapter):

    async def place_order(self, symbol, side, size, price=None, order_type="market"):
        return {"dex": "dydx", "status": "submitted"}

    async def cancel_order(self, order_id):
        return {"status": "cancelled"}

    async def get_position(self, symbol):
        return {"size": 0}

    async def get_price(self, symbol: str):
        return 3000
