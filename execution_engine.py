# execution_engine.py
"""
ExecutionEngine.

Purpose:
- Central decision engine for automated trade execution
- Orchestrates all guards and policies
- Decides APPROVED / REJECTED
- No business logic, no exchange interaction

Standard library only.
"""

from typing import Dict, Any

from runtime_guard import RuntimeGuard
from feature_flag_guard import FeatureFlagGuard
from access_control_policy import AccessControlPolicy
from subscription_policy import SubscriptionPolicy
from billing_guard import BillingGuard
from risk_gate import RiskGate
from rate_limit_engine import RateLimitEngine
from observability_tracing import ObservabilityTracing
from observability_metrics import ObservabilityMetrics


class ExecutionRejected(Exception):
    """Raised when execution is rejected by any guard."""


class ExecutionEngine:
    @classmethod
    def execute(cls, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a trade intent and decide whether execution is allowed.

        Expected intent keys (minimum):
        - user_id
        - action
        - symbol
        - side
        - quantity
        """
        RuntimeGuard.assert_ready("ExecutionEngine")

        with ObservabilityTracing.span("execution_engine"):
            try:
                FeatureFlagGuard.assert_enabled("trading")

                AccessControlPolicy.enforce(
                    policy_name="trade_execution",
                    subject_id=intent["user_id"]
                )

                SubscriptionPolicy.enforce(
                    policy_name="trade_execution",
                    user_id=intent["user_id"],
                    context=intent
                )

                BillingGuard.enforce(
                    user_id=intent["user_id"],
                    action="trade"
                )

                RiskGate.evaluate(intent)

                RateLimitEngine.consume(
                    key=str(intent["user_id"]),
                    action="trade"
                )

            except Exception as exc:
                ObservabilityMetrics.increment("execution_rejected")
                raise ExecutionRejected(str(exc)) from exc

            ObservabilityMetrics.increment("execution_approved")
            return {
                "status": "APPROVED",
                "intent": intent,
            }
