# recovery_orchestrator.py
# Central Fail-Safe and Recovery Orchestrator for GRSM

import threading
import time


class RecoveryOrchestrator:
    """
    Monitors system health and orchestrates automatic recovery
    or safe-mode shutdown when critical conditions are detected.
    """

    def __init__(self, health_checker, latency_monitor, global_risk_state, strategy_manager, batch_optimizer):
        self.health_checker = health_checker
        self.latency_monitor = latency_monitor
        self.global_risk_state = global_risk_state
        self.strategy_manager = strategy_manager
        self.batch_optimizer = batch_optimizer
        self._stop_flag = threading.Event()
        self._thread = threading.Thread(target=self._run_loop)
        self._lock = threading.RLock()
        self.critical_latency_ms = 500  # example threshold

    def start(self):
        self._stop_flag.clear()
        self._thread.start()

    def stop(self):
        self._stop_flag.set()
        self._thread.join()

    def _run_loop(self):
        while not self._stop_flag.is_set():
            try:
                self._check_and_recover()
            except Exception as e:
                print(f"[RecoveryOrchestrator] Error: {e}")
            time.sleep(1)

    def _check_and_recover(self):
        with self._lock:
            # Check if trading is halted by risk manager
            if self.global_risk_state.is_trading_halted():
                print("[RecoveryOrchestrator] Risk halt detected. Stopping strategies and flushing batches.")
                self.strategy_manager.stop_all()
                self.batch_optimizer.flush_all()
                return

            # Check latency
            if self.latency_monitor.is_critical(self.critical_latency_ms):
                print(f"[RecoveryOrchestrator] Critical latency detected (> {self.critical_latency_ms}ms). Triggering safe mode.")
                self.strategy_manager.stop_all()
                self.batch_optimizer.flush_all()
                # Could implement additional throttling or circuit-breaker logic here

            # Additional health checks
            # Could extend to detect shadow ledger inconsistencies, event log corruption, etc.
