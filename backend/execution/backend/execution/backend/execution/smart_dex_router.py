import time
from typing import Any, Dict

from backend.exchange_connectors.exchange_registry import ExchangeRegistry
from backend.exchange_connectors.base_dex_connector import NormalizedOrder
from backend.execution.exchange_scoring_engine import ExchangeScoringEngine


class SmartDexRouter:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry
        self.scoring_engine = ExchangeScoringEngine(registry)

    # ------------------------------------------------
    # MAIN ROUTING METHOD (Unified Scoring)
    # ------------------------------------------------

    async def route_order(
        self,
        order: NormalizedOrder,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
    ) -> Any:

        ranked_exchanges = await self.scoring_engine.rank_exchanges(
            symbol=order.symbol,
            spreads=spreads,
            funding_rates=funding_rates,
        )

        if not ranked_exchanges:
            raise RuntimeError("No healthy exchanges available")

        last_exception = None

        for name in ranked_exchanges:

            try:
                connector = self.registry.get(name)

                start_time = time.time()

                result = await connector.place_order(order)

                latency_ms = (time.time() - start_time) * 1000

                # success reporting
                self.registry.report_success(name, latency_ms)

                return {
                    "exchange": name,
                    "result": result,
                    "latency_ms": latency_ms,
                    "ranking_order": ranked_exchanges,
                }

            except Exception as e:

                # error reporting
                self.registry.report_error(name)
                last_exception = e

        raise RuntimeError(
            f"All exchanges failed. Last error: {last_exception}"
        )

    # ------------------------------------------------
    # OPTIONAL: SIMPLE LATENCY-ONLY FALLBACK
    # ------------------------------------------------

    async def route_latency_only(self, order: NormalizedOrder) -> Any:

        sorted_exchanges = self.registry.get_sorted_by_latency()

        if not sorted_exchanges:
            raise RuntimeError("No healthy exchanges available")

        last_exception = None

        for name in sorted_exchanges:

            try:
                connector = self.registry.get(name)

                start_time = time.time()
                result = await connector.place_order(order)
                latency_ms = (time.time() - start_time) * 1000

                self.registry.report_success(name, latency_ms)

                return {
                    "exchange": name,
                    "result": result,
                    "latency_ms": latency_ms,
                }

            except Exception as e:
                self.registry.report_error(name)
                last_exception = e

        raise RuntimeError(
            f"All exchanges failed. Last error: {last_exception}"
        )
