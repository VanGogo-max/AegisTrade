from typing import Dict, Any, List

from backend.risk.position_sizer import PositionSizer
from backend.risk.drawdown_guard import DrawdownGuard
from backend.risk.portfolio_risk_manager import PortfolioRiskManager


class StrategyExecutionEngine:

    def __init__(
        self,
        router,
        equity: float
    ):

        self.router = router

        self.position_sizer = PositionSizer(equity)
        self.drawdown_guard = DrawdownGuard()
        self.portfolio = PortfolioRiskManager(equity)

        self.strategies: List[Any] = []

    def register_strategy(self, strategy):
        self.strategies.append(strategy)

    def update_equity(self, equity: float):

        self.position_sizer.update_equity(equity)
        self.portfolio.update_equity(equity)

        state = self.drawdown_guard.update(equity)

        if state.trading_blocked:
            print("Trading halted due to drawdown")

    async def on_market_data(self, data: Dict):

        for strategy in self.strategies:

            signal = strategy.on_market_data(data)

            if not signal:
                continue

            if self.drawdown_guard.trading_blocked:
                return

            risk_state = self.portfolio.evaluate()

            if not risk_state.allowed:
                return

            size = self.position_sizer.calculate_position_size(
                entry_price=signal["entry"],
                stop_price=signal["stop"],
                leverage=signal.get("leverage", 1)
            )

            if not size:
                return

            await self.router.execute_order(
                symbol=signal["symbol"],
                side=signal["side"],
                size=size.size
            )
