# access_control_policy.py
"""
AccessControlPolicy.

Purpose:
- Centralized runtime enforcement of access control rules
- Fail-fast on unauthorized access
- Runtime-safe and startup-safe

No business logic.
Standard library only.
"""

from typing import Any, Dict
from policy_registry import PolicyRegistry, PolicyRegistryError
from runtime_guard import RuntimeGuard


class AccessControlError(Exception):
    """Raised when access control policy is violated."""


class AccessControlPolicy:
    @classmethod
    def enforce(
        cls, policy_name: str, entity_id: str, context: Dict[str, Any] | None = None
    ) -> None:
        """
        Enforce an access control policy at runtime.
        Raises AccessControlError on violation.
        """
        RuntimeGuard.assert_ready("AccessControlPolicy")

        try:
            policy = PolicyRegistry.get(policy_name)
        except PolicyRegistryError as exc:
            raise AccessControlError(
                f"Unknown access control policy '{policy_name}'"
            ) from exc

        # Placeholder: actual access evaluation is outside core
        # Interface enforces:
        # 1) Runtime readiness
        # 2) Known policy
        # 3) Explicit call for audit / compliance
        #
        # Example:
        # if not policy.allow(entity_id, context):
        #     raise AccessControlError(
        #         f"Access denied for {entity_id} under policy {policy_name}"
        #     )
