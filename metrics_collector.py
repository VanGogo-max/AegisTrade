import time
import threading
from typing import Dict


class MetricsCollector:
    """
    Thread-safe collector for runtime system metrics.
    """

    def __init__(self) -> None:
        self._start_time = time.time()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._timings: Dict[str, float] = {}
        self._lock = threading.Lock()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def record_timing(self, name: str, duration: float) -> None:
        with self._lock:
            self._timings[name] = duration

    def uptime_seconds(self) -> float:
        return time.time() - self._start_time

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._timings.clear()
            self._start_time = time.time()

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {
                "uptime_seconds": self.uptime_seconds(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timings": dict(self._timings),
            }
