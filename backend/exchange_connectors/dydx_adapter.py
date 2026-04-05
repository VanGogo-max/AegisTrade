# dydx_adapter.py
"""
dYdX v4 Exchange Adapter (FINAL)

Role:
- Concrete adapter for dYdX v4 (orderbook perp DEX)
- Translate abstract TradeIntent into dYdX order payloads
- No signing (handled by dydx_signer)
- No network (handled by dydx_tx_sender)
- No strategy / risk logic
"""

from typing import Dict, Any
import time


class DydxAdapterError(Exception):
    pass


class DydxAdapter:
    def __init__(self, market_map: Dict[str, str]):
        """
        Args:
            market_map: mapping from internal symbol to dYdX market id
                        e.g. {"BTC-USD": "BTC-USD-PERP"}
        """
        if not market_map:
            raise DydxAdapterError("market_map is required")
        self.market_map = market_map

    # =========================
    # Public API
    # =========================

    def open_position(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(trade_intent, opening=True)

        return {
            "exchange": "DYDX_V4",
            "action": "OPEN_POSITION",
            "payload": self._build_open_order(trade_intent),
            "created_at": int(time.time()),
        }

    def close_position(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(trade_intent, opening=False)

        return {
            "exchange": "DYDX_V4",
            "action": "CLOSE_POSITION",
            "payload": self._build_close_order(trade_intent),
            "created_at": int(time.time()),
        }

    # =========================
    # Validation
    # =========================

    def _validate(self, trade_intent: Dict[str, Any], opening: bool) -> None:
        required = {"symbol", "side", "size_usd"}
        missing = required - trade_intent.keys()
        if missing:
            raise DydxAdapterError(f"Missing required fields: {missing}")

        if trade_intent["symbol"] not in self.market_map:
            raise DydxAdapterError(f"Unsupported market: {trade_intent['symbol']}")

        if trade_intent["side"] not in {"long", "short"}:
            raise DydxAdapterError("side must be 'long' or 'short'")

        if trade_intent["size_usd"] <= 0:
            raise DydxAdapterError("size_usd must be positive")

        if opening and "leverage" not in trade_intent:
            raise DydxAdapterError("leverage required for opening position")

    # =========================
    # Payload Builders
    # =========================

    def _build_open_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "market": self.market_map[trade_intent["symbol"]],
            "side": "BUY" if trade_intent["side"] == "long" else "SELL",
            "type": trade_intent.get("order_type", "MARKET"),
            "sizeUsd": trade_intent["size_usd"],
            "leverage": trade_intent["leverage"],
            "price": trade_intent.get("limit_price"),
            "reduceOnly": False,
        }

    def _build_close_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "market": self.market_map[trade_intent["symbol"]],
            "side": "SELL" if trade_intent["side"] == "long" else "BUY",
            "type": "MARKET",
            "sizeUsd": trade_intent["size_usd"],
            "reduceOnly": True,
        }
