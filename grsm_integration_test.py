# tests/grsm_integration_test.py

import threading
from core.risk.global_risk_state_manager import GlobalRiskStateManager
from core.strategies.base_strategy import BaseStrategy

# -------------------------------
# Примерни стратегии
# -------------------------------
class TestStrategyA(BaseStrategy):
    def generate_orders(self):
        return [
            {"symbol": "BTCUSDT", "size": 0.05, "price": 25000, "direction": 1, "leverage": 2},
            {"symbol": "ETHUSDT", "size": 0.1, "price": 1500, "direction": 1, "leverage": 2},
        ]

class TestStrategyB(BaseStrategy):
    def generate_orders(self):
        return [
            {"symbol": "BTCUSDT", "size": 0.02, "price": 25100, "direction": -1, "leverage": 2},
            {"symbol": "ETHUSDT", "size": 0.05, "price": 1490, "direction": -1, "leverage": 2},
        ]

# -------------------------------
# Тест функция
# -------------------------------
def run_multi_strategy_test():
    grsm = GlobalRiskStateManager()

    # Стартираме стратегиите
    strat_a = TestStrategyA("StrategyA", grsm)
    strat_b = TestStrategyB("StrategyB", grsm)

    # Използваме thread-ове за симулация на паралелни стратегии
    t1 = threading.Thread(target=lambda: print("[A]", strat_a.run()))
    t2 = threading.Thread(target=lambda: print("[B]", strat_b.run()))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Финален snapshot
    snapshot = grsm.shadow_ledger.get_snapshot()
    print("\n[GRSM TEST] Final snapshot:", snapshot)

    # Проверка на replay
    grsm.replay_engine.replay(grsm.shadow_ledger)
    snapshot_after_replay = grsm.shadow_ledger.get_snapshot()
    print("\n[GRSM TEST] Snapshot after replay:", snapshot_after_replay)

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    run_multi_strategy_test()
