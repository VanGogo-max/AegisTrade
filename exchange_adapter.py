"""
exchange_adapter.py

Defines a unified interface for exchange interaction.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from types import OrderSide


class ExchangeAdapter(ABC):
    """
    Abstract adapter that standardizes interaction
    with any exchange (real, paper, or backtest).
    """

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """
        Returns the latest market price for a symbol.
        """
        raise NotImplementedError

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Places an order on the exchange.
        """
        raise NotImplementedError

    @abstractmethod
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Closes an open position for a symbol.
        """
        raise NotImplementedError
