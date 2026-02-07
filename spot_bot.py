"""
spot_bot.py

High-level coordinator for SPOT trading logic.
"""

from typing import Optional

from domain_types import MarketType, TradingPair
from position_manager import PositionManager
from risk_manager import RiskManager
from strategy_selector import StrategySelector
from strategy_base import StrategySignal


class SpotBot:
    """
    Coordinates SPOT trading by combining strategies,
    risk checks, and position management.
    """

    def __init__(
        self,
        trading_pair: TradingPair,
        position_manager: PositionManager,
        risk_manager: RiskManager,
        strategy_selector: StrategySelector,
    ) -> None:
        self.market_type = MarketType.SPOT
        self.trading_pair = trading_pair
        self.position_manager = position_manager
        self.risk_manager = risk_manager
        self.strategy_selector = strategy_selector

    def on_price_update(self, price: float) -> Optional[str]:
        """
        Processes a new price update.
        Returns position_id if a position is opened, otherwise None.
        """
        signal: Optional[StrategySignal] = self.strategy_selector.on_price_update(price)

        if signal is None or signal.side is None:
            return None

        self.risk_manager.validate_new_position(
            position_manager=self.position_manager,
            market_type=self.market_type,
            side=signal.side,
            size=1.0,
            leverage=None,
        )

        position = self.position_manager.open_position(
            market_type=self.market_type,
            trading_pair=self.trading_pair,
            side=signal.side,
            size=1.0,
            entry_price=price,
            leverage=None,
        )

        return position.position_id
