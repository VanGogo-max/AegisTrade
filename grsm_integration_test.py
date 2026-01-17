# grsm_integration_test.py
# Integration tests for GRSM
# Tests full flow: RiskMonitor -> StrategyManager -> BatchOptimizer -> ExecutionEngine

import time

from core.risk_monitor import RiskMonitor, RiskLimits
from core.execution_engine import ExecutionEngine
from core.batch_optimizer import BatchOptimizer
from core.strategy_manager import StrategyManager
from core.base_strategy import BaseStrategy


class DummyStrategy(BaseStrategy):
    """
    Simple test strategy generating deterministic orders
    """
    def generate_orders(self):
        return [
            {"symbol": "BTCUSDT", "size": 0.01, "price": 25000, "direction": 1},
            {"symbol": "ETHUSDT", "size": 0.1, "price": 1800, "direction": -1}
        ]


def run_integration_test():
    print("Starting GRSM integration test...")

    # Initialize core components
    risk_limits = RiskLimits(max_drawdown_pct=0.5, max_daily_loss_pct=0.3)
    risk_monitor = RiskMonitor(risk_limits)
    risk_monitor.initialize(starting_equity=100000.0)

    execution_engine = ExecutionEngine()
    batch_optimizer = BatchOptimizer(order_router=None)  # We'll attach order_router later

    # Temporary OrderRouter for testing
    from core.order_router import OrderRouter
    order_router = OrderRouter(risk_monitor, risk_engine=risk_monitor, execution_engine=execution_engine)
    batch_optimizer.order_router = order_router

    strategy_manager = StrategyManager(batch_optimizer, risk_monitor)

    # Register dummy strategy
    dummy_strategy = DummyStrategy(name="DummyStrategy")
    strategy_manager.register_strategy(dummy_strategy)

    # Start strategies
    strategy_manager.start_all()

    # Run for short time
    time.sleep(2)

    # Flush any remaining orders
    batch_optimizer.flush_all()

    # Check RiskMonitor state
    snapshot = {
        "equity": risk_monitor.state.equity,
        "daily_pnl": risk_monitor.state.daily_pnl,
        "open_exposure": risk_monitor.state.open_exposure
    }
    print("Final RiskMonitor snapshot:", snapshot)

    print("GRSM integration test completed.")


if __name__ == "__main__":
    run_integration_test()
