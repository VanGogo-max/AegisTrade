# kcex_order_builder.py
"""
Responsibility:
- Build normalized order objects for KCEX
- Validate parameters before sending to adapter / signer
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class KCEXOrder:
    symbol: str
    side: str        # BUY / SELL
    quantity: float
    price: Optional[float]
    leverage: int
    order_type: str  # MARKET / LIMIT


class KCEXOrderBuilder:
    def build_market_order(
        self, symbol: str, side: str, quantity: float, leverage: int
    ) -> KCEXOrder:
        self._validate_side(side)
        self._validate_quantity(quantity)
        self._validate_leverage(leverage)

        return KCEXOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=None,
            leverage=leverage,
            order_type="MARKET",
        )

    def build_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        leverage: int,
    ) -> KCEXOrder:
        self._validate_side(side)
        self._validate_quantity(quantity)
        self._validate_price(price)
        self._validate_leverage(leverage)

        return KCEXOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            leverage=leverage,
            order_type="LIMIT",
        )

    def _validate_side(self, side: str):
        if side not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")

    def _validate_quantity(self, qty: float):
        if qty <= 0:
            raise ValueError("Quantity must be positive")

    def _validate_price(self, price: float):
        if price <= 0:
            raise ValueError("Price must be positive")

    def _validate_leverage(self, lev: int):
        if lev < 1 or lev > 100:
            raise ValueError("Leverage must be between 1 and 100")
