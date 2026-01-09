"""
exchange_router.py — FINAL

Central exchange routing layer.

Purpose:
- Route TradeIntent execution to the correct exchange adapter
- Enforce explicit exchange allowlist
- Prevent silent misrouting
- Support multi-exchange execution (DEX-first)

Design guarantees:
- No execution logic
- No strategy logic
- No network calls
- Deterministic routing only
"""

from typing import Dict, Any

from exchange_adapter_base import ExchangeAdapterBase


class ExchangeRoutingError(Exception):
    pass


class ExchangeRouter:
    """
    Deterministic router for exchange adapters.
    """

    def __init__(self, adapters: Dict[str, ExchangeAdapterBase]):
        """
        Args:
            adapters: mapping {exchange_name: adapter_instance}
        """
        if not adapters:
            raise ExchangeRoutingError("No exchange adapters provided")

        self._adapters = adapters

    def get_adapter(self, exchange: str) -> ExchangeAdapterBase:
        """
        Return adapter for given exchange.

        Raises:
            ExchangeRoutingError if exchange is unsupported
        """
        if not exchange:
            raise ExchangeRoutingError("Exchange name is required")

        adapter = self._adapters.get(exchange.lower())
        if not adapter:
            raise ExchangeRoutingError(
                f"Unsupported exchange '{exchange}'. "
                f"Allowed: {list(self._adapters.keys())}"
            )

        return adapter

    def route(self, trade_intent: Dict[str, Any]) -> ExchangeAdapterBase:
        """
        Resolve adapter based on TradeIntent.

        Expects:
            trade_intent['exchange']

        Returns:
            ExchangeAdapterBase
        """
        exchange = trade_intent.get("exchange")
        if not exchange:
            raise ExchangeRoutingError("TradeIntent missing 'exchange' field")

        return self.get_adapter(exchange)

    def supported_exchanges(self) -> list[str]:
        """
        List supported exchange identifiers.
        """
        return list(self._adapters.keys())
