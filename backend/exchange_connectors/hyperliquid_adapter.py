# hyperliquid_adapter.py
"""
Hyperliquid Exchange Adapter (FINAL)

Role:
- Reference exchange adapter for Hyperliquid
- Translate abstract TradeIntent into Hyperliquid order payloads
- No strategy logic
- No risk logic
- No signing (handled by hyperliquid_signer)
- No network calls (handled by hyperliquid_tx_sender)

Sources:
- Hyperliquid API: https://docs.hyperliquid.xyz
- Hyperliquid GitHub: https://github.com/hyperliquid-dex
"""

from typing import Dict, Any
import time


class HyperliquidAdapterError(Exception):
    pass


class HyperliquidAdapter:
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    # =========================
    # Public Execution API
    # =========================

    def open_position(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_trade_intent(trade_intent, opening=True)

        return {
            "exchange": "HYPERLIQUID",
            "action": "OPEN_POSITION",
            "payload": self._build_open_order(trade_intent),
            "created_at": int(time.time()),
        }

    def close_position(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_trade_intent(trade_intent, opening=False)

        return {
            "exchange": "HYPERLIQUID",
            "action": "CLOSE_POSITION",
            "payload": self._build_close_order(trade_intent),
            "created_at": int(time.time()),
        }

    # =========================
    # Validation
    # =========================

    def _validate_trade_intent(self, trade_intent: Dict[str, Any], opening: bool) -> None:
        required = {"symbol", "side", "size_usd"}
        missing = required - trade_intent.keys()
        if missing:
            raise HyperliquidAdapterError(f"Missing required fields: {missing}")

        if trade_intent["side"] not in {"long", "short"}:
            raise HyperliquidAdapterError("side must be 'long' or 'short'")

        if trade_intent["size_usd"] <= 0:
            raise HyperliquidAdapterError("size_usd must be positive")

        if opening and "leverage" not in trade_intent:
            raise HyperliquidAdapterError("leverage required for opening position")

    # =========================
    # Payload Builders
    # =========================

    def _build_open_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
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

    def _build_close_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "order",
            "symbol": trade_intent["symbol"],
            "isBuy": trade_intent["side"] != "long",
            "sizeUsd": trade_intent["size_usd"],
            "orderType": "market",
            "reduceOnly": True,
        }
