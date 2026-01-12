# vertex_adapter.py
"""
Vertex Protocol Adapter (FINAL)

Responsibility:
- Concrete DEX adapter for Vertex Protocol
- Translate generic trade intents into Vertex-compatible execution calls
- Provide unified interface for router and execution pipeline

No strategy logic.
No signing.
No private keys.
No direct RPC (delegated to sender layer).

References:
- Vertex Docs: https://docs.vertexprotocol.com
"""

from typing import Dict, Any
import uuid
import random


class VertexAdapterError(Exception):
    pass


class VertexAdapter:
    def __init__(self, network: str = "arbitrum"):
        self.network = network
        self._connected = True
        self._orders: Dict[str, Dict[str, Any]] = {}

    def is_connected(self) -> bool:
        return self._connected

    def get_price(self, symbol: str) -> float:
        """
        Simulated price feed (paper mode).
        """
        base = 30000.0
        noise = random.uniform(-100, 100)
        return round(base + noise, 2)

    def build_order(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Vertex-compatible order payload from generic trade intent.
        """
        required = {"symbol", "side", "quantity"}
        missing = required - intent.keys()
        if missing:
            raise VertexAdapterError(f"Missing fields: {missing}")

        return {
            "exchange": "Vertex",
            "network": self.network,
            "symbol": intent["symbol"],
            "side": intent["side"],
            "quantity": intent["quantity"],
            "price": intent.get("price") or self.get_price(intent["symbol"]),
            "type": intent.get("type", "MARKET"),
        }

    def simulate_execution(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Paper-trade execution simulator.
        """
        order_id = str(uuid.uuid4())

        execution = {
            "order_id": order_id,
            "status": "FILLED",
            "filled_price": order_payload["price"],
            "quantity": order_payload["quantity"],
            "side": order_payload["side"],
            "symbol": order_payload["symbol"],
            "exchange": "Vertex",
        }

        self._orders[order_id] = execution
        return execution

    def get_order(self, order_id: str) -> Dict[str, Any] | None:
        return self._orders.get(order_id)
