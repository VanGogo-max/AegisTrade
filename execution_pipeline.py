# execution_pipeline.py
"""
execution_pipeline.py — FINAL

Deterministic execution orchestrator.

Purpose:
- Wire the full execution flow in ONE place
- Enforce strict order:
    1) Preflight (capabilities validation)
    2) ExecutionEngine (policies / risk / billing)
    3) Exchange routing
    4) Adapter execution (build tx payload)
- No strategy logic
- No signing
- No network calls

Inputs:
- trade_intent (dict)

Output:
- execution_result (dict) ready for signer / sender
"""

from typing import Dict, Any

from exchange_registry import ExchangeRegistry
from trade_preflight_validator import TradePreflightValidator
from execution_engine import ExecutionEngine, ExecutionRejected


class ExecutionPipelineError(Exception):
    """Raised when pipeline execution fails."""


class ExecutionPipeline:
    """
    Single-entry execution pipeline.
    """

    def __init__(self, registry: ExchangeRegistry):
        self._registry = registry
        self._router = registry.get_router()

    def execute(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade intent through the full pipeline.
        """

        try:
            # =========================
            # 1. Capabilities preflight
            # =========================
            exchange = trade_intent.get("exchange")
            if not exchange:
                raise ExecutionPipelineError(
                    "TradeIntent missing 'exchange'"
                )

            capabilities = self._registry.get_capabilities(exchange)
            TradePreflightValidator.validate(trade_intent, capabilities)

            # =========================
            # 2. Execution engine (guards)
            # =========================
            engine_result = ExecutionEngine.execute(trade_intent)
            if engine_result.get("status") != "APPROVED":
                raise ExecutionPipelineError("Execution not approved")

            # =========================
            # 3. Route to exchange adapter
            # =========================
            adapter = self._router.route(trade_intent)

            # =========================
            # 4. Adapter execution
            # =========================
            action = trade_intent.get("action")
            if not action:
                raise ExecutionPipelineError(
                    "TradeIntent missing 'action'"
                )

            if action == "OPEN_POSITION":
                execution_payload = adapter.open_position(trade_intent)
            elif action == "CLOSE_POSITION":
                execution_payload = adapter.close_position(trade_intent)
            else:
                raise ExecutionPipelineError(
                    f"Unsupported action '{action}'"
                )

            return {
                "status": "READY",
                "exchange": exchange,
                "payload": execution_payload,
            }

        except ExecutionRejected as exc:
            raise ExecutionPipelineError(
                f"Execution rejected: {exc}"
            ) from exc

        except Exception as exc:
            raise ExecutionPipelineError(str(exc)) from exc
