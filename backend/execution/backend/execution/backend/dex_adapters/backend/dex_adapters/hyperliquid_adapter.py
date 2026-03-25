from backend.dex_adapters.base_adapter import BaseDexAdapter


class HyperliquidAdapter(BaseDexAdapter):

    async def place_order(self, symbol, side, size, price, order_type):
        # TODO: интеграция с Hyperliquid API / SDK
        return {
            "status": "submitted",
            "dex": "hyperliquid",
            "symbol": symbol,
        }

    async def cancel_order(self, order_id):
        return {"status": "cancelled", "order_id": order_id}

    async def get_position(self, symbol):
        return {"symbol": symbol, "size": 0}
