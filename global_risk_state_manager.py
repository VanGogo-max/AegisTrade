# core/risk/global_risk_state_manager.py

from core.risk.shadow_ledger import ShadowLedger
from core.risk.risk_rules_engine import RiskRulesEngine
from core.risk.event_bus import EventBus
from core.risk.replay_engine import ReplayEngine
from enum import Enum, auto
from threading import RLock

class GRSMState(Enum):
    INIT = auto()
    NORMAL = auto()
    RISK_LOCK = auto()
    EMERGENCY = auto()
    SHUTDOWN = auto()

class GlobalRiskStateManager:
    def __init__(self):
        self.state = GRSMState.INIT
        self.shadow_ledger = ShadowLedger()
        self.risk_engine = RiskRulesEngine(max_leverage=5.0)
        self.event_bus = EventBus()
        self.replay_engine = ReplayEngine()
        self.lock = RLock()
        self.state = GRSMState.NORMAL

    # -------------------------------
    # EMERGENCY / fail-safe
    # -------------------------------
    def emergency_freeze(self, reason=""):
        self.state = GRSMState.EMERGENCY
        print(f"[EMERGENCY] Trading frozen: {reason}")

    def check_circuit_breakers(self, sim_account):
        # Пример: прекомерен used_margin
        if sim_account["used_margin"] > 1.5 * sim_account["available_margin"]:
            self.emergency_freeze("Circuit breaker triggered: margin > 150%")
            return True
        return False

    # -------------------------------
    # Тристепенна проверка + fail-safe
    # -------------------------------
    def process_order(self, order):
        with self.lock:
            # Step 1: simulate
            sim_account, sim_positions = self.shadow_ledger.simulate_order(order)

            # Step 1a: fail-safe check
            if self.check_circuit_breakers(sim_account):
                return {"status": "REJECTED", "reason": "EMERGENCY"}

            # Step 2: validate
            decision = self.risk_engine.evaluate(sim_account, sim_positions, order)
            if decision != "ALLOW":
                return {"status": "REJECTED", "reason": decision}

            # Step 3: commit
            self.shadow_ledger.commit(sim_account, sim_positions)

            # Step 4: log event for replay
            self.replay_engine.log_event(order, pre_hash="pre", post_hash="post")

            # Step 5: emit event for async processing
            self.event_bus.emit({"type": "ORDER_COMMITTED", "order": order})

            return {"status": "ACCEPTED"}


# -------------------------------
# Тест / пример за работа
# -------------------------------
if __name__ == "__main__":
    grsm = GlobalRiskStateManager()

    # Приемлив ордер
    order1 = {"symbol": "BTCUSDT", "size": 0.1, "price": 25000, "direction": 1, "leverage": 2}
    print("Order1 result:", grsm.process_order(order1))

    # Ордер с прекомерен leverage
    order2 = {"symbol": "BTCUSDT", "size": 1.0, "price": 25000, "direction": 1, "leverage": 50}
    print("Order2 result:", grsm.process_order(order2))

    # Snapshot след commit
    snapshot = grsm.shadow_ledger.get_snapshot()
    print("Snapshot:", snapshot)

    # Проверка EMERGENCY
    big_order = {"symbol": "BTCUSDT", "size": 10, "price": 25000, "direction": 1, "leverage": 2}
    print("Big order result:", grsm.process_order(big_order))
