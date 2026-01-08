"""
trade_intent_schema.py

Canonical trade intent schema.

Purpose:
- Single source of truth for what execution_engine is allowed to execute
- Strict validation BEFORE risk, billing and execution layers
- Deterministic, explicit, auditable structure

Design rules:
- NO execution logic
- NO side effects
- NO external dependencies
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


class TradeIntentValidationError(Exception):
    pass


@dataclass(frozen=True)
class TradeIntent:
    """
    Immutable trade intent.
    """

    # Core identifiers
    intent_id: str = field(default_factory=lambda: str(uuid4()))
    strategy_id: str = ""
    actor_id: str = ""

    # Trade definition
    symbol: str = ""
    side: str = ""           # buy | sell
    quantity: float = 0.0
    price: float = 0.0

    # Execution context
    exchange: str = ""
    time_in_force: str = "GTC"   # GTC | IOC | FOK
    created_at_utc: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    # Optional metadata (never interpreted by engine)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate intent invariants.
        Raises TradeIntentValidationError on failure.
        """

        if not self.strategy_id:
            raise TradeIntentValidationError("strategy_id is required")

        if not self.actor_id:
            raise TradeIntentValidationError("actor_id is required")

        if not self.symbol:
            raise TradeIntentValidationError("symbol is required")

        if self.side not in {"buy", "sell"}:
            raise TradeIntentValidationError("side must be 'buy' or 'sell'")

        if self.quantity <= 0:
            raise TradeIntentValidationError("quantity must be positive")

        if self.price <= 0:
            raise TradeIntentValidationError("price must be positive")

        if not self.exchange:
            raise TradeIntentValidationError("exchange is required")

        if self.time_in_force not in {"GTC", "IOC", "FOK"}:
            raise TradeIntentValidationError(
                "time_in_force must be GTC, IOC or FOK"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize intent to dict (safe for audit / execution).
        """
        return {
            "intent_id": self.intent_id,
            "strategy_id": self.strategy_id,
            "actor_id": self.actor_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "exchange": self.exchange,
            "time_in_force": self.time_in_force,
            "created_at_utc": self.created_at_utc,
            "metadata": dict(self.metadata),
        }
