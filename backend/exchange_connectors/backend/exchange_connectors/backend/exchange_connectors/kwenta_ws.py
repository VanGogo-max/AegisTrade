import asyncio
import json
from typing import Any, Dict, List, Callable

from web3 import Web3
from web3.middleware import geth_poa_middleware

from backend.exchange_connectors.base_connector import BaseDEXConnector
from backend.config import settings  # Твоят config с RPC URLs

class KwentaWSConnector(BaseDEXConnector):
    """
    Kwenta connector (Optimism mainnet) за perps / smart-margin.
    Слуша smart contract събития и/или subgraph.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        super().__init__("kwenta")
        self.loop = loop or asyncio.get_event_loop()
        self.w3 = Web3(Web3.WebsocketProvider(settings.KWENTA_RPC_WS))
        # Ако е PoA chain (Optimism/Arbitrum)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.event_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    async def connect(self):
        """Стартира слушането на smart contract events"""
        self.loop.create_task(self._listen_position_events())
        self.loop.create_task(self._listen_trade_events())

    async def _listen_position_events(self):
        """Слуша Kwenta PositionModified и PositionLiquidated events"""
        contract = self.w3.eth.contract(address=settings.KWENTA_SMART_MARGIN, abi=settings.KWENTA_SMART_MARGIN_ABI)
        event_filter = contract.events.PositionModified.createFilter(fromBlock='latest')
        while True:
            for event in event_filter.get_new_entries():
                normalized = self._normalize_position_event(event)
                await self._dispatch_event("position", normalized)
            await asyncio.sleep(1)  # rate limit / polling

    async def _listen_trade_events(self):
        """Слуша DelayedOrderSubmitted / TradeExecuted events"""
        contract = self.w3.eth.contract(address=settings.KWENTA_PERPS, abi=settings.KWENTA_PERPS_ABI)
        event_filter = contract.events.TradeExecuted.createFilter(fromBlock='latest')
        while True:
            for event in event_filter.get_new_entries():
                normalized = self._normalize_trade_event(event)
                await self._dispatch_event("trade", normalized)
            await asyncio.sleep(1)

    async def _dispatch_event(self, event_type: str, data: Dict[str, Any]):
        """Връща нормализирано event dict към Multi-DEX hub"""
        self.loop.create_task(self._broadcast(event_type, data))

    async def _broadcast(self, event_type: str, data: Dict[str, Any]):
        """Hook към UnifiedMarketDataRouter / WS Hub"""
        for handler in self.event_handlers.get(event_type, []):
            handler(data)

    def register_handler(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Позволява на app.py да се абонира за Kwenta events"""
        self.event_handlers.setdefault(event_type, []).append(callback)

    def _normalize_position_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "exchange": "kwenta",
            "type": "position",
            "timestamp": self.w3.eth.get_block(event.blockNumber)['timestamp'],
            "symbol": event.args.asset,
            "side": "long" if event.args.size > 0 else "short",
            "size": abs(event.args.size),
            "margin": event.args.margin,
            "liquidationPrice": event.args.liquidationPrice,
        }

    def _normalize_trade_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "exchange": "kwenta",
            "type": "trade",
            "timestamp": self.w3.eth.get_block(event.blockNumber)['timestamp'],
            "symbol": event.args.asset,
            "side": "buy" if event.args.isBuy else "sell",
            "size": event.args.size,
            "price": event.args.price,
            "margin": event.args.margin,
        }
