from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class MarketState:
    symbol: str
    price: float
    atr: float
    ema_fast: float
    ema_slow: float
    volume: float
    avg_volume: float


@dataclass
class StrategyDecision:
    strategy_name: str
    timeframe: str
    confidence: float


class StrategySelector:
    """
    Regime-based strategy selector.
    """

    def __init__(self):
        self.volatility_threshold = 0.02     # 2% ATR/Price
        self.trend_threshold = 0.01          # 1% EMA distance
        self.volume_spike_threshold = 1.5    # 150% от средния обем

    # ----------------------------------------
    # PUBLIC METHOD
    # ----------------------------------------
    def select_strategy(self, state: MarketState) -> StrategyDecision:

        volatility_ratio = state.atr / state.price
        trend_strength = abs(state.ema_fast - state.ema_slow) / state.price
        volume_ratio = state.volume / state.avg_volume if state.avg_volume > 0 else 0

        # TRENDING + HIGH VOLATILITY
        if volatility_ratio > self.volatility_threshold and trend_strength > self.trend_threshold:
            return StrategyDecision(
                strategy_name="TURTLE_BREAKOUT",
                timeframe="4h",
                confidence=0.85
            )

        # HIGH VOLATILITY + VOLUME SPIKE
        if volatility_ratio > self.volatility_threshold and volume_ratio > self.volume_spike_threshold:
            return StrategyDecision(
                strategy_name="MULTI_ENTRY_EXPANSION",
                timeframe="1h",
                confidence=0.80
            )

        # LOW VOLATILITY (RANGE)
        if volatility_ratio < self.volatility_threshold and trend_strength < self.trend_threshold:
            return StrategyDecision(
                strategy_name="MEAN_REVERSION",
                timeframe="15m",
                confidence=0.75
            )

        # DEFAULT SAFE MODE
        return StrategyDecision(
            strategy_name="NO_TRADE",
            timeframe="N/A",
            confidence=0.50
        )
