import asyncio
from typing import Dict, List, Any
from datetime import datetime

from backend.ai.strategy_selector import StrategySelector
from backend.risk.risk_engine import RiskEngine
from backend.risk.volatility_controller import VolatilityController
from backend.portfolio.portfolio_optimizer import PortfolioOptimizer
from backend.portfolio.drawdown_guard import DrawdownGuard


class TradingOrchestrator:
    """
    Central execution brain.

    Coordinates:
    - Strategy selection
    - Portfolio optimization
    - Risk filtering
    - Volatility adjustment
    - Drawdown protection
    """

    def __init__(
        self,
        strategy_selector: StrategySelector,
        risk_engine: RiskEngine,
        volatility_controller: VolatilityController,
        portfolio_optimizer: PortfolioOptimizer,
        drawdown_guard: DrawdownGuard,
    ):
        self.strategy_selector = strategy_selector
        self.risk_engine = risk_engine
        self.volatility_controller = volatility_controller
        self.portfolio_optimizer = portfolio_optimizer
        self.drawdown_guard = drawdown_guard

    async def process_market_data(
        self,
        symbol: str,
        market_state: Dict[str, Any],
        account_state: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        Main processing pipeline.
        """

        # 1️⃣ Strategy selection
        strategy_signal = self.strategy_selector.select_strategy(
            symbol=symbol,
            market_state=market_state,
        )

        if strategy_signal is None:
            return None

        # 2️⃣ Portfolio optimization
        optimized_signal = self.portfolio_optimizer.optimize(
            symbol=symbol,
            signal=strategy_signal,
            portfolio_state=account_state,
        )

        if optimized_signal is None:
            return None

        # 3️⃣ Risk engine validation
        risk_checked_signal = self.risk_engine.validate_signal(
            symbol=symbol,
            signal=optimized_signal,
            account_state=account_state,
        )

        if risk_checked_signal is None:
            return None

        # 4️⃣ Volatility control
        vol_adjusted_signal = self.volatility_controller.adjust_position(
            symbol=symbol,
            signal=risk_checked_signal,
            market_state=market_state,
        )

        if vol_adjusted_signal is None:
            return None

        # 5️⃣ Drawdown guard
        if self.drawdown_guard.is_trading_blocked(account_state):
            return None

        return {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "signal": vol_adjusted_signal,
        }
