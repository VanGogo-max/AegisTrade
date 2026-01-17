# health_checker.py
# Health Monitoring for GRSM
# Checks core modules and triggers alerts / fail-safe

import threading
import time

class HealthChecker:
    """
    Periodically checks the health of GRSM components.
    """

    def __init__(self, risk_monitor, execution_engine, batch_optimizer, strategy_manager, interval_sec=1.0):
        self.risk_monitor = risk_monitor
        self.execution_engine = execution_engine
        self.batch_optimizer = batch_optimizer
        self.strategy_manager = strategy_manager
        self.interval_sec = interval_sec
        self._stop_flag = threading.Event()
        self._thread = threading.Thread(target=self._run_loop)
        self._lock = threading.RLock()

    def start(self):
        self._stop_flag.clear()
        self._thread.start()

    def stop(self):
        self._stop_flag.set()
        self._thread.join()

    def _run_loop(self):
        while not self._stop_flag.is_set():
            try:
                self._check_health()
            except Exception as e:
                print(f"[HealthChecker] Error during health check: {e}")
            time.sleep(self.interval_sec)

    def _check_health(self):
        with self._lock:
            if self.risk_monitor.is_halted():
                print("[HealthChecker] RiskMonitor halted! Triggering emergency procedures.")

            # Example checks: shadow ledger consistency
            snapshot = self.execution_engine.shadow_ledger.get_snapshot()
            account_balance = snapshot["account"]["balance"]
            used_margin = snapshot["account"]["used_margin"]

            if used_margin > account_balance * 1.0:  # margin cannot exceed total balance
                print("[HealthChecker] Margin exceeds account balance! Halting system.")
                self.risk_monitor._trigger_halt("MARGIN_OVERFLOW_DETECTED")

            # Check pending orders in batch optimizer
            for symbol, orders in self.batch_optimizer._pending_orders.items():
                if len(orders) > self.batch_optimizer.max_batch_size * 10:
                    print(f"[HealthChecker] Too many pending orders for {symbol}. Flushing batch.")
                    self.batch_optimizer.flush(symbol)

            # Additional strategy activity checks could be added here
