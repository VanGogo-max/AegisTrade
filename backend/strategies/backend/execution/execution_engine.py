# backend/execution/execution_engine.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional
from abc import ABC, abstractmethod


# ==========================================================
# ENUMS
# ==========================================================

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


# ==========================================================
# STANDARDIZED REQUEST / RESPONSE
# ==========================================================

@dataclass(frozen=True)
class ExecutionRequest:
    exchange: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType
    price: Optional[Decimal] = None
    client_order_id: Optional[str] = None


@dataclass(frozen=True)
class ExecutionResult:
    exchange: str
    symbol: str
    order_id: str
    status: str
    filled_quantity: Decimal
    avg_price: Optional[Decimal]
    raw_response: dict


# ==========================================================
# ADAPTER INTERFACE
# ==========================================================

class BaseExecutionAdapter(ABC):
    """
    All exchange execution adapters must implement this interface.
    """

    @abstractmethod
    async def place_order(self, request: ExecutionRequest) -> ExecutionResult:
        pass

    @abstractmethod
    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
    ) -> bool:
        pass


# ==========================================================
# EXECUTION ENGINE
# ==========================================================

class ExecutionEngine:
    """
    Routes execution requests to the correct exchange adapter.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, BaseExecutionAdapter] = {}

    # ------------------------------------------------------

    def register_adapter(
        self,
        exchange: str,
        adapter: BaseExecutionAdapter,
    ) -> None:
        if exchange in self._adapters:
            raise ValueError(f"Adapter for exchange '{exchange}' already registered")

        self._adapters[exchange] = adapter

    # ------------------------------------------------------

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        adapter = self._get_adapter(request.exchange)

        if request.order_type == OrderType.LIMIT and request.price is None:
            raise ValueError("Limit order requires price")

        return await adapter.place_order(request)

    # ------------------------------------------------------

    async def cancel(
        self,
        exchange: str,
        symbol: str,
        order_id: str,
    ) -> bool:
        adapter = self._get_adapter(exchange)
        return await adapter.cancel_order(symbol, order_id)

    # ------------------------------------------------------

    def _get_adapter(self, exchange: str) -> BaseExecutionAdapter:
        adapter = self._adapters.get(exchange)

        if not adapter:
            raise ValueError(f"No execution adapter registered for '{exchange}'")

        return adapter
