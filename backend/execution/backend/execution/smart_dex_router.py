import time
from typing import Any
from backend.exchange_connectors.exchange_registry import ExchangeRegistry
from backend.exchange_connectors.base_dex_connector import NormalizedOrder


class SmartDexRouter:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry

    # ----------------------------------
    # ROUTE ORDER (Latency-aware)
    # ----------------------------------

    async def route_order(self, order: NormalizedOrder) -> Any:

        sorted_exchanges = self.registry.get_sorted_by_latency()

        if not sorted_exchanges:
            raise RuntimeError("No healthy exchanges available")

        last_exception = None

        for name in sorted_exchanges:

            try:
                connector = self.registry.get(name)

                start = time.time()

                result = await connector.place_order(order)

                latency = (time.time() - start) * 1000
                self.registry.report_success(name, latency)

                return {
                    "exchange": name,
                    "result": result,
                    "latency_ms": latency,
                }

            except Exception as e:
                self.registry.report_error(name)
                last_exception = e

        raise RuntimeError(
            f"All exchanges failed. Last error: {last_exception}"
        )
