# backend/execution/order_executor.py

import asyncio
from typing import Dict, Any, Optional


class OrderExecutor:
    """
    Responsible for sending orders to the selected exchange connector
    and handling execution lifecycle.
    """

    def __init__(self, exchange_registry):

        self.exchange_registry = exchange_registry

        self.active_orders: Dict[str, Dict] = {}

    async def execute(
        self,
        exchange: str,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "market",
        price: Optional[float] = None,
        reduce_only: bool = False
    ) -> Dict[str, Any]:

        connector = self.exchange_registry.get(exchange)

        if connector is None:
            raise Exception(f"Exchange not registered: {exchange}")

        order = {
            "symbol": symbol,
            "side": side,
            "size": size,
            "type": order_type,
            "price": price,
            "reduce_only": reduce_only
        }

        result = await connector.place_order(order)

        if result and "order_id" in result:
            self.active_orders[result["order_id"]] = {
                "exchange": exchange,
                "symbol": symbol,
                "side": side,
                "size": size
            }

        return result

    async def cancel(
        self,
        exchange: str,
        order_id: str
    ):

        connector = self.exchange_registry.get(exchange)

        if connector is None:
            raise Exception("Exchange not found")

        result = await connector.cancel_order(order_id)

        if order_id in self.active_orders:
            del self.active_orders[order_id]

        return result

    async def close_position(
        self,
        exchange: str,
        symbol: str,
        side: str,
        size: float
    ):

        close_side = "sell" if side == "buy" else "buy"

        return await self.execute(
            exchange=exchange,
            symbol=symbol,
            side=close_side,
            size=size,
            order_type="market",
            reduce_only=True
        )

    def get_active_orders(self):

        return self.active_orders

    async def emergency_close_all(self):

        tasks = []

        for order_id, order in self.active_orders.items():

            tasks.append(
                self.close_position(
                    exchange=order["exchange"],
                    symbol=order["symbol"],
                    side=order["side"],
                    size=order["size"]
                )
            )

        if tasks:
            await asyncio.gather(*tasks)

        self.active_orders.clear()
