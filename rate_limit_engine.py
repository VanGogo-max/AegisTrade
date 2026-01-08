# rate_limit_engine.py
"""
RateLimitEngine.

Purpose:
- Centralized runtime enforcement of rate limits
- Fail-fast on policy violation
- Runtime-safe and startup-safe

No business logic.
Standard library only.
"""

from typing import Dict
from policy_registry import PolicyRegistry, PolicyRegistryError
from runtime_guard import RuntimeGuard


class RateLimitError(Exception):
    """Raised when a rate limit is exceeded."""


class RateLimitEngine:
    _counters: Dict[str, int] = {}
    _thresholds: Dict[str, int] = {}

    @classmethod
    def configure_threshold(cls, policy_name: str, limit: int) -> None:
        """
        Set max allowed calls for a policy.
        Must be done before runtime usage.
        """
        cls._thresholds[policy_name] = limit

    @classmethod
    def check(cls, policy_name: str, entity_id: str) -> None:
        """
        Enforce rate limit for a given entity (user, bot, strategy, etc.)
        Raises RateLimitError on violation.
        """
        RuntimeGuard.assert_ready("RateLimitEngine")

        try:
            PolicyRegistry.get(policy_name)
        except PolicyRegistryError as exc:
            raise RateLimitError(
                f"Unknown rate limit policy '{policy_name}'"
            ) from exc

        limit = cls._thresholds.get(policy_name)
        if limit is None:
            raise RateLimitError(f"No threshold configured for policy '{policy_name}'")

        key = f"{policy_name}:{entity_id}"
        cls._counters[key] = cls._counters.get(key, 0) + 1

        if cls._counters[key] > limit:
            raise RateLimitError(
                f"Rate limit exceeded for {entity_id} under policy '{policy_name}'"
            )

    @classmethod
    def reset(cls, entity_id: str, policy_name: str) -> None:
        """
        Reset counter for specific entity and policy.
        """
        key = f"{policy_name}:{entity_id}"
        cls._counters.pop(key, None)
