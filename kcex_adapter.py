# kcex_adapter.py
"""
Responsibility:
- Concrete DEX adapter for KCEX
- Simulated execution layer (no real API, no keys)
"""

import uuid
import random
from typing import Dict

from dex_adapter import DexAdapter


class KCEXAdapter(DexAdapter):
    def __init__(self):
        super().__init__(name="KCEX")
        self._connected = True
        self._open_orders: Dict[str, dict] = {}

    def is_connected(self) -> bool:
        return self._connected

    def get_price(self, symbol: str) -> float:
        base_price = 30000.0
        noise = random.uniform(-80.0, 80.0)
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
        execution_price = price if price else self.get_price(symbol)

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
