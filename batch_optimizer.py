# batch_optimizer.py
# Batch Optimizer for GRSM Order Execution
# Thread-safe, multi-strategy ready

import threading
from typing import List, Dict
from collections import defaultdict

class BatchOptimizer:
    """
    Optimizes order execution by grouping orders per symbol,
    reducing slippage, and minimizing execution costs.
    Works in conjunction with OrderRouter and RiskMonitor.
    """

    def __init__(self, order_router, max_batch_size: int = 5):
        self.order_router = order_router
        self.max_batch_size = max_batch_size
        self._lock = threading.RLock()
        self._pending_orders: Dict[str, List[Dict]] = defaultdict(list)

    def submit_order(self, order: Dict):
        """
        Add order to batch queue. If batch size reached, flush automatically.
        Returns result of execution or None if queued.
        """
        with self._lock:
            symbol = order["symbol"]
            self._pending_orders[symbol].append(order)
            if len(self._pending_orders[symbol]) >= self.max_batch_size:
                return self.flush(symbol)
        return None

    def flush(self, symbol: str = None):
        """
        Commit all pending orders for a given symbol or all symbols.
        Returns list of execution results.
        """
        with self._lock:
            results = []
            symbols_to_flush = [symbol] if symbol else list(self._pending_orders.keys())

            for sym in symbols_to_flush:
                batch = self._pending_orders.get(sym, [])
                if batch:
                    res = self.order_router.process_orders_batch(batch)
                    results.extend(res)
                    self._pending_orders[sym] = []  # clear after flush

            return results

    def flush_all(self):
        """
        Flush all pending orders for all symbols.
        """
        return self.flush()
