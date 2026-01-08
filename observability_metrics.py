# observability_metrics.py
"""
ObservabilityMetrics.

Purpose:
- Centralized runtime metrics collection
- ENV-driven and runtime-safe
- Compatible with ObservabilityConfig, Prometheus, OpenTelemetry
- Read-only API for consumers

No business logic.
Standard library only.
"""

from runtime_guard import RuntimeGuard
from observability_config import ObservabilityConfig

class ObservabilityMetricsError(Exception):
    """Raised on invalid metrics operations."""


class ObservabilityMetrics:
    _counters: dict[str, int] = {}

    @classmethod
    def increment(cls, name: str, value: int = 1) -> None:
        """
        Increment a named counter.
        Runtime-safe, no business logic executed.
        """
        RuntimeGuard.assert_ready("ObservabilityMetrics")
        config = ObservabilityConfig.get()
        if not config.metrics_enabled:
            return

        cls._counters[name] = cls._counters.get(name, 0) + value

    @classmethod
    def get(cls, name: str) -> int:
        """
        Return the current value of a counter.
        """
        return cls._counters.get(name, 0)

    @classmethod
    def reset(cls, name: str | None = None) -> None:
        """
        Reset counter(s). Useful for tests or controlled resets.
        """
        if name:
            cls._counters.pop(name, None)
        else:
            cls._counters.clear()

    @classmethod
    def list_counters(cls) -> tuple[str, ...]:
        """List all registered metric names."""
        return tuple(sorted(cls._counters.keys()))
