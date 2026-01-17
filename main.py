# main.py
# Entry point for GRSM
# Initializes and runs the full system

import time
from core.config import Config
from core.risk_monitor import RiskMonitor, RiskLimits
from core.execution_engine import ExecutionEngine
from core.batch_optimizer import BatchOptimizer
from core.order_router import OrderRouter
from core.strategy_manager import StrategyManager
from core.base_strategy import BaseStrategy
from core.global_risk_state_manager import GlobalRiskStateManager
from core.lock_manager import LockManager
from core.health_checker import HealthChecker
from core.state_persistence import StatePersistence
from core.replay_engine import ReplayEngine
from core.event_bus import EventBus

# ----------------- Dummy Strategy for startup -----------------
class DummyStrategy(BaseStrategy):
    def generate_orders(self):
        return [
            {"symbol": "BTCUSDT", "size": 0.01, "price": 25000, "direction": 1},
            {"symbol": "ETHUSDT", "size": 0.1, "price": 1800, "direction": -1}
        ]

# ----------------- Initialize core components -----------------
risk_limits = RiskLimits(
    max_drawdown_pct=Config.MAX_DRAWDOWN_PCT,
    max_daily_loss_pct=Config.MAX_DAILY_LOSS_PCT,
    max_leverage=Config.MAX_LEVERAGE,
    max_position_pct=Config.MAX_POSITION_PCT,
    max_correlated_exposure_pct=Config.MAX_CORRELATED_EXPOSURE_PCT
)
risk_monitor = RiskMonitor(risk_limits)
risk_monitor.initialize(starting_equity=Config.DEFAULT_STARTING_BALANCE)

execution_engine = ExecutionEngine()
lock_manager = LockManager()
global_risk_state = GlobalRiskStateManager(risk_monitor, execution_engine.shadow_ledger, lock_manager)
state_persistence = StatePersistence()
event_bus = EventBus()

# ----------------- Order Routing & Batch Optimizer -----------------
order_router = OrderRouter(risk_monitor, risk_engine=risk_monitor, execution_engine=execution_engine)
batch_optimizer = BatchOptimizer(order_router, max_batch_size=Config.MAX_BATCH_SIZE)

# ----------------- Strategy Manager -----------------
strategy_manager = StrategyManager(batch_optimizer, risk_monitor)
dummy_strategy = DummyStrategy(name="DummyStrategy")
strategy_manager.register_strategy(dummy_strategy)

# ----------------- Health Checker -----------------
health_checker = HealthChecker(risk_monitor, execution_engine, batch_optimizer, strategy_manager, interval_sec=Config.HEALTH_CHECK_INTERVAL_SEC)
health_checker.start()

# ----------------- Replay Engine -----------------
replay_engine = ReplayEngine(state_persistence, execution_engine.shadow_ledger, risk_monitor)
replay_engine.replay()  # restore last known state

# ----------------- Start strategies -----------------
strategy_manager.start_all()

# ----------------- Main Loop -----------------
try:
    while not risk_monitor.is_halted():
        time.sleep(1)
        # Optionally persist snapshots every few seconds
        snapshot = {
            "account": execution_engine.shadow_ledger.account.copy(),
            "positions": {k:v.copy() for k,v in execution_engine.shadow_ledger.positions.items()},
            "risk_state": global_risk_state.get_risk_snapshot()
        }
        state_persistence.save_snapshot(snapshot)
except KeyboardInterrupt:
    print("Received exit signal, shutting down...")
finally:
    health_checker.stop()
    batch_optimizer.flush_all()
    print("GRSM system shutdown completed.")
