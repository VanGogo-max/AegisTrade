# hyperliquid_adapter.py
"""
Responsibility:
- Concrete DEX adapter for Hyperliquid
- Simulated execution for development and testing

Does NOT depend on:
- bots
- strategies
- Web3 / RPC / private keys
"""

import uuid
import random
from typing import Dict

from dex_adapter import DexAdapter


class HyperliquidAdapter(DexAdapter):
    def __init__(self):
        super().__init__(name="Hyperliquid")
        self._connected = True
        self._open_orders: Dict[str, dict] = {}

    def is_connected(self) -> bool:
        return self._connected

    def get_price(self, symbol: str) -> float:
        """
        Simulated market price.
        In real implementation this will query Hyperliquid API.
        """
        base_price = 30000.0
        noise = random.uniform(-50.0, 50.0)
        return round(base_price + noise, 2)

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float | None = None,
    ) -> str:
        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        order_id = str(uuid.uuid4())
        execution_price = price if price is not None else self.get_price(symbol)

        self._open_orders[order_id] = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": execution_price,
            "status": "FILLED",
        }

        return order_id

    def cancel_order(self, order_id: str) -> bool:
        if order_id not in self._open_orders:
            return False

        self._open_orders[order_id]["status"] = "CANCELED"
        return True
