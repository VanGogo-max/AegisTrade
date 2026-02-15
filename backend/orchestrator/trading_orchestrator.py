from typing import Dict, Any
import asyncio

from backend.market_data.market_router import MarketRouter
from backend.ai.strategy_selector import StrategySelector
from backend.risk.risk_engine import RiskEngine
from backend.risk.volatility_controller import VolatilityController
from backend.portfolio.portfolio_optimizer import PortfolioOptimizer
from backend.portfolio.drawdown_guard import DrawdownGuard
from backend.execution.binance_futures_executor import BinanceFuturesExecutor


class TradingOrchestrator:
    """
    Central brain of the trading system.
    Coordinates AI, risk, portfolio and execution.
    """

    def __init__(self):
        self.market_router = MarketRouter()
        self.strategy_selector = StrategySelector()
        self.risk_engine = RiskEngine()
        self.volatility_controller = VolatilityController()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.drawdown_guard = DrawdownGuard()
        self.executor = BinanceFuturesExecutor()

    async def process_symbol(
        self,
        symbol: str,
        account_state: Dict[str, Any]
    ) -> Dict[str, Any]:

        # 1️⃣ Market data
        market_state = await self.market_router.get_market_state(symbol)

        # 2️⃣ AI selects best strategy
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

        # signal format expected:
        # {
        #   "side": "BUY" / "SELL",
        #   "size": float,
        #   "confidence": float
        # }

        # 4️⃣ Volatility-adjusted position sizing
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

        # 6️⃣ Portfolio optimization check
        if not self.portfolio_optimizer.validate_allocation(
            symbol=symbol,
            signal=signal,
            account_state=account_state
        ):
            return {"status": "portfolio_rejected"}

        # 7️⃣ Global drawdown guard
        if not self.drawdown_guard.allow_trading(account_state):
            return {"status": "drawdown_lock"}

        # 8️⃣ Execute order
        order_response = await self.executor.place_order(
            symbol=symbol,
            side=signal["side"],
            quantity=signal["size"],
            order_type="MARKET"
        )

        return {
            "status": "executed",
            "strategy": strategy.__class__.__name__,
            "order": order_response
        }

    async def run_cycle(
        self,
        symbols: list,
        account_state: Dict[str, Any]
    ) -> Dict[str, Any]:

        results = {}

        tasks = [
            self.process_symbol(symbol, account_state)
            for symbol in symbols
        ]

        responses = await asyncio.gather(*tasks)

        for symbol, result in zip(symbols, responses):
            results[symbol] = result

        return results
