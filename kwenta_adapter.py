# kwenta_adapter.py
"""
Kwenta DEX Adapter (FINAL)

Responsibility:
- Concrete exchange adapter for Kwenta (Synthetix Perps)
- Provides unified interface for:
    * price fetch
    * order placement
    * order cancel
    * connectivity status
- Simulation-only (no RPC, no private keys)

Conforms to:
- DexAdapter interface
"""

import uuid
import random
from typing import Dict

from dex_adapter import DexAdapter


class KwentaAdapter(DexAdapter):
    def __init__(self):
        super().__init__(name="Kwenta")
        self._connected = True
        self._open_orders: Dict[str, dict] = {}

    def is_connected(self) -> bool:
        return self._connected

    def get_price(self, symbol: str) -> float:
        """
        Simulated oracle price (Synthetix-style).
        """
        base_price = 2500.0
        noise = random.uniform(-20.0, 20.0)
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
            "exchange": "Kwenta",
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
