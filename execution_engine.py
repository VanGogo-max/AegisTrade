# execution_engine.py
# Core Execution Engine for GRSM
# Handles actual order submission, shadow ledger simulation, and thread-safety

import threading
from typing import Dict, List

class ShadowLedger:
    """
    Minimal shadow ledger to track simulated positions and account state
    """
    def __init__(self, starting_balance: float = 100000.0):
        self.account = {"balance": starting_balance, "used_margin": 0.0}
        self.positions: Dict[str, Dict] = {}  # e.g., {"BTCUSDT": {"size": 0.05, "entry_price": 25000}}
        self._lock = threading.RLock()

    def simulate_order(self, order: Dict):
        with self._lock:
            symbol = order["symbol"]
            size = order["size"] * order["direction"]
            price = order["price"]

            pos = self.positions.get(symbol, {"size": 0.0, "entry_price": 0.0})

            new_size = pos["size"] + size
            if new_size != 0:
                new_entry_price = (pos["size"]*pos["entry_price"] + size*price)/new_size
            else:
                new_entry_price = 0.0

            self.positions[symbol] = {"size": new_size, "entry_price": new_entry_price}

            # Update used margin (simplified)
            self.account["used_margin"] = sum(abs(p["size"]*p["entry_price"]) for p in self.positions.values())

    def get_snapshot(self):
        with self._lock:
            return {"account": self.account.copy(), "positions": {k:v.copy() for k,v in self.positions.items()}}


class ExecutionEngine:
    """
    Handles sending orders to real exchanges (mocked for simulation)
    """
    def __init__(self):
        self.shadow_ledger = ShadowLedger()
        self._lock = threading.RLock()

    def send_order(self, order: Dict):
        """
        Sends order to exchange.
        Here it is mocked; in real usage, connect to REST/WebSocket or SDK.
        """
        with self._lock:
            # First simulate order in shadow ledger
            self.shadow_ledger.simulate_order(order)

            # Mock actual execution
            print(f"[ExecutionEngine] Executed order: {order}")

    def batch_execute(self, orders: List[Dict]):
        """
        Execute multiple orders atomically
        """
        results = []
        with self._lock:
            for order in orders:
                self.send_order(order)
                results.append(order)
        return results
