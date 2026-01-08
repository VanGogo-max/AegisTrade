# exchange_adapter_base.py
"""
ExchangeAdapterBase.

Purpose:
- Define a strict, minimal contract for exchange integrations
- No exchange-specific logic
- No credentials handling
- No business logic

This is an interface layer only.
Standard library only.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from runtime_guard import RuntimeGuard


class ExchangeAdapterError(Exception):
    """Raised on exchange adapter failures."""


class ExchangeAdapterBase(ABC):
    """
    Abstract base class for all exchange adapters.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self._connected = False

    def connect(self) -> None:
        """
        Establish connection/session with the exchange.
        Must be idempotent.
        """
        RuntimeGuard.assert_ready("ExchangeAdapter")
        self._connected = True

    def shutdown(self) -> None:
        """
        Gracefully close any open connections.
        """
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order on the exchange.

        Expected order keys (minimum):
        - symbol
        - side
        - quantity
        - type

        Returns:
        - order_id
        - status
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an existing order.
        """
        raise NotImplementedError

    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """
        Fetch account balances.
        """
        raise NotImplementedError
