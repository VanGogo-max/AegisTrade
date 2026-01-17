# order_router.py
# Central Order Router for GRSM
# Thread-safe, risk-aware, fail-safe ready

import threading
from typing import List, Dict

class OrderRouter:
    """
    Handles batch order submission from multiple strategies,
    validates via RiskMonitor and RiskRulesEngine,
    and routes to execution engine safely.
    """

    def __init__(self, risk_monitor, risk_engine, execution_engine):
        self.risk_monitor = risk_monitor
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self._lock = threading.RLock()

    def process_orders_batch(self, orders: List[Dict]):
        """
        Processes a batch of orders atomically:
        1. Validate each order
        2. If all pass, commit to execution engine
        3. If any fails, block batch and trigger alerts if needed
        Returns list of results per order.
        """
        results = []
        with self._lock:
            if self.risk_monitor.is_halted():
                return [{"order": o, "status": "HALTED"} for o in orders]

            for order in orders:
                decision = self.risk_engine.evaluate(
                    self.execution_engine.shadow_ledger.account,
                    self.execution_engine.shadow_ledger.positions,
                    order
                )
                results.append({"order": order, "status": decision})

            # Check if any order was blocked
            if any(r["status"] != "ALLOW" for r in results):
                return results  # Blocked batch, do not execute

            # All allowed → commit
            for r in results:
                self._commit_order(r["order"])

        return results

    def _commit_order(self, order: Dict):
        """
        Sends order to execution engine.
        Thread-safe commit with shadow ledger update.
        """
        # First, simulate in shadow ledger
        self.execution_engine.shadow_ledger.simulate_order(order)

        # Then commit to real execution engine
        self.execution_engine.send_order(order)
