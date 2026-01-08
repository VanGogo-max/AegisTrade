# observability_tracing.py
"""
ObservabilityTracing.

Purpose:
- Central runtime tracing management
- ENV-driven, runtime-safe
- Context manager for spans
- Compatible with OpenTelemetry / Jaeger / Zipkin

No business logic.
Standard library only.
"""

from runtime_guard import RuntimeGuard
from observability_config import ObservabilityConfig
from contextlib import contextmanager
from time import perf_counter

class TracingError(Exception):
    """Raised on tracing operation failures."""


class ObservabilityTracing:
    _active_spans: list[str] = []

    @classmethod
    @contextmanager
    def span(cls, name: str, attributes: dict | None = None):
        """
        Context manager for a tracing span.
        Example usage:

        with ObservabilityTracing.span("execute_trade", {"user_id": 123}):
            ...
        """
        RuntimeGuard.assert_ready("ObservabilityTracing")

        config = ObservabilityConfig.get()
        if not config.tracing_enabled:
            # Tracing disabled, skip execution
            yield
            return

        attributes = attributes or {}
        start_time = perf_counter()
        cls._active_spans.append(name)
        try:
            yield
        finally:
            end_time = perf_counter()
            cls._active_spans.pop()
            # Placeholder: export span, duration, attributes
            # Example for telemetry export:
            # TelemetryExporter.send(name, start_time, end_time, attributes)

    @classmethod
    def current_span(cls) -> str | None:
        """Return the current active span, if any."""
        return cls._active_spans[-1] if cls._active_spans else None
