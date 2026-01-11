# kwenta_order_builder.py
"""
Kwenta Order Builder (FINAL)

Responsibility:
- Translates abstract TradeIntent into Kwenta-specific order payload
- No signing, no sending, no RPC
- Pure deterministic builder

References:
- Kwenta Perps (Synthetix V3): https://docs.kwenta.io
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class KwentaMarketConfig:
    symbol: str
    base_asset: str
    quote_asset: str
    max_leverage: float


KWENTA_MARKETS = {
    "ETH-USD": KwentaMarketConfig("ETH-USD", "ETH", "USD", 25.0),
    "BTC-USD": KwentaMarketConfig("BTC-USD", "BTC", "USD", 20.0),
}


class KwentaOrderBuilder:
    """
    Builds Kwenta-compatible order instructions from trade intents.
    """

    @staticmethod
    def build_open_position(intent: Dict[str, Any]) -> Dict[str, Any]:
        KwentaOrderBuilder._validate_intent(intent, opening=True)

        market = KWENTA_MARKETS[intent["symbol"]]

        return {
            "protocol": "KWENTA",
            "action": "OPEN_POSITION",
            "market": market.symbol,
            "side": intent["side"],
            "size_usd": intent["size_usd"],
            "leverage": intent["leverage"],
            "reduce_only": False,
            "acceptable_price": intent.get("acceptable_price"),
        }

    @staticmethod
    def build_close_position(intent: Dict[str, Any]) -> Dict[str, Any]:
        KwentaOrderBuilder._validate_intent(intent, opening=False)

        market = KWENTA_MARKETS[intent["symbol"]]

        return {
            "protocol": "KWENTA",
            "action": "CLOSE_POSITION",
            "market": market.symbol,
            "side": intent["side"],
            "size_usd": intent["size_usd"],
            "reduce_only": True,
            "acceptable_price": intent.get("acceptable_price"),
        }

    @staticmethod
    def _validate_intent(intent: Dict[str, Any], opening: bool) -> None:
        required = {"symbol", "side", "size_usd"}
        missing = required - intent.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        if intent["symbol"] not in KWENTA_MARKETS:
            raise ValueError(f"Unsupported Kwenta market: {intent['symbol']}")

        if intent["side"] not in {"long", "short"}:
            raise ValueError("side must be 'long' or 'short'")

        if intent["size_usd"] <= 0:
            raise ValueError("size_usd must be positive")

        if opening:
            if "leverage" not in intent:
                raise ValueError("leverage is required when opening a position")

            max_lev = KWENTA_MARKETS[intent["symbol"]].max_leverage
            if intent["leverage"] > max_lev:
                raise ValueError(f"Leverage exceeds max allowed: {max_lev}")
