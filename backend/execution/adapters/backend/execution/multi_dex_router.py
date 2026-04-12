"""
AegisTrade — Multi-DEX Router
"""
from __future__ import annotations
import asyncio
from typing import Dict, List, Optional

from backend.config.config import PREFERRED_DEX_ORDER, DRY_RUN
from backend.execution.adapters.all_adapters import (
    BaseDEXAdapter, OrderResult,
    HyperliquidAdapter, DydxAdapter, GmxAdapter,
    ApexAdapter, KwentaAdapter, VertexAdapter,
)
from backend.utils.logger import get_logger

log = get_logger(__name__)

ADAPTER_MAP: Dict[str, type] = {
    "hyperliquid": HyperliquidAdapter,
    "dydx": DydxAdapter,
    "gmx": GmxAdapter,
    "apex": ApexAdapter,
    "kwenta": KwentaAdapter,
    "vertex": VertexAdapter,
}


class MultiDEXRouter:
    def __init__(self, dry_run: bool = DRY_RUN) -> None:
        self.dry_run = dry_run
        self._adapters: Dict[str, BaseDEXAdapter] = {}

    async def start(self) -> None:
        for name in PREFERRED_DEX_ORDER:
            cls = ADAPTER_MAP[name]
            adapter: BaseDEXAdapter = cls(dry_run=self.dry_run)
            await adapter.start()
            self._adapters[name] = adapter
        log.info(
            "MultiDEXRouter started (%d adapters, dry_run=%s)",
            len(self._adapters), self.dry_run
        )

    async def stop(self) -> None:
        for adapter in self._adapters.values():
            await adapter.stop()

    async def _select_best_dex(
        self, symbol: str, qty: float, price: float
    ) -> List[str]:
        scores = []
        for name in PREFERRED_DEX_ORDER:
            adapter = self._adapters.get(name)
            if not adapter:
                continue
            try:
                fee = await adapter.get_fee_estimate(symbol, qty)
                liq = await adapter.check_liquidity(symbol, qty, price)
                if liq:
                    scores.append((fee, name))
            except Exception as e:
                log.debug("Score error for %s: %s", name, e)
        scores.sort(key=lambda x: x[0])
        return [name for _, name in scores]

    async def route_order(
        self, symbol: str, side: str, qty: float, price: float
    ) -> OrderResult:
        ordered = await self._select_best_dex(symbol, qty, price)
        if not ordered:
            ordered = list(PREFERRED_DEX_ORDER)

        for dex_name in ordered:
            adapter = self._adapters.get(dex_name)
            if not adapter:
                continue
            log.info("Routing %s %s %s to %s", side, qty, symbol, dex_name)
            result = await adapter.place_order(symbol, side, qty, price)
            if result.success:
                log.info(
                    "Filled on %s: price=%.4f qty=%.6f fee=%.4f",
                    dex_name, result.filled_price, result.filled_qty, result.fee
                )
                return result
            log.warning("Failed on %s: %s — trying next", dex_name, result.error)

        return OrderResult(False, "none", error="All DEX adapters failed")

    async def split_order(
        self, symbol: str, side: str, qty: float, price: float, parts: int = 2
    ) -> List[OrderResult]:
        split_qty = round(qty / parts, 8)
        ordered = await self._select_best_dex(symbol, split_qty, price)
        results = []
        for dex_name in ordered[:parts]:
            adapter = self._adapters.get(dex_name)
            if not adapter:
                continue
            result = await adapter.place_order(symbol, side, split_qty, price)
            results.append(result)
        return results

    async def cancel(self, dex: str, order_id: str) -> bool:
        adapter = self._adapters.get(dex)
        if adapter:
            return await adapter.cancel_order(order_id)
        return False
