# hyperliquid_order_builder.py
"""
Hyperliquid Order Builder (FINAL)

Role:
- Build canonical Hyperliquid order payloads from TradeIntent
- No signing
- No network
- No strategy logic
- Deterministic transformation only

Used by:
- hyperliquid_adapter
- hyperliquid_order_executor
"""

from typing import Dict, Any


class HyperliquidOrderBuilder:
    def build_open(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(trade_intent, opening=True)

        return {
            "type": "order",
            "symbol": trade_intent["symbol"],
            "isBuy": trade_intent["side"] == "long",
            "sizeUsd": trade_intent["size_usd"],
            "leverage": trade_intent["leverage"],
            "orderType": trade_intent.get("order_type", "market"),
            "limitPrice": trade_intent.get("limit_price"),
            "reduceOnly": False,
        }

    def build_close(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(trade_intent, opening=False)

        return {
            "type": "order",
            "symbol": trade_intent["symbol"],
            "isBuy": trade_intent["side"] != "long",
            "sizeUsd": trade_intent["size_usd"],
            "orderType": "market",
            "reduceOnly": True,
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
