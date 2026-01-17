# core/risk/global_risk_state_manager.py
from threading import RLock
from core.risk.shadow_ledger import ShadowLedger
from core.risk.risk_rules_engine import RiskRulesEngine
from core.risk.event_bus import EventBus
from core.risk.replay_engine import ReplayEngine
from enum import Enum, auto

class GRSMState(Enum):
    INIT = auto()
    NORMAL = auto()
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

        # стартираме async обработка на събития
        self.event_bus.start_processing(self._handle_event)

    # -------------------------------
    # Async event handler
    # -------------------------------
    def _handle_event(self, event):
        print("[EventBus] Handling event:", event)

    # -------------------------------
    # EMERGENCY / fail-safe
    # -------------------------------
    def emergency_freeze(self, reason=""):
        self.state = GRSMState.EMERGENCY
        print(f"[EMERGENCY] Trading frozen: {reason}")

    def check_circuit_breakers(self, sim_account):
        if sim_account["used_margin"] > 1.5 * sim_account["available_margin"]:
            self.emergency_freeze("Circuit breaker triggered")
            return True
        return False

    # -------------------------------
    # Batch / single order processing
    # -------------------------------
    def process_orders_batch(self, orders):
        """
        Batch обработка на ордери
        """
        results = []
        with self.lock:
            for order in orders:
                sim_account, sim_positions = self.shadow_ledger.simulate_order(order)
                if self.check_circuit_breakers(sim_account):
                    results.append({"status": "REJECTED", "reason": "EMERGENCY"})
                    continue

                decision = self.risk_engine.evaluate(sim_account, sim_positions, order)
                if decision != "ALLOW":
                    results.append({"status": "REJECTED", "reason": decision})
                    continue

                # Commit
                self.shadow_ledger.commit(sim_account, sim_positions)

                # Log за replay
                self.replay_engine.log_event(order, pre_hash="pre", post_hash="post")

                # Emit event
                self.event_bus.emit({"type": "ORDER_COMMITTED", "order": order})

                results.append({"status": "ACCEPTED"})
        return results
