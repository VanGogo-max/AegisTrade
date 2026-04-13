"""
AegisTrade — Multi-DEX Router
"""
from __future__ import annotations
from backend.execution.adapters.all_adapters import (
    HyperliquidAdapter, DydxAdapter, GmxAdapter,
    ApexAdapter, KwentaAdapter, VertexAdapter,
    OrderResult,
)
from backend.utils.logger import get_logger

log = get_logger(__name__)


class MultiDEXRouter:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
        self._adapters = {
            "hyperliquid": HyperliquidAdapter(dry_run),
            "dydx":        DydxAdapter(dry_run),
            "gmx":         GmxAdapter(dry_run),
            "apex":        ApexAdapter(dry_run),
            "kwenta":      KwentaAdapter(dry_run),
            "vertex":      VertexAdapter(dry_run),
        }

    async def start(self) -> None:
        for a in self._adapters.values():
            await a.start()

    async def stop(self) -> None:
        for a in self._adapters.values():
            await a.stop()

    async def place_order(
        self, dex: str, symbol: str, side: str, qty: float, price: float
    ) -> OrderResult:
        adapter = self._adapters.get(dex)
        if not adapter:
            return OrderResult(False, dex, error=f"Unknown DEX: {dex}")
        return await adapter.place_order(symbol, side, qty, price)

    async def cancel_order(self, dex: str, order_id: str) -> bool:
        adapter = self._adapters.get(dex)
        if not adapter:
            return False
        return await adapter.cancel_order(order_id)

    async def best_dex(
        self, symbol: str, qty: float, price: float
    ) -> str:
        """Returns the DEX with lowest fee estimate."""
        best, best_fee = "hyperliquid", float("inf")
        for name, adapter in self._adapters.items():
            try:
                fee = await adapter.get_fee_estimate(symbol, qty)
                liquid = await adapter.check_liquidity(symbol, qty, price)
                if liquid and fee < best_fee:
                    best, best_fee = name, fee
            except Exception:
                pass
        return best
