# exchange_registry.py
"""
exchange_registry.py — FINAL

Central exchange registry and bootstrap layer.

Purpose:
- Register enabled exchanges
- Bind adapters to declared capabilities
- Validate configuration consistency at startup
- Provide a ready ExchangeRouter instance

Design guarantees:
- NO execution logic
- NO network calls
- NO signing
- Fail-fast on misconfiguration
"""

from typing import Dict, List

from exchange_adapter_base import ExchangeAdapterBase
from exchange_router import ExchangeRouter
from exchange_capabilities import (
    EXCHANGE_CAPABILITIES,
    ExchangeCapabilities,
)


class ExchangeRegistryError(Exception):
    pass


class ExchangeRegistry:
    """
    Registry for enabled exchanges and their adapters.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, ExchangeAdapterBase] = {}
        self._capabilities: Dict[str, ExchangeCapabilities] = {}

    # =========================
    # Registration
    # =========================

    def register_exchange(
        self,
        exchange: str,
        adapter: ExchangeAdapterBase,
    ) -> None:
        key = exchange.lower()

        if key in self._adapters:
            raise ExchangeRegistryError(
                f"Exchange '{exchange}' already registered"
            )

        if key not in EXCHANGE_CAPABILITIES:
            raise ExchangeRegistryError(
                f"No capabilities declared for exchange '{exchange}'"
            )

        self._adapters[key] = adapter
        self._capabilities[key] = EXCHANGE_CAPABILITIES[key]

    # =========================
    # Validation
    # =========================

    def validate(self) -> None:
        if not self._adapters:
            raise ExchangeRegistryError("No exchanges registered")

        for key in self._adapters.keys():
            if key not in self._capabilities:
                raise ExchangeRegistryError(
                    f"Missing capabilities for exchange '{key}'"
                )

    # =========================
    # Accessors
    # =========================

    def get_router(self) -> ExchangeRouter:
        self.validate()
        return ExchangeRouter(adapters=self._adapters)

    def list_exchanges(self) -> List[str]:
        return list(self._adapters.keys())

    def get_capabilities(self, exchange: str) -> ExchangeCapabilities:
        key = exchange.lower()
        if key not in self._capabilities:
            raise ExchangeRegistryError(
                f"Unknown exchange '{exchange}'"
            )
        return self._capabilities[key]
