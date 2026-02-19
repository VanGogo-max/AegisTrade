import asyncio
import time
from typing import Any, Dict, List

from backend.exchange_connectors.exchange_registry import ExchangeRegistry
from backend.exchange_connectors.base_dex_connector import NormalizedOrder

from backend.execution.exchange_scoring_engine import ExchangeScoringEngine
from backend.execution.liquidity_analyzer import LiquidityAnalyzer
from backend.execution.order_splitter import OrderSplitter
from backend.execution.execution_aggregator import ExecutionAggregator


class SmartDexRouter:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry

        self.scoring_engine = ExchangeScoringEngine(registry)
        self.liquidity_analyzer = LiquidityAnalyzer(registry)
        self.order_splitter = OrderSplitter()
        self.aggregator = ExecutionAggregator()

    # ==============================================================
    # MAIN ENTRY
    # ==============================================================

    async def route_order(
        self,
        order: NormalizedOrder,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
        use_split: bool = True,
    ) -> Dict:

        if not use_split:
            return await self._route_single(order, spreads, funding_rates)

        return await self._route_split(order, spreads, funding_rates)

    # ==============================================================
    # SINGLE EXECUTION (Backward Compatible)
    # ==============================================================

    async def _route_single(
        self,
        order: NormalizedOrder,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
    ) -> Dict:

        ranked = await self.scoring_engine.rank_exchanges(
            symbol=order.symbol,
            spreads=spreads,
            funding_rates=funding_rates,
        )

        last_exception = None

        for name in ranked:

            try:
                connector = self.registry.get(name)

                start = time.time()
                result = await connector.place_order(order)
                latency = (time.time() - start) * 1000

                self.registry.report_success(name, latency)

                return {
                    "mode": "single",
                    "exchange": name,
                    "execution": result,
                    "latency_ms": latency,
                }

            except Exception as e:
                self.registry.report_error(name)
                last_exception = e

        raise RuntimeError(f"All exchanges failed: {last_exception}")

    # ==============================================================
    # SPLIT EXECUTION 2.0
    # ==============================================================

    async def _route_split(
        self,
        order: NormalizedOrder,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
    ) -> Dict:

        # 1️⃣ Analyze liquidity
        liquidity_map = await self.liquidity_analyzer.analyze(
            symbol=order.symbol,
            side=order.side,
            total_size=order.size,
        )

        if not liquidity_map:
            raise RuntimeError("No liquidity available")

        # 2️⃣ Compute optimal split
        allocations = self.liquidity_analyzer.compute_optimal_split(
            liquidity_map,
            total_size=order.size,
        )

        # 3️⃣ Generate child orders
        child_orders = self.order_splitter.split(order, allocations)

        if not self.order_splitter.validate_split(order, child_orders):
            raise RuntimeError("Split validation failed")

        # 4️⃣ Execute in parallel
        execution_results = await self._execute_parallel(child_orders)
