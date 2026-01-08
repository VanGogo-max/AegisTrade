# secrets_guard.py
"""
Secrets access guard.

Purpose:
- Enforce explicit allow-list for secrets
- Prevent accidental logging / dumping
- Fail-fast on missing secrets
- Centralize secret access

Sources:
- Config (environment variables only)

No business logic.
Standard library only.
"""

from typing import FrozenSet
from config_loader import Config, ConfigError


class SecretsError(Exception):
    """Raised on invalid or unsafe secret access."""


class _SecretValue(str):
    """
    String wrapper that prevents accidental logging.
    """

    def __repr__(self) -> str:  # pragma: no cover
        return "<SECRET>"

    def __str__(self) -> str:  # pragma: no cover
        return "<SECRET>"


class SecretsGuard:
    _loaded: bool = False
    _allowed: FrozenSet[str] = frozenset()

    # Minimal baseline – extend via env, not code
    BASE_REQUIRED = {
        "API_KEY",
        "API_SECRET",
    }

    @classmethod
    def load(cls) -> None:
        """
        Validate and lock secrets.
        Must be called once at startup.
        """
        if cls._loaded:
            return

        missing = []
        for key in cls.BASE_REQUIRED:
            try:
                Config.get(key)
            except ConfigError:
                missing.append(key)

        if missing:
            raise SecretsError(
                f"Missing required secrets: {', '.join(sorted(missing))}"
            )

        cls._allowed = frozenset(cls.BASE_REQUIRED)
        cls._loaded = True

    @classmethod
    def get(cls, key: str) -> str:
        """
        Return secret value.
        Logging-safe wrapper is enforced.
        """
        cls._ensure_loaded()

        if key not in cls._allowed:
            raise SecretsError(f"Access denied to secret: {key}")

        value = Config.get(key)
        return _SecretValue(value)

    @classmethod
    def is_allowed(cls, key: str) -> bool:
        cls._ensure_loaded()
        return key in cls._allowed

    @classmethod
    def _ensure_loaded(cls) -> None:
        if not cls._loaded:
            raise SecretsError(
                "SecretsGuard not loaded. Call SecretsGuard.load() first."
            )
