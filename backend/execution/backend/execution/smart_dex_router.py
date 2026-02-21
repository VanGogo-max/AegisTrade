import asyncio
import time
from typing import Dict, List

from backend.exchange_connectors.exchange_registry import ExchangeRegistry
from backend.exchange_connectors.base_dex_connector import NormalizedOrder

from backend.execution.exchange_scoring_engine import ExchangeScoringEngine
from backend.execution.liquidity_analyzer import LiquidityAnalyzer
from backend.execution.order_splitter import OrderSplitter
from backend.execution.execution_aggregator import ExecutionAggregator
from backend.execution.execution_monitor import ExecutionMonitor


class SmartDexRouter:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry

        self.scoring_engine = ExchangeScoringEngine(registry)
        self.liquidity_analyzer = LiquidityAnalyzer(registry)
        self.order_splitter = OrderSplitter()
        self.aggregator = ExecutionAggregator()
        self.monitor = ExecutionMonitor()

    # ==============================================================
    # SINGLE EXECUTION (с adaptive feedback)
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

        for name in ranked:

            try:
                connector = self.registry.get(name)

                start = time.time()
                result = await connector.place_order(order)
                latency = (time.time() - start) * 1000

                self.registry.report_success(name, latency)

                # 🔥 Calculate slippage if avg_price exists
                avg_price = result.get("avg_price", 0.0)
                expected_price = spreads.get(name, avg_price)
                slippage = abs((avg_price - expected_price) / expected_price) if expected_price else 0

                # 🔥 Feed adaptive engine
                self.scoring_engine.update_performance(
                    exchange=name,
                    slippage=slippage,
                    latency_ms=latency,
                    success=True,
                )

                return {
                    "mode": "single",
                    "exchange": name,
                    "execution": result,
                }

            except Exception:
                self.registry.report_error(name)

                self.scoring_engine.update_performance(
                    exchange=name,
                    slippage=0.05,
                    latency_ms=1000,
                    success=False,
                )

        raise RuntimeError("All exchanges failed")

    # ==============================================================
    # SPLIT EXECUTION (feedback per exchange)
    # ==============================================================

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

        avg_price = result.get("avg_price", 0.0)
        slippage = 0.0  # ще бъде изчислено от monitor при aggregate

        # 🔥 Adaptive feedback
        self.scoring_engine.update_performance(
            exchange=exchange,
            slippage=slippage,
            latency_ms=latency,
            success=True,
        )

        return {
            "exchange": exchange,
            "filled_size": result.get("filled_size", 0.0),
            "avg_price": avg_price,
            "fees": result.get("fees", 0.0),
            "latency_ms": latency,
        }
