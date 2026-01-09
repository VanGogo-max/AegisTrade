# trade_preflight_validator.py
"""
trade_preflight_validator.py — FINAL

Preflight validation layer for trade intents.

Purpose:
- Validate a TradeIntent against exchange capabilities BEFORE execution
- Fail fast on unsupported order types, margin models, leverage, etc.
- Prevent invalid trades from reaching adapters or signers

Design guarantees:
- NO execution
- NO network calls
- NO signing
- Deterministic validation only

Inputs:
- trade_intent (dict)
- exchange_capabilities (ExchangeCapabilities)

Outputs:
- raises TradePreflightError on invalid intent
- returns None if valid
"""

from typing import Dict, Any

from exchange_capabilities import ExchangeCapabilities


class TradePreflightError(Exception):
    """Raised when a trade intent is incompatible with exchange capabilities."""


class TradePreflightValidator:
    @staticmethod
    def validate(
        trade_intent: Dict[str, Any],
        capabilities: ExchangeCapabilities,
    ) -> None:
        """
        Validate trade intent against exchange capabilities.
        """

        # =========================
        # Required fields
        # =========================
        required_fields = {
            "exchange",
            "market",
            "side",
            "order_type",
            "size_usd",
        }

        missing = required_fields - trade_intent.keys()
        if missing:
            raise TradePreflightError(
                f"TradeIntent missing required fields: {missing}"
            )

        # =========================
        # Order type support
        # =========================
        order_type = trade_intent["order_type"]
        if order_type not in capabilities.order_types:
            raise TradePreflightError(
                f"Order type '{order_type}' not supported by {capabilities.exchange}"
            )

        # =========================
        # Reduce-only
        # =========================
        if trade_intent.get("reduce_only", False):
            if not capabilities.reduce_only:
                raise TradePreflightError(
                    f"Reduce-only orders not supported by {capabilities.exchange}"
                )

        # =========================
        # Post-only
        # =========================
        if trade_intent.get("post_only", False):
            if not capabilities.post_only:
                raise TradePreflightError(
                    f"Post-only orders not supported by {capabilities.exchange}"
                )

        # =========================
        # Leverage validation
        # =========================
        leverage = trade_intent.get("leverage")
        if leverage is not None:
            if leverage <= 0:
                raise TradePreflightError("Leverage must be positive")

            if leverage > capabilities.max_leverage:
                raise TradePreflightError(
                    f"Leverage {leverage} exceeds max "
                    f"{capabilities.max_leverage} for {capabilities.exchange}"
                )

        # =========================
        # Margin model
        # =========================
        margin_mode = trade_intent.get("margin_mode")
        if margin_mode == "isolated" and not capabilities.isolated_margin:
            raise TradePreflightError(
                f"Isolated margin not supported by {capabilities.exchange}"
            )

        if margin_mode == "cross" and not capabilities.cross_margin:
            raise TradePreflightError(
                f"Cross margin not supported by {capabilities.exchange}"
            )

        # =========================
        # Market type
        # =========================
        market_type = trade_intent.get("market_type", "perpetual")

        if market_type == "perpetual" and not capabilities.perpetuals:
            raise TradePreflightError(
                f"Perpetual markets not supported by {capabilities.exchange}"
            )

        if market_type == "spot" and not capabilities.spot:
            raise TradePreflightError(
                f"Spot markets not supported by {capabilities.exchange}"
            )

        # =========================
        # Size validation
        # =========================
        if trade_intent["size_usd"] <= 0:
            raise TradePreflightError("size_usd must be positive")

        # =========================
        # Side validation
        # =========================
        if trade_intent["side"] not in {"long", "short", "buy", "sell"}:
            raise TradePreflightError(
                f"Invalid side '{trade_intent['side']}'"
            )

        # If we reach here → intent is valid
        return None
