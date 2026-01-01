# dex_adapter.py
"""
Responsibility:
- Abstract interface for Decentralized Exchanges (DEX)
- Unified contract for order execution and price retrieval

Does NOT depend on:
- bots
- strategies
- risk management
- Web3 libraries
"""

from abc import ABC, abstractmethod
from typing import Optional


class DexAdapter(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """
        Returns the latest market price for a symbol.
        """
        raise NotImplementedError

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> str:
        """
        Places an order on the DEX.
        Returns order_id.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancels an existing order.
        """
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Checks adapter readiness.
        """
        raise NotImplementedError
