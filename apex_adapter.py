# apex_adapter.py
"""
Apex Protocol Adapter (FINAL)

Responsibility:
- Concrete DEX adapter for Apex Protocol (Perpetuals)
- Translate generic TradeIntent into Apex-compatible order payloads
- Paper-trading simulation mode (no RPC, no signing)

References:
- Apex Docs: https://docs.apex.exchange
"""

from typing import Dict, Any
import uuid
import random


class ApexAdapterError(Exception):
    pass


class ApexAdapter:
    def __init__(self, network: str = "arbitrum"):
        self.network = network
        self._connected = True
        self._orders: Dict[str, Dict[str, Any]] = {}

    def is_connected(self) -> bool:
        return self._connected

    def get_price(self, symbol: str) -> float:
        base = 30000.0
        noise = random.uniform(-120, 120)
        return round(base + noise, 2)

    def build_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        required = {"symbol", "side", "quantity"}
        missing = required - trade_intent.keys()
        if missing:
            raise ApexAdapterError(f"Missing required fields: {missing}")

        return {
            "exchange": "Apex",
            "network": self.network,
            "symbol": trade_intent["symbol"],
            "side": trade_intent["side"],
            "quantity": float(trade_intent["quantity"]),
            "price": trade_intent.get("price") or self.get_price(trade_intent["symbol"]),
            "order_type": trade_intent.get("order_type", "MARKET"),
            "reduce_only": trade_intent.get("reduce_only", False),
        }

    def simulate_execution(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())

        execution = {
            "order_id": order_id,
            "exchange": "Apex",
            "symbol": order_payload["symbol"],
            "side": order_payload["side"],
            "filled_price": order_payload["price"],
            "quantity": order_payload["quantity"],
            "status": "FILLED",
        }

        self._orders[order_id] = execution
        return execution

    def get_order(self, order_id: str) -> Dict[str, Any] | None:
        return self._orders.get(order_id)
