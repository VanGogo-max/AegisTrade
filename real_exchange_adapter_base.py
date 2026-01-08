"""
real_exchange_adapter_base.py

Abstract base for real exchange adapters.

Purpose:
- Standardized interface for any real crypto exchange
- Safe integration without hardcoding keys or logic
- Separation between execution engine and exchange-specific API
- Enterprise-grade contract for production

Constraints:
- No API keys embedded
- No actual execution (implementation in child classes)
- Standard library only
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from runtime_guard import RuntimeGuard


class RealExchangeAdapterError(Exception):
    """Raised for adapter-specific failures."""


class RealExchangeAdapterBase(ABC):
    """
    Abstract base class for all real exchange adapters.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self._connected = False

    def connect(self) -> None:
        """
        Establish connection/session with the real exchange.
        Must be idempotent.
        """
        RuntimeGuard.assert_ready("RealExchangeAdapter")
        self._connected = True

    def shutdown(self) -> None:
        """
        Gracefully close connection/session.
        """
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a real order on the exchange.

        Order keys required:
        - symbol
        - side
        - quantity
        - type (limit/market/etc.)
        Returns:
        - order_id
        - status
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an existing order on the exchange.
        """
        raise NotImplementedError

    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """
        Retrieve account balances.
        """
        raise NotImplementedError

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of an existing order.
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch market data for a symbol (price, depth, volume, etc.).
        """
        raise NotImplementedError
