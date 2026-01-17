# core/risk/global_risk_state_manager.py

from core.risk.shadow_ledger import ShadowLedger
from core.risk.risk_rules_engine import RiskRulesEngine
from enum import Enum, auto
from threading import RLock

# -------------------------------
# GRSM State
# -------------------------------
class GRSMState(Enum):
    INIT = auto()
    NORMAL = auto()
    RISK_LOCK = auto()
    EMERGENCY = auto()
    SHUTDOWN = auto()

# -------------------------------
# Global Risk & State Manager
# -------------------------------
class GlobalRiskStateManager:
    def __init__(self):
        self.state = GRSMState.INIT
        self.shadow_ledger = ShadowLedger()
        self.risk_engine = RiskRulesEngine(max_leverage=5.0)
        self.lock = RLock()
        self.state = GRSMState.NORMAL

    def process_order(self, order):
        """
        Тристепенна проверка:
        1️⃣ Симулираме ордера
        2️⃣ Проверяваме правила
        3️⃣ Commit ако е ALLOW
        """
        with self.lock:
            # Step 1: simulate
            sim_account, sim_positions = self.shadow_ledger.simulate_order(order)

            # Step 2: validate
            decision = self.risk_engine.evaluate(sim_account, sim_positions, order)
            if decision != "ALLOW":
                return {"status": "REJECTED", "reason": decision}

            # Step 3: commit
            self.shadow_ledger.commit(sim_account, sim_positions)
            return {"status": "ACCEPTED"}


# -------------------------------
# Тест / пример за работа
# -------------------------------
if __name__ == "__main__":
    grsm = GlobalRiskStateManager()

    # Приемлив ордер
    order1 = {"symbol": "BTCUSDT", "size": 0.1, "price": 25000, "direction": 1, "leverage": 2}
    result1 = grsm.process_order(order1)
    print("Order1 result:", result1)

    # Прекомерен leverage
    order2 = {"symbol": "BTCUSDT", "size": 1.0, "price": 25000, "direction": 1, "leverage": 50}
    result2 = grsm.process_order(order2)
    print("Order2 result:", result2)

    # Проверка snapshot
    snapshot = grsm.shadow_ledger.get_snapshot()
    print("Snapshot:", snapshot)
