# dydx_order_builder.py
"""
dYdX v4 Order Builder (FINAL)

Role:
- Deterministic builder of dYdX v4 order payloads from TradeIntent
- No signing
- No network
- No strategy / risk logic
- Pure transformation layer

Used by:
- dydx_adapter
- dydx_order_executor
"""

from typing import Dict, Any


class DydxOrderBuilder:
    def build_open(self, trade_intent: Dict[str, Any], market_id: str) -> Dict[str, Any]:
        self._validate(trade_intent, opening=True)

        return {
            "market": market_id,
            "side": "BUY" if trade_intent["side"] == "long" else "SELL",
            "type": trade_intent.get("order_type", "MARKET"),
            "sizeUsd": trade_intent["size_usd"],
            "leverage": trade_intent["leverage"],
            "price": trade_intent.get("limit_price"),
            "reduceOnly": False,
            "timeInForce": trade_intent.get("time_in_force", "IOC"),
        }

    def build_close(self, trade_intent: Dict[str, Any], market_id: str) -> Dict[str, Any]:
        self._validate(trade_intent, opening=False)

        return {
            "market": market_id,
            "side": "SELL" if trade_intent["side"] == "long" else "BUY",
            "type": "MARKET",
            "sizeUsd": trade_intent["size_usd"],
            "reduceOnly": True,
            "timeInForce": "IOC",
        }

    def _validate(self, trade_intent: Dict[str, Any], opening: bool) -> None:
        required = {"symbol", "side", "size_usd"}
        missing = required - trade_intent.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        if trade_intent["side"] not in {"long", "short"}:
            raise ValueError("side must be 'long' or 'short'")

        if trade_intent["size_usd"] <= 0:
            raise ValueError("size_usd must be positive")

        if opening and "leverage" not in trade_intent:
            raise ValueError("leverage required for opening position")
