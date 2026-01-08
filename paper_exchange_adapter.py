"""
paper_exchange_adapter.py

Paper (simulated) exchange adapter.

Purpose:
- Safe testing of execution logic without real funds
- Deterministic behavior
- Full compatibility with ExchangeAdapterBase

NO real API calls
NO network
NO credentials
"""

from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from exchange_adapter_base import ExchangeAdapterBase, ExchangeAdapterError
from runtime_guard import RuntimeGuard


class PaperExchangeAdapter(ExchangeAdapterBase):
    """
    Simulated exchange adapter for paper trading.
    """

    def __init__(self, initial_balance: float = 100_000.0):
        super().__init__(exchange_name="PAPER")
        self._balance = {
            "USD": float(initial_balance)
        }
        self._orders: Dict[str, Dict[str, Any]] = {}

    def connect(self) -> None:
        """
        Simulated connection.
        """
        RuntimeGuard.assert_ready("PaperExchangeAdapter")
        self._connected = True

    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate order execution.

        Order example:
        {
            "symbol": "BTC/USD",
            "side": "buy",
            "quantity": 0.1,
            "price": 30000
        }
        """
        if not self._connected:
            raise ExchangeAdapterError("Paper exchange not connected")

        required = {"symbol", "side", "quantity", "price"}
        if not required.issubset(order):
            raise ExchangeAdapterError("Invalid order schema")

        order_id = str(uuid4())
        cost = float(order["quantity"]) * float(order["price"])

        if order["side"] == "buy":
            if self._balance["USD"] < cost:
                raise ExchangeAdapterError("Insufficient paper balance")
            self._balance["USD"] -= cost

        elif order["side"] == "sell":
            # No asset accounting (intentional simplification)
            self._balance["USD"] += cost

        else:
            raise ExchangeAdapterError("Unsupported order side")

        record = {
            "order_id": order_id,
            "exchange": self.exchange_name,
            "status": "filled",
            "filled_qty": order["quantity"],
            "price": order["price"],
            "timestamp": datetime.utcnow().isoformat()
        }

        self._orders[order_id] = record
        return record

    def cancel_order(self, order_id: str) -> None:
        """
        Cancel order (only if exists and not filled).
        """
        if order_id not in self._orders:
            raise ExchangeAdapterError("Order not found")

        # Paper orders are instant-filled; cancellation not applicable
        raise ExchangeAdapterError("Paper orders cannot be cancelled")

    def get_balance(self) -> Dict[str, Any]:
        """
        Return simulated balances.
        """
        return dict(self._balance)
