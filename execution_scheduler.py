"""
execution_scheduler.py

Enterprise-grade scheduler for TradeIntent execution.

Purpose:
- Periodically fetch or receive intents
- Orchestrate execution via ExecutionEngine
- Dispatch to appropriate exchange adapter (paper or real)
- Log all executions to audit + persistence
- Safe, deterministic, testable

Constraints:
- No strategy logic
- No direct trading decisions
- Thread-safe
- Standard library only
"""

import threading
import time
from typing import List, Callable, Dict, Any

from trade_intent_schema import TradeIntent, TradeIntentValidationError
from execution_engine import ExecutionEngine, ExecutionRejected
from execution_audit_log import ExecutionAuditLog
from execution_persistence import ExecutionPersistence

# Exchange adapter interface
from exchange_adapter_base import ExchangeAdapterBase


class ExecutionScheduler:
    """
    Threaded scheduler for TradeIntent execution.
    """

    def __init__(
        self,
        fetch_intents_fn: Callable[[], List[TradeIntent]],
        exchange_adapter: ExchangeAdapterBase,
        interval_seconds: float = 1.0,
    ):
        """
        Args:
            fetch_intents_fn: Function returning list of TradeIntent
            exchange_adapter: Exchange adapter (paper or real)
            interval_seconds: Scheduler tick interval
        """
        self.fetch_intents_fn = fetch_intents_fn
        self.exchange_adapter = exchange_adapter
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.persistence = ExecutionPersistence()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                intents = self.fetch_intents_fn()
                for intent in intents:
                    self._process_intent(intent)
            except Exception as exc:
                # Optional: log scheduler-level exceptions
                print(f"Scheduler exception: {exc}")
            time.sleep(self.interval_seconds)

    def _process_intent(self, intent: TradeIntent) -> None:
        """
        Validate, execute, audit, persist
        """
        try:
            intent.validate()
        except TradeIntentValidationError as exc:
            print(f"Invalid TradeIntent: {exc}")
            return

        try:
            result = ExecutionEngine.execute(intent.to_dict())
        except ExecutionRejected as exc:
            status = "REJECTED"
            print(f"ExecutionRejected: {exc}")
        else:
            status = "APPROVED"

        # Dispatch to exchange adapter only if approved
        exchange_result = None
        if status == "APPROVED":
            try:
                exchange_result = self.exchange_adapter.place_order(intent.to_dict())
            except Exception as exc:
                status = "FAILED"
                print(f"Exchange error: {exc}")

        # Record in audit log
        ExecutionAuditLog.record(
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            price=intent.price,
            exchange=intent.exchange,
            strategy=intent.strategy_id,
            result=status,
            metadata={"exchange_result": exchange_result},
        )

        # Persist snapshot
        self.persistence.append({
            "intent": intent.to_dict(),
            "status": status,
            "exchange_result": exchange_result
        })
