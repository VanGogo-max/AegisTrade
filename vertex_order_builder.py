# vertex_order_builder.py
"""
Vertex Order Builder (FINAL)

Responsibility:
- Convert normalized TradeIntent into Vertex order structure
- No signing
- No sending
- No RPC
"""

from typing import Dict, Any


class VertexOrderBuildError(Exception):
    pass


class VertexOrderBuilder:
    def build(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        required = {"symbol", "side", "quantity"}
        missing = required - trade_intent.keys()
        if missing:
            raise VertexOrderBuildError(f"Missing required fields: {missing}")

        if trade_intent["side"] not in ("long", "short", "buy", "sell"):
            raise VertexOrderBuildError("Invalid side")

        order = {
            "symbol": trade_intent["symbol"],
            "side": trade_intent["side"],
            "quantity": float(trade_intent["quantity"]),
            "order_type": trade_intent.get("order_type", "MARKET"),
            "price": trade_intent.get("price"),
            "reduce_only": trade_intent.get("reduce_only", False),
            "time_in_force": trade_intent.get("time_in_force", "GTC"),
        }

        return order
