# metrics_collector.py
import threading
import time
from typing import Dict, Any


class MetricsCollector:
    """
    Collects and aggregates real-time system and trading metrics.
    Feeds data to health_checker and global_risk_state_manager.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.metrics: Dict[str, Any] = {
            "pnl": 0.0,
            "open_positions": 0,
            "latency_ms": 0.0,
            "slippage": 0.0,
            "error_rate": 0.0,
            "last_update": time.time()
        }

    def update_metric(self, key: str, value: Any):
        with self.lock:
            self.metrics[key] = value
            self.metrics["last_update"] = time.time()

    def increment(self, key: str, delta: float = 1.0):
        with self.lock:
            if key not in self.metrics:
                self.metrics[key] = 0.0
            self.metrics[key] += delta
            self.metrics["last_update"] = time.time()

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.metrics)

    def reset(self):
        with self.lock:
            for k in self.metrics:
                if isinstance(self.metrics[k], (int, float)):
                    self.metrics[k] = 0
            self.metrics["last_update"] = time.time()

    def is_stale(self, max_age_sec: float = 5.0) -> bool:
        with self.lock:
            return (time.time() - self.metrics["last_update"]) > max_age_sec
