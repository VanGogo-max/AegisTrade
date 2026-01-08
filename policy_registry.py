# policy_registry.py
"""
Policy registry.

Purpose:
- Central, explicit registry for all policy components
- Enforce allow-listing and lifecycle safety
- Prevent dynamic / unsafe policy mutation at runtime

No business logic.
Standard library only.
"""

from typing import Dict, Protocol
from startup_guard import StartupGuard
from runtime_guard import RuntimeGuard


class PolicyRegistryError(Exception):
    """Raised on invalid policy registry operations."""


class Policy(Protocol):
    """
    Structural contract for policies.
    Business logic is outside the scope.
    """

    name: str


class PolicyRegistry:
    _policies: Dict[str, Policy] = {}
    _locked: bool = False

    @classmethod
    def register(cls, policy: Policy) -> None:
        """
        Register a policy.
        Allowed ONLY before system startup completion.
        """
        if cls._locked:
            raise PolicyRegistryError(
                "Policy registry is locked; registration not allowed"
            )

        if not hasattr(policy, "name"):
            raise PolicyRegistryError("Policy must define 'name' attribute")

        name = policy.name

        if name in cls._policies:
            raise PolicyRegistryError(f"Policy already registered: {name}")

        cls._policies[name] = policy

    @classmethod
    def lock(cls) -> None:
        """
        Lock registry after startup.
        Must be called before SYSTEM_READY.
        """
        if cls._locked:
            return

        cls._locked = True

    @classmethod
    def get(cls, name: str) -> Policy:
        """
        Retrieve a registered policy.
        Runtime-safe.
        """
        RuntimeGuard.assert_ready("PolicyRegistry")

        try:
            return cls._policies[name]
        except KeyError:
            raise PolicyRegistryError(f"Policy not found: {name}")

    @classmethod
    def list(cls) -> tuple[str, ...]:
        """
        List registered policy names.
        Runtime-safe.
        """
        RuntimeGuard.assert_ready("PolicyRegistry")
        return tuple(sorted(cls._policies.keys()))
