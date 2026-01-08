# risk_gate.py
"""
RiskGate.

Purpose:
- Central runtime validation point for all risk policies
- Fail-fast on policy violation
- Runtime-safe and startup-safe

No business logic.
Standard library only.
"""

from policy_registry import PolicyRegistry, PolicyRegistryError
from runtime_guard import RuntimeGuard


class RiskGateError(Exception):
    """Raised when a risk policy is violated."""


class RiskGate:
    @classmethod
    def evaluate(cls, policy_name: str, **context) -> None:
        """
        Evaluate a risk policy at runtime.
        Raises RiskGateError on violation.
        """
        RuntimeGuard.assert_ready("RiskGate")

        try:
            policy = PolicyRegistry.get(policy_name)
        except PolicyRegistryError as exc:
            raise RiskGateError(
                f"Risk evaluation failed: unknown policy '{policy_name}'"
            ) from exc

        # Placeholder: policy check logic is outside enterprise core
        # Only interface / contract is enforced
        # Example for auditing / extension:
        # if not policy.allow(context):
        #     raise RiskGateError(f"Policy {policy_name} violation")
