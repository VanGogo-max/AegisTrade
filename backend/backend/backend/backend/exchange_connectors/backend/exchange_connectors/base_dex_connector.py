# backend/exchange_connectors/base_dex_connector.py

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class NormalizedOrder:
    symbol: str
    side: str
    size: float
    price: Optional[float]
    order_type: str
    reduce_only: bool = False


@dataclass
class NormalizedPosition:
    symbol: str
    size: float
    entry_price: float
    unrealized_pnl: float


class BaseDexConnector(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def place_order(self, order: NormalizedOrder):
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str):
        pass

    @abstractmethod
    async def fetch_positions(self) -> List[NormalizedPosition]:
        pass

    @abstractmethod
    async def fetch_funding_rate(self, symbol: str) -> float:
        pass

    @abstractmethod
    async def subscribe_orderbook(self, symbol: str):
        pass

    @abstractmethod
    async def close(self):
        pass
