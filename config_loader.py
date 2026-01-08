# config_loader.py
"""
Centralized, read-only configuration loader.

Sources:
- Environment variables (required)
- Optional .env file (local/dev only)

No business logic.
No project dependencies.
Standard library only.
"""

import os
from typing import Dict, Optional


class ConfigError(Exception):
    """Raised on invalid or missing configuration."""


class Config:
    _loaded: bool = False
    _config: Dict[str, str] = {}

    # Minimal required base keys (can be extended safely)
    REQUIRED_KEYS = {
        "ENV",        # dev / staging / prod
        "APP_NAME",
        "LOG_LEVEL",
    }

    @classmethod
    def load(cls, dotenv_path: str = ".env") -> None:
        """
        Load configuration once.
        Safe to call multiple times.
        """
        if cls._loaded:
            return

        cls._load_dotenv(dotenv_path)
        cls._config = dict(os.environ)

        missing = sorted(
            key for key in cls.REQUIRED_KEYS
            if not cls._config.get(key)
        )
        if missing:
            raise ConfigError(
                f"Missing required config keys: {', '.join(missing)}"
            )

        cls._loaded = True

    @classmethod
    def get(cls, key: str) -> str:
        cls._ensure_loaded()
        if key not in cls._config:
            raise ConfigError(f"Config key not found: {key}")
        return cls._config[key]

    @classmethod
    def get_int(cls, key: str) -> int:
        value = cls.get(key)
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"Config key '{key}' is not a valid int")

    @classmethod
    def get_bool(cls, key: str) -> bool:
        value = cls.get(key).lower()
        if value in ("1", "true", "yes", "on"):
            return True
        if value in ("0", "false", "no", "off"):
            return False
        raise ConfigError(f"Config key '{key}' is not a valid bool")

    @classmethod
    def get_optional(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        cls._ensure_loaded()
        return cls._config.get(key, default)

    @classmethod
    def _ensure_loaded(cls) -> None:
        if not cls._loaded:
            raise ConfigError("Config not loaded. Call Config.load() first.")

    @staticmethod
    def _load_dotenv(path: str) -> None:
        """
        Load .env file if present.
        Existing environment variables are NOT overridden.
        """
        if not os.path.isfile(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
