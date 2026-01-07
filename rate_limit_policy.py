"""
rate_limit_policy.py

Enterprise Rate Limit Policy

Responsibilities:
- Define rate limits per subscription plan
- Differentiate limits by action type
- Exempt admins from rate limits

Pure policy layer:
- No counters
- No persistence
- No enforcement
"""

from typing import Dict


class RateLimitDecision:
    """
    Result of a rate limit policy evaluation.
    """

    def __init__(self, allowed: bool, reason: str, limit: int) -> None:
        self.allowed = allowed
        self.reason = reason
        self.limit = limit


class RateLimitPolicy:
    """
    Defines rate limit rules per plan and action.
    """

    def __init__(self) -> None:
        # limits are expressed as requests per minute
        self._plan_limits: Dict[str, Dict[str, int]] = {
            "FREE": {
                "read": 30,
                "trade": 5,
            },
            "BASIC": {
                "read": 120,
                "trade": 30,
            },
            "PRO": {
                "read": 600,
                "trade": 120,
            },
        }

    # STEP A — Input validation
    def evaluate(
        self,
        plan: str,
        action: str,
        is_admin: bool = False,
    ) -> RateLimitDecision:
        if not isinstance(plan, str) or not plan:
            return RateLimitDecision(
                allowed=False,
                reason="invalid_plan",
                limit=0,
            )

        if not isinstance(action, str) or not action:
            return RateLimitDecision(
                allowed=False,
                reason="invalid_action",
                limit=0,
            )

        # STEP B — Policy resolution
        if is_admin:
            return RateLimitDecision(
                allowed=True,
                reason="admin_unlimited",
                limit=-1,
            )

        plan_limits = self._plan_limits.get(plan)
        if not plan_limits:
            return RateLimitDecision(
                allowed=False,
                reason="unknown_plan",
                limit=0,
            )

        limit = plan_limits.get(action)
        if limit is None:
            return RateLimitDecision(
                allowed=False,
                reason="action_not_allowed",
                limit=0,
            )

        # STEP C — Deterministic decision
        return RateLimitDecision(
            allowed=True,
            reason="rate_limit_applied",
            limit=limit,
        )
