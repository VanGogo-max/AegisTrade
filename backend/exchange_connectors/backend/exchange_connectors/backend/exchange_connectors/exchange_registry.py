import asyncio
import time
from typing import Dict, List
from .base_dex_connector import BaseDexConnector


class ExchangeStatus:
    def __init__(self):
        self.healthy: bool = True
        self.last_check: float = 0
        self.latency_ms: float = 0
        self.error_count: int = 0


class ExchangeRegistry:

    def __init__(self):
        self._exchanges: Dict[str, BaseDexConnector] = {}
        self._status: Dict[str, ExchangeStatus] = {}

        self.max_errors = 3
        self.healthcheck_interval = 15  # seconds

    # ----------------------------------
    # REGISTER
    # ----------------------------------

    def register(self, name: str, connector: BaseDexConnector):

        if name in self._exchanges:
            raise ValueError(f"Exchange '{name}' already registered")

        self._exchanges[name] = connector
        self._status[name] = ExchangeStatus()

    # ----------------------------------
    # GET (only healthy)
    # ----------------------------------

    def get(self, name: str) -> BaseDexConnector:

        if name not in self._exchanges:
            raise ValueError(f"Exchange '{name}' not found")

        if not self._status[name].healthy:
            raise RuntimeError(f"Exchange '{name}' is unhealthy")

        return self._exchanges[name]

    # ----------------------------------
    # LIST HEALTHY
    # ----------------------------------

    def healthy_exchanges(self) -> List[str]:
        return [
            name for name, status in self._status.items()
            if status.healthy
        ]

    # ----------------------------------
    # ERROR TRACKING
    # ----------------------------------

    def report_error(self, name: str):

        status = self._status[name]
        status.error_count += 1

        if status.error_count >= self.max_errors:
            status.healthy = False

    def report_success(self, name: str, latency_ms: float):

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
                    # минимален ping тест
                    await connector.fetch_positions()

                    latency = (time.time() - start) * 1000
                    self.report_success(name, latency)

                except Exception:
                    self.report_error(name)

            await asyncio.sleep(self.healthcheck_interval)
