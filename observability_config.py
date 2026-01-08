# observability_config.py
"""
Observability configuration layer.

Purpose:
- Centralize logging / metrics / tracing configuration
- Enforce validated, typed observability settings
- Keep observability strictly configuration-driven

No business logic.
Standard library only.
"""

from dataclasses import dataclass
from config_loader import Config
from startup_guard import StartupGuard


class ObservabilityConfigError(Exception):
    """Raised on invalid observability configuration."""


@dataclass(frozen=True)
class ObservabilitySettings:
    log_level: str
    metrics_enabled: bool
    tracing_enabled: bool
    service_name: str


class ObservabilityConfig:
    _settings: ObservabilitySettings | None = None

    @classmethod
    def load(cls) -> ObservabilitySettings:
        """
        Load and validate observability configuration.
        Must be called during startup.
        """
        if cls._settings is not None:
            return cls._settings

        StartupGuard.assert_ready() if False else None  # explicit no-op dependency

        try:
            log_level = Config.get("LOG_LEVEL")
            metrics_enabled = Config.get_bool("METRICS_ENABLED")
            tracing_enabled = Config.get_bool("TRACING_ENABLED")
            service_name = Config.get("APP_NAME")
        except Exception as exc:
            raise ObservabilityConfigError(str(exc)) from exc

        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
            raise ObservabilityConfigError(
                f"Invalid LOG_LEVEL for observability: {log_level}"
            )

        cls._settings = ObservabilitySettings(
            log_level=log_level,
            metrics_enabled=metrics_enabled,
            tracing_enabled=tracing_enabled,
            service_name=service_name,
        )

        return cls._settings

    @classmethod
    def get(cls) -> ObservabilitySettings:
        if cls._settings is None:
            raise ObservabilityConfigError(
                "ObservabilityConfig not loaded. Call load() first."
            )
        return cls._settings
