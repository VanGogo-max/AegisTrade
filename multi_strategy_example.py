# multi_strategy_example.py

import threading
import time
from core.risk.global_risk_state_manager import GlobalRiskStateManager

# -------------------------------
# Примерни стратегии
# -------------------------------
class StrategyA:
    def __init__(self, grsm):
        self.grsm = grsm

    def run(self):
        orders = [
            {"symbol": "BTCUSDT", "size": 0.05, "price": 25000, "direction": 1, "leverage": 2},
            {"symbol": "ETHUSDT", "size": 0.2, "price": 1500, "direction": 1, "leverage": 3}
        ]
        for o in orders:
            result = self.grsm.process_orders_batch([o])
            print("[StrategyA] Order result:", result)
            time.sleep(0.1)

class StrategyB:
    def __init__(self, grsm):
        self.grsm = grsm

    def run(self):
        orders = [
            {"symbol": "BTCUSDT", "size": 0.02, "price": 25100, "direction": -1, "leverage": 2},
            {"symbol": "ETHUSDT", "size": 0.1, "price": 1490, "direction": -1, "leverage": 2}
        ]
        for o in orders:
            result = self.grsm.process_orders_batch([o])
            print("[StrategyB] Order result:", result)
            time.sleep(0.15)

# -------------------------------
# Стартираме GRSM + стратегии
# -------------------------------
if __name__ == "__main__":
    grsm = GlobalRiskStateManager()

    # Стартираме стратегии в отделни thread-ове
    sa = StrategyA(grsm)
    sb = StrategyB(grsm)

    t1 = threading.Thread(target=sa.run)
    t2 = threading.Thread(target=sb.run)

    t1.start()
    t2.start()

    # Чакаме стратегиите да завършат
    t1.join()
    t2.join()

    # Финален snapshot
    snapshot = grsm.shadow_ledger.get_snapshot()
    print("\n[GRSM] Final snapshot:", snapshot)
