# grsm_recovery_example.py

from core.risk.global_risk_state_manager import GlobalRiskStateManager
import copy

# -------------------------------
# Стартово GRSM
# -------------------------------
grsm = GlobalRiskStateManager()

# Стартираме няколко ордера
orders = [
    {"symbol": "BTCUSDT", "size": 0.05, "price": 25000, "direction": 1, "leverage": 2},
    {"symbol": "ETHUSDT", "size": 0.1, "price": 1500, "direction": 1, "leverage": 3},
    {"symbol": "BTCUSDT", "size": 0.02, "price": 25100, "direction": -1, "leverage": 2}
]

# Commit-ва ордерите
for o in orders:
    grsm.process_orders_batch([o])

print("[Before restart] Snapshot:", grsm.shadow_ledger.get_snapshot())

# -------------------------------
# Симулираме рестарт
# -------------------------------
# 1. Съхраняваме snapshot и event_log
saved_snapshot = copy.deepcopy(grsm.shadow_ledger.get_snapshot())
saved_events = copy.deepcopy(grsm.replay_engine.event_log)

# 2. Създаваме нов GRSM instance
grsm_recovered = GlobalRiskStateManager()

# -------------------------------
# Recovery от snapshot + replay
# -------------------------------
# Възстановяваме snapshot
grsm_recovered.shadow_ledger.account = saved_snapshot["account"]
grsm_recovered.shadow_ledger.positions = saved_snapshot["positions"]

# Replay на всички събития
grsm_recovered.replay_engine.event_log = saved_events
grsm_recovered.replay_engine.replay(grsm_recovered.shadow_ledger)

print("\n[After recovery] Snapshot:", grsm_recovered.shadow_ledger.get_snapshot())
