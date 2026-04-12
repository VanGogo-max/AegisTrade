"""
AegisTrade — DEX Adapters
"""
from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import aiohttp

from backend.config.config import MAX_RETRIES, RETRY_DELAY_S
from backend.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class OrderResult:
    success: bool
    dex: str
    order_id: str = ""
    filled_price: float = 0.0
    filled_qty: float = 0.0
    fee: float = 0.0
    error: str = ""
    simulated: bool = False


class BaseDEXAdapter(ABC):
    name: str = "base"

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

    async def stop(self) -> None:
        if self._session:
            await self._session.close()

    async def _post_with_retry(self, url: str, payload: dict) -> Optional[dict]:
        for attempt in range(MAX_RETRIES):
            try:
                async with self._session.post(url, json=payload) as r:
                    if r.status == 200:
                        return await r.json()
                    log.warning("%s HTTP %d attempt %d", self.name, r.status, attempt + 1)
            except Exception as e:
                log.warning("%s error (attempt %d): %s", self.name, attempt + 1, e)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY_S)
        return None

    def _sim_result(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        return OrderResult(
            success=True,
            dex=self.name,
            order_id=f"SIM-{self.name[:3].upper()}-{symbol}-{side}",
            filled_price=price,
            filled_qty=qty,
            fee=price * qty * 0.001,
            simulated=True,
        )

    @abstractmethod
    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult: ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool: ...

    @abstractmethod
    async def get_fee_estimate(self, symbol: str, qty: float) -> float: ...

    @abstractmethod
    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool: ...


class HyperliquidAdapter(BaseDEXAdapter):
    name = "hyperliquid"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("Hyperliquid live order requires wallet signing — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.0002

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return True


class DydxAdapter(BaseDEXAdapter):
    name = "dydx"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("dYdX live order requires STARK signing — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.0005

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return True


class GmxAdapter(BaseDEXAdapter):
    name = "gmx"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("GMX live order requires Web3 signing — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.001

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return price * qty < 5000


class ApexAdapter(BaseDEXAdapter):
    name = "apex"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("Apex live order requires STARK signing — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.0005

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return True


class KwentaAdapter(BaseDEXAdapter):
    name = "kwenta"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("Kwenta live order requires Optimism wallet — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.001

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return price * qty < 2000


class VertexAdapter(BaseDEXAdapter):
    name = "vertex"

    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        if self.dry_run:
            return self._sim_result(symbol, side, qty, price)
        log.warning("Vertex live order requires EIP-712 signing — not implemented")
        return OrderResult(False, self.name, error="Live signing not configured")

    async def cancel_order(self, order_id: str) -> bool:
        return self.dry_run

    async def get_fee_estimate(self, symbol: str, qty: float) -> float:
        return 0.0002

    async def check_liquidity(self, symbol: str, qty: float, price: float) -> bool:
        return True
