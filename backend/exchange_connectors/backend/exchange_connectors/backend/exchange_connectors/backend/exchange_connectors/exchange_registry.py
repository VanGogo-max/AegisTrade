import asyncio
import time
from typing import Dict, List, Tuple
from .base_dex_connector import BaseDexConnector


class ExchangeStatus:
    def __init__(self):
        self.healthy: bool = True
        self.last_check: float = 0.0
        self.latency_ms: float = 0.0
        self.error_count: int = 0


class ExchangeRegistry:

    def __init__(self):
        self._exchanges: Dict[str, BaseDexConnector] = {}
        self._status: Dict[str, ExchangeStatus] = {}

        self.max_errors = 3
        self.healthcheck_interval = 15  # seconds

    # ----------------------------------
    # REGISTER / UNREGISTER
    # ----------------------------------

    def register(self, name: str, connector: BaseDexConnector):

        if name in self._exchanges:
            raise ValueError(f"Exchange '{name}' already registered")

        self._exchanges[name] = connector
        self._status[name] = ExchangeStatus()

    def unregister(self, name: str):

        if name not in self._exchanges:
            raise ValueError(f"Exchange '{name}' not found")

        del self._exchanges[name]
        del self._status[name]

    # ----------------------------------
    # GET
    # ----------------------------------

    def get(self, name: str) -> BaseDexConnector:

        if name not in self._exchanges:
            raise ValueError(f"Exchange '{name}' not found")

        if not self._status[name].healthy:
            raise RuntimeError(f"Exchange '{name}' is unhealthy")

        return self._exchanges[name]

    # ----------------------------------
    # LISTING
    # ----------------------------------

    def list_all(self) -> List[str]:
        return list(self._exchanges.keys())

    def healthy_exchanges(self) -> List[str]:
        return [
            name for name, status in self._status.items()
            if status.healthy
        ]

    def get_sorted_by_latency(self) -> List[str]:

        healthy: List[Tuple[str, float]] = []

        for name, status in self._status.items():
            if status.healthy:
                latency = status.latency_ms if status.latency_ms > 0 else 999999
                healthy.append((name, latency))

        healthy.sort(key=lambda x: x[1])

        return [name for name, _ in healthy]

    # ----------------------------------
    # ERROR / SUCCESS REPORTING
    # ----------------------------------

    def report_error(self, name: str):

        if name not in self._status:
            return

        status = self._status[name]
        status.error_count += 1

        if status.error_count >= self.max_errors:
            status.healthy = False

    def report_success(self, name: str, latency_ms: float):

        if name not in self._status:
            return

        status = self._status[name]
        status.error_count = 0
        status.healthy = True
        status.latency_ms = latency_ms
        status.last_check = time.time()

    # ----------------------------------
    # HEALTH CHECK LOOP
    # ----------------------------------

    async def health_check_loop(self):

        while True:

            for name, connector in self._exchanges.items():

                start = time.time()

                try:
                    # lightweight call – трябва да е евтин endpoint
                    await connector.fetch_positions()

                    latency = (time.time() - start) * 1000
                    self.report_success(name, latency)

                except Exception:
                    self.report_error(name)

            await asyncio.sleep(self.healthcheck_interval)
