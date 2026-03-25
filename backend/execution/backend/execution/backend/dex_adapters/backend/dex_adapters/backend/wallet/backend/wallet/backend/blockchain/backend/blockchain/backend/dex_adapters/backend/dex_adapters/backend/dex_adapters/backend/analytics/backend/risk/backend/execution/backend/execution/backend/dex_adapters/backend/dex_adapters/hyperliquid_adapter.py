from backend.dex_adapters.base_adapter import BaseDexAdapter


class HyperliquidAdapter(BaseDexAdapter):

    async def place_order(self, symbol, side, size, price=None, order_type="market"):
        return {
            "dex": "hyperliquid",
            "status": "submitted",
        }

    async def cancel_order(self, order_id):
        return {"status": "cancelled"}

    async def get_position(self, symbol):
        return {"size": 0}

    async def get_price(self, symbol: str):
        # mock (реално тук ще е API call)
        return 3000
