# backend/market_data/market_router.py

import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Type, Union, Awaitable

from .normalizer import (
    NormalizedTrade,
    NormalizedOrderBook,
    NormalizedOHLCV,
    MarketEventType,
)


MarketEvent = Union[
    NormalizedTrade,
    NormalizedOrderBook,
    NormalizedOHLCV,
]


Subscriber = Callable[[MarketEvent], Awaitable[None]]


class MarketRouter:
    """
    Central event router for normalized market data.

    Responsibilities:
    - Route events by symbol
    - Route events by event type
    - Maintain latest state cache
    - Notify async subscribers
    """

    def __init__(self) -> None:
        self._subscribers_by_symbol: Dict[str, List[Subscriber]] = defaultdict(list)
        self._subscribers_by_type: Dict[MarketEventType, List[Subscriber]] = defaultdict(list)

        self._latest_trades: Dict[str, NormalizedTrade] = {}
        self._latest_orderbooks: Dict[str, NormalizedOrderBook] = {}
        self._latest_ohlcv: Dict[str, NormalizedOHLCV] = {}

        self._lock = asyncio.Lock()

    # ==========================================================
    # SUBSCRIPTION API
    # ==========================================================

    async def subscribe_symbol(self, symbol: str, callback: Subscriber) -> None:
        async with self._lock:
            self._subscribers_by_symbol[symbol].append(callback)

    async def subscribe_event_type(
        self,
        event_type: MarketEventType,
        callback: Subscriber,
    ) -> None:
        async with self._lock:
            self._subscribers_by_type[event_type].append(callback)

    # ==========================================================
    # SNAPSHOT ACCESS
    # ==========================================================

    def get_latest_trade(self, symbol: str) -> Union[NormalizedTrade, None]:
        return self._latest_trades.get(symbol)

    def get_latest_orderbook(self, symbol: str) -> Union[NormalizedOrderBook, None]:
        return self._latest_orderbooks.get(symbol)

    def get_latest_ohlcv(self, symbol: str) -> Union[NormalizedOHLCV, None]:
        return self._latest_ohlcv.get(symbol)

    # ==========================================================
    # EVENT INGESTION
    # ==========================================================

    async def publish(self, event: MarketEvent) -> None:
        """
        Publish normalized event to:
        - internal cache
        - symbol subscribers
        - event-type subscribers
        """

        async with self._lock:
            self._update_cache(event)

            symbol_subs = list(self._subscribers_by_symbol.get(event.symbol, []))
            type_subs = list(self._subscribers_by_type.get(event.event_type, []))

        await self._dispatch(symbol_subs + type_subs, event)

    # ==========================================================
    # INTERNALS
    # ==========================================================

    def _update_cache(self, event: MarketEvent) -> None:
        if event.event_type == MarketEventType.TRADE:
            self._latest_trades[event.symbol] = event

        elif event.event_type == MarketEventType.ORDERBOOK:
            self._latest_orderbooks[event.symbol] = event

        elif event.event_type == MarketEventType.OHLCV:
            self._latest_ohlcv[event.symbol] = event

    async def _dispatch(
        self,
        subscribers: List[Subscriber],
        event: MarketEvent,
    ) -> None:
        if not subscribers:
            return

        await asyncio.gather(
            *(subscriber(event) for subscriber in subscribers),
            return_exceptions=True,
        )
