# strategy_manager.py
# Central Strategy Manager for GRSM
# Coordinates multiple strategies, threads, and batch execution

import threading
from typing import List
from core.strategies.base_strategy import BaseStrategy

class StrategyManager:
    """
    Manages multiple strategies, running them in parallel threads,
    submitting orders via BatchOptimizer, and respecting RiskMonitor signals.
    """

    def __init__(self, batch_optimizer, risk_monitor):
        self.batch_optimizer = batch_optimizer
        self.risk_monitor = risk_monitor
        self.strategies: List[BaseStrategy] = []
        self._threads: List[threading.Thread] = []
        self._lock = threading.RLock()

    def register_strategy(self, strategy: BaseStrategy):
        """
        Add a strategy to the manager
        """
        with self._lock:
            self.strategies.append(strategy)

    def start_all(self):
        """
        Launch all registered strategies in separate threads
        """
        with self._lock:
            for strat in self.strategies:
                t = threading.Thread(target=self._run_strategy_loop, args=(strat,))
                t.start()
                self._threads.append(t)

    def _run_strategy_loop(self, strategy: BaseStrategy):
        """
        Core loop for running a strategy:
        - generate orders
        - submit via batch optimizer
        - check risk halt flag
        """
        while not self.risk_monitor.is_halted():
            try:
                orders = strategy.generate_orders()
                if orders:
                    for order in orders:
                        self.batch_optimizer.submit_order(order)
            except Exception as e:
                print(f"[StrategyManager] Error in {strategy.name}: {e}")

    def wait_for_completion(self):
        """
        Join all strategy threads (optional, for testing or controlled runs)
        """
        for t in self._threads:
            t.join()
