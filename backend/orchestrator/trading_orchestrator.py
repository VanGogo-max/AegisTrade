from typing import Dict, Any, List
import asyncio

from backend.market_data.market_router import MarketRouter
from backend.ai.strategy_selector import StrategySelector
from backend.risk.risk_engine import RiskEngine
from backend.risk.volatility_controller import VolatilityController
from backend.portfolio.portfolio_optimizer import PortfolioOptimizer
from backend.portfolio.drawdown_guard import DrawdownGuard
from backend.execution.dex_executor import DexExecutor


class DexTradingOrchestrator:
    """
    DEX-native orchestrator.
    Supports multiple decentralized perpetual exchanges.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name

        self.market_router = MarketRouter()
        self.strategy_selector = StrategySelector()
        self.risk_engine = RiskEngine()
        self.volatility_controller = VolatilityController()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.drawdown_guard = DrawdownGuard()

        self.executor = DexExecutor(exchange_name)

    async def process_symbol(
        self,
        symbol: str,
        account_state: Dict[str, Any]
    ) -> Dict[str, Any]:

        # 1️⃣ Get market data
        market_state = await self.market_router.get_market_state(
            symbol=symbol,
            exchange=self.exchange_name
        )

        # 2️⃣ AI strategy selection
        strategy = self.strategy_selector.select_strategy(
            symbol=symbol,
            market_state=market_state
        )

        if strategy is None:
            return {"status": "no_strategy"}

        # 3️⃣ Generate signal
        signal = strategy.generate_signal(market_state)

        if signal is None:
            return {"status": "no_signal"}

        # 4️⃣ Volatility-adjusted sizing
        signal = self.volatility_controller.adjust_position_size(
            symbol=symbol,
            signal=signal,
            market_state=market_state
        )

        # 5️⃣ Risk validation
        if not self.risk_engine.validate_trade(
            symbol=symbol,
            signal=signal,
            account_state=account_state
        ):
            return {"status": "risk_rejected"}

        # 6️⃣ Portfolio validation
        if not self.portfolio_optimizer.validate_allocation(
            symbol=symbol,
            signal=signal,
            account_state=account_state
        ):
            return {"status": "portfolio_rejected"}

        # 7️⃣ Drawdown guard
        if not self.drawdown_guard.allow_trading(account_state):
            return {"status": "drawdown_lock"}

        # 8️⃣ Execute on selected DEX
        order_response = await self.executor.place_order(
            symbol=symbol,
            side=signal["side"],
            size=signal["size"]
        )

        return {
            "status": "executed",
            "exchange": self.exchange_name,
            "strategy": strategy.__class__.__name__,
            "order": order_response
        }

    async def run_cycle(
        self,
        symbols: List[str],
        account_state: Dict[str, Any]
    ) -> Dict[str, Any]:

        tasks = [
            self.process_symbol(symbol, account_state)
            for symbol in symbols
        ]

        responses = await asyncio.gather(*tasks)

        return dict(zip(symbols, responses))
