"""
gmx_order_builder.py — FINAL

GMX Order Builder.

Purpose:
- Convert validated TradeIntent into GMX-compatible order payload
- Prepare deterministic calldata inputs (NO signing, NO sending)
- Act as the single translation layer between core system and GMX protocol

Design guarantees:
- No network calls
- No signing
- No execution
- No strategy logic
- Deterministic & testable
"""

from typing import Dict, Any


class GMXOrderBuilderError(Exception):
    pass


class GMXOrderBuilder:
    """
    Deterministic builder for GMX orders.
    """

    @staticmethod
    def build(trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build GMX order payload from TradeIntent.

        Required TradeIntent fields:
            - symbol
            - side ("BUY" / "SELL")
            - quantity
            - price
            - account
            - market

        Returns:
            Dict[str, Any] — GMX order payload
        """

        required_fields = [
            "symbol",
            "side",
            "quantity",
            "price",
            "account",
            "market",
        ]

        missing = [f for f in required_fields if f not in trade_intent]
        if missing:
            raise GMXOrderBuilderError(
                f"TradeIntent missing required fields: {missing}"
            )

        side = trade_intent["side"].upper()
        if side not in ("BUY", "SELL"):
            raise GMXOrderBuilderError(f"Invalid side: {side}")

        quantity = float(trade_intent["quantity"])
        price = float(trade_intent["price"])

        if quantity <= 0:
            raise GMXOrderBuilderError("Quantity must be positive")

        if price <= 0:
            raise GMXOrderBuilderError("Price must be positive")

        is_long = side == "BUY"

        # GMX-style order payload (protocol-agnostic, ABI-ready)
        order_payload = {
            "account": trade_intent["account"],
            "market": trade_intent["market"],
            "symbol": trade_intent["symbol"],
            "is_long": is_long,
            "size_delta_usd": quantity * price,
            "acceptable_price": price,
            "execution_fee": trade_intent.get("execution_fee", 0),
            "callback_gas_limit": trade_intent.get("callback_gas_limit", 0),
            "metadata": {
                "source": "auto_trading_system",
                "intent_id": trade_intent.get("intent_id"),
            },
        }

        return order_payload
