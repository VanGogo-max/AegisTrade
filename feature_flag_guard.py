# feature_flag_guard.py
"""
FeatureFlagGuard.

Purpose:
- Central runtime enforcement of feature toggles
- ENV-driven and configurable per environment
- Runtime-safe and fail-fast on disabled feature

No business logic.
Standard library only.
"""

from runtime_guard import RuntimeGuard
from config_loader import Config


class FeatureFlagError(Exception):
    """Raised when a feature is disabled."""


class FeatureFlagGuard:
    _cache: dict[str, bool] = {}

    @classmethod
    def assert_enabled(cls, feature_name: str) -> None:
        """
        Ensure that a given feature is enabled.
        Raises FeatureFlagError if disabled.
        Caches value for efficiency.
        """
        RuntimeGuard.assert_ready("FeatureFlagGuard")

        key = feature_name.upper()
        if key not in cls._cache:
            try:
                cls._cache[key] = Config.get_bool(f"FEATURE_{key}")
            except Exception as exc:
                raise FeatureFlagError(
                    f"Failed to read feature flag '{feature_name}'"
                ) from exc

        if not cls._cache[key]:
            raise FeatureFlagError(f"Feature '{feature_name}' is disabled")

    @classmethod
    def reset_cache(cls) -> None:
        """Reset cached feature flags (useful for testing or hot reload)."""
        cls._cache.clear()
