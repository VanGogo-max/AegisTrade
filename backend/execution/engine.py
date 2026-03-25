from typing import Dict, Any
from backend.execution.router import DexRouter


class ExecutionEngine:
    def __init__(self):
        self.router = DexRouter()

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

    async def cancel_order(self, dex: str, order_id: str):
        adapter = self.router.get_adapter(dex)
        return await adapter.cancel_order(order_id)

    async def get_position(self, dex: str, symbol: str):
        adapter = self.router.get_adapter(dex)
        return await adapter.get_position(symbol)
