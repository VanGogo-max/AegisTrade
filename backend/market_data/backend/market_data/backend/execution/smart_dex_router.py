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

        # 5️⃣ Aggregate results
        aggregated = self.aggregator.aggregate(execution_results)

        aggregated["mode"] = "split"
        aggregated["child_orders"] = len(child_orders)

        return aggregated

    # ==============================================================
    # PARALLEL EXECUTION
    # ==============================================================

    async def _execute_parallel(self, child_orders: List[Dict]) -> List[Dict]:

        tasks = []

        for item in child_orders:

            exchange = item["exchange"]
            order = item["order"]

            tasks.append(
                self._execute_single_child(exchange, order)
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []

        for result in results:

            if isinstance(result, Exception):
                continue

            valid_results.append(result)

        return valid_results

    async def _execute_single_child(
        self,
        exchange: str,
        order: NormalizedOrder,
    ) -> Dict:

        connector = self.registry.get(exchange)

        start = time.time()

        result = await connector.place_order(order)

        latency = (time.time() - start) * 1000

        self.registry.report_success(exchange, latency)

        # Очаква се connector да връща:
        # {
        #   "filled_size": float,
        #   "avg_price": float,
        #   "fees": float
        # }

        return {
            "exchange": exchange,
            "filled_size": result.get("filled_size", 0.0),
            "avg_price": result.get("avg_price", 0.0),
            "fees": result.get("fees", 0.0),
            "latency_ms": latency,
        }
