# subscription_policy.py
"""
SubscriptionPolicy.

Purpose:
- Central runtime enforcement of subscription policies
- Multi-plan and multi-user safe
- Fail-fast on invalid or expired subscription
- Runtime-safe

No business logic.
Standard library only.
"""

from typing import Any, Dict
from runtime_guard import RuntimeGuard
from policy_registry import PolicyRegistry, PolicyRegistryError


class SubscriptionPolicyError(Exception):
    """Raised when subscription check fails."""


class SubscriptionPolicy:
    _plans: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def define_plan(cls, policy_name: str, plan_config: Dict[str, Any]) -> None:
        """
        Define a subscription plan configuration.
        Must be called during startup.
        """
        cls._plans[policy_name] = plan_config

    @classmethod
    def enforce(
        cls, policy_name: str, user_id: str, context: Dict[str, Any] | None = None
    ) -> None:
        """
        Enforce a subscription policy at runtime.
        Raises SubscriptionPolicyError on violation.
        """
        RuntimeGuard.assert_ready("SubscriptionPolicy")

        try:
            PolicyRegistry.get(policy_name)
        except PolicyRegistryError as exc:
            raise SubscriptionPolicyError(
                f"Unknown subscription policy '{policy_name}'"
            ) from exc

        plan = cls._plans.get(policy_name)
        if plan is None:
            raise SubscriptionPolicyError(
                f"No plan configuration found for policy '{policy_name}'"
            )

        # Placeholder: actual subscription validation happens outside core
        # Example:
        # if plan["status"] != "active":
        #     raise SubscriptionPolicyError(
        #         f"User {user_id} subscription inactive under {policy_name}"
        #     )
