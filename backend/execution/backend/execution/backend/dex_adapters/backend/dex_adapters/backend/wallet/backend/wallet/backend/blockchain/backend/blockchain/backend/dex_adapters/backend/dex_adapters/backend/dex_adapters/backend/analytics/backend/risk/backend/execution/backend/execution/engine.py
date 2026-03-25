from typing import Dict, Any

from backend.execution.router import DexRouter
from backend.execution.multi_dex_router import MultiDexRouter


class ExecutionEngine:
    def __init__(self):
        self.router = DexRouter()

        # Multi-DEX layer
        self.multi_router = MultiDexRouter(self.router.adapters)

    # ---------------- SINGLE DEX ----------------

    async def place_order(
        self,
        dex: str,
        symbol: str,
        side: str,
        size: float,
        price: float = None,
        order_type: str = "market",
    ) -> Dict[str, Any]:

        adapter = self.router.get_adapter(dex)

        return await adapter.place_order(
            symbol=symbol,
            side=side,
            size=size,
            price=price,
            order_type=order_type,
        )

    async def get_position(self, dex: str, symbol: str):
        adapter = self.router.get_adapter(dex)
        return await adapter.get_position(symbol)

    async def cancel_order(self, dex: str, order_id: str):
        adapter = self.router.get_adapter(dex)
        return await adapter.cancel_order(order_id)

    # ---------------- MULTI DEX ----------------

    async def multi_execute(
        self,
        symbol: str,
        side: str,
        size: float,
        split: bool = False
    ):
        return await self.multi_router.execute(
            symbol=symbol,
            side=side,
            size=size,
            split=split
        )

    async def get_multi_prices(self, symbol: str):
        return await self.multi_router.get_prices(symbol)
