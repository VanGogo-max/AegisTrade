from dataclasses import dataclass
from typing import Dict, Optional
import math


@dataclass
class RiskConfig:
    max_risk_per_trade: float = 0.01  # 1% риск
    max_daily_drawdown: float = 0.05  # 5% дневен лимит
    leverage: int = 5
    use_isolated_margin: bool = True


class FuturesPositionManager:
    def __init__(self, config: RiskConfig):
        self.config = config
        self.daily_loss = 0.0

    # -----------------------------
    # POSITION SIZE CALCULATION
    # -----------------------------
    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_price: float,
    ) -> float:
        """
        Position sizing based on fixed % risk model.
        """
        risk_amount = balance * self.config.max_risk_per_trade
        stop_distance = abs(entry_price - stop_price)

        if stop_distance == 0:
            raise ValueError("Stop distance cannot be zero")

        position_size = risk_amount / stop_distance
        leveraged_size = position_size * self.config.leverage

        return round(leveraged_size, 6)

    # -----------------------------
    # STOP LOSS CALCULATION
    # -----------------------------
    def calculate_stop_loss(
        self,
        entry_price: float,
        direction: str,
        atr: float,
        multiplier: float = 1.5,
    ) -> float:
        """
        ATR-based stop loss.
        """
        if direction == "LONG":
            return round(entry_price - atr * multiplier, 6)
        elif direction == "SHORT":
            return round(entry_price + atr * multiplier, 6)
        else:
            raise ValueError("Direction must be LONG or SHORT")

    # -----------------------------
    # TAKE PROFIT CALCULATION
    # -----------------------------
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_price: float,
        risk_reward_ratio: float = 2.0,
    ) -> float:
        """
        Risk/Reward based TP.
        """
        risk = abs(entry_price - stop_price)
        reward = risk * risk_reward_ratio

        if entry_price > stop_price:
            return round(entry_price + reward, 6)
        else:
            return round(entry_price - reward, 6)

    # -----------------------------
    # DAILY DRAWDOWN CONTROL
    # -----------------------------
    def update_daily_loss(self, loss: float):
        self.daily_loss += loss

    def can_trade(self) -> bool:
        return self.daily_loss < self.config.max_daily_drawdown
