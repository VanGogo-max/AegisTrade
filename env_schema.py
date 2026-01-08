# env_schema.py
"""
Environment schema validation.

Purpose:
- Define a single source of truth for environment variables
- Enforce presence, type and allowed values
- Fail-fast during application startup

Works on top of Config.
No business logic.
Standard library only.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Optional
from config_loader import Config, ConfigError


class EnvSchemaError(Exception):
    """Raised when environment schema validation fails."""


@dataclass(frozen=True)
class EnvField:
    name: str
    type: type
    required: bool = True
    allowed: Optional[Iterable[Any]] = None


class EnvSchema:
    """
    Enterprise ENV contract.
    Extend by adding fields – never inline-check env vars elsewhere.
    """

    FIELDS = (
        EnvField("ENV", str, allowed=("dev", "staging", "prod")),
        EnvField("APP_NAME", str),
        EnvField("LOG_LEVEL", str, allowed=("DEBUG", "INFO", "WARNING", "ERROR")),
        EnvField("API_KEY", str),
        EnvField("API_SECRET", str),
    )

    @classmethod
    def validate(cls) -> None:
        """
        Validate environment variables against schema.
        Must be called after Config.load().
        """
        errors = []

        for field in cls.FIELDS:
            try:
                raw_value = Config.get(field.name)
            except ConfigError:
                if field.required:
                    errors.append(f"{field.name}: missing")
                continue

            try:
                value = field.type(raw_value)
            except Exception:
                errors.append(f"{field.name}: invalid type")
                continue

            if field.allowed and value not in field.allowed:
                errors.append(
                    f"{field.name}: invalid value "
                    f"(allowed: {', '.join(map(str, field.allowed))})"
                )

        if errors:
            raise EnvSchemaError(
                "Environment schema validation failed:\n- "
                + "\n- ".join(errors)
            )
