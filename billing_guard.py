# billing_guard.py
"""
BillingGuard.

Purpose:
- Central runtime enforcement of billing and subscription policies
- Fail-fast on invalid subscription or billing violation
- Runtime-safe and startup-safe

No business logic.
Standard library only.
"""

from typing import Any, Dict
from runtime_guard import RuntimeGuard
from policy_registry import PolicyRegistry, PolicyRegistryError


class BillingGuardError(Exception):
    """Raised when billing or subscription check fails."""


class BillingGuard:
    @classmethod
    def enforce(
        cls, policy_name: str, user_id: str, context: Dict[str, Any] | None = None
    ) -> None:
        """
        Enforce a billing or subscription policy at runtime.
        Raises BillingGuardError on violation.
        """
        RuntimeGuard.assert_ready("BillingGuard")

        try:
            policy = PolicyRegistry.get(policy_name)
        except PolicyRegistryError as exc:
            raise BillingGuardError(
                f"Unknown billing/subscription policy '{policy_name}'"
            ) from exc

        # Placeholder: actual billing evaluation is outside enterprise core
        # Interface ensures:
        # 1) Runtime readiness
        # 2) Known policy enforcement
        # 3) Explicit call for audit / compliance
        #
        # Example:
        # if not policy.allow(user_id, context):
        #     raise BillingGuardError(
        #         f"User {user_id} violates policy {policy_name}"
        #     )
