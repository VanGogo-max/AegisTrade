# backend/monitoring/system_monitor.py

import time
from typing import Dict, Any


class SystemMonitor:

    def __init__(self):

        self.start_time = time.time()

        self.exchange_status: Dict[str, Dict[str, Any]] = {}

        self.errors = []

        self.latency: Dict[str, float] = {}

    def register_exchange(self, name: str):

        self.exchange_status[name] = {
            "connected": False,
            "last_heartbeat": None
        }

    def set_connected(self, name: str, status: bool):

        if name not in self.exchange_status:
            self.register_exchange(name)

        self.exchange_status[name]["connected"] = status
        self.exchange_status[name]["last_heartbeat"] = time.time()

    def record_latency(self, exchange: str, latency: float):

        self.latency[exchange] = latency

    def record_error(self, error: str):

        self.errors.append({
            "error": error,
            "time": time.time()
        })

    def uptime(self):

        return time.time() - self.start_time

    def get_status(self):

        return {
            "uptime": self.uptime(),
            "exchanges": self.exchange_status,
            "latency": self.latency,
            "recent_errors": self.errors[-20:]
        }

    def is_exchange_alive(self, name: str, timeout: int = 30):

        if name not in self.exchange_status:
            return False

        last = self.exchange_status[name]["last_heartbeat"]

        if last is None:
            return False

        return (time.time() - last) < timeout
