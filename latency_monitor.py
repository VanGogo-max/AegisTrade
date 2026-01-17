# latency_monitor.py
import time
import threading
from collections import deque
from typing import Deque, Dict


class LatencyMonitor:
    """
    Monitors execution and network latency in real time.
    Feeds data into MetricsCollector and HealthChecker.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.lock = threading.Lock()
        self.samples: Deque[float] = deque(maxlen=window_size)

    def record(self, start_ts: float, end_ts: float):
        latency_ms = (end_ts - start_ts) * 1000.0
        with self.lock:
            self.samples.append(latency_ms)

    def average(self) -> float:
        with self.lock:
            if not self.samples:
                return 0.0
            return sum(self.samples) / len(self.samples)

    def max_latency(self) -> float:
        with self.lock:
            if not self.samples:
                return 0.0
            return max(self.samples)

    def min_latency(self) -> float:
        with self.lock:
            if not self.samples:
                return 0.0
            return min(self.samples)

    def snapshot(self) -> Dict[str, float]:
        with self.lock:
            if not self.samples:
                return {"avg": 0.0, "max": 0.0, "min": 0.0}
            return {
                "avg": sum(self.samples) / len(self.samples),
                "max": max(self.samples),
                "min": min(self.samples),
            }

    def is_critical(self, threshold_ms: float) -> bool:
        """
        Returns True if average latency exceeds critical threshold.
        """
        return self.average() > threshold_ms
