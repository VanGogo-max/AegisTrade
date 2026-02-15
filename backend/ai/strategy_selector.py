from dataclasses import dataclass
from typing import Dict, Optional, List
import time


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

    def __init__(self):
        # Regime thresholds
        self.volatility_threshold = 0.02
        self.trend_threshold = 0.01
        self.volume_spike_threshold = 1.5

        # Regime memory
        self.last_strategy: Dict[str, str] = {}
        self.last_switch_time: Dict[str, float] = {}
        self.min_hold_seconds = 1800  # 30 мин

        # Correlation memory
        self.symbol_correlation: Dict[str, List[str]] = {}

        # Optional ML model placeholder
        self.ml_model = None  # later plug-in

    # --------------------------------------------------
    # PUBLIC ENTRY
    # --------------------------------------------------
    def select_strategy(
        self,
        state: MarketState,
        open_positions: Dict[str, Dict],
        portfolio_risk: float,
    ) -> StrategyDecision:

        # 1️⃣ Portfolio risk filter
        if portfolio_risk > 0.25:
            return StrategyDecision("NO_TRADE", "N/A", 0.9)

        # 2️⃣ Correlation filter
        if self._is_correlated(state.symbol, open_positions):
            return StrategyDecision("NO_TRADE", "N/A", 0.85)

        # 3️⃣ ML override (if model exists)
        if self.ml_model:
            return self._ml_decision(state)

        # 4️⃣ Rule-based fallback
        decision = self._rule_based_decision(state)

        # 5️⃣ Regime memory filter
        decision = self._apply_regime_memory(state.symbol, decision)

        return decision

    # --------------------------------------------------
    # RULE-BASED DECISION
    # --------------------------------------------------
    def _rule_based_decision(self, state: MarketState) -> StrategyDecision:

        volatility_ratio = state.atr / state.price
        trend_strength = abs(state.ema_fast - state.ema_slow) / state.price
        volume_ratio = state.volume / state.avg_volume if state.avg_volume > 0 else 0

        confidence = 0.6

        if volatility_ratio > self.volatility_threshold and trend_strength > self.trend_threshold:
            confidence = self._confidence_score(volatility_ratio, trend_strength)
            return StrategyDecision("TURTLE_BREAKOUT", "4h", confidence)

        if volatility_ratio > self.volatility_threshold and volume_ratio > self.volume_spike_threshold:
            confidence = self._confidence_score(volatility_ratio, volume_ratio)
            return StrategyDecision("MULTI_ENTRY_EXPANSION", "1h", confidence)

        if volatility_ratio < self.volatility_threshold and trend_strength < self.trend_threshold:
            confidence = 0.7
            return StrategyDecision("MEAN_REVERSION", "15m", confidence)

        return StrategyDecision("NO_TRADE", "N/A", 0.5)

    # --------------------------------------------------
    # CONFIDENCE WEIGHTING
    # --------------------------------------------------
    def _confidence_score(self, metric1: float, metric2: float) -> float:
        raw_score = (metric1 + metric2) / 2
        return min(max(raw_score * 10, 0.5), 0.95)

    # --------------------------------------------------
    # REGIME MEMORY
    # --------------------------------------------------
    def _apply_regime_memory(
        self,
        symbol: str,
        decision: StrategyDecision,
    ) -> StrategyDecision:

        now = time.time()

        if symbol not in self.last_strategy:
            self._store_regime(symbol, decision.strategy_name, now)
            return decision

        if decision.strategy_name != self.last_strategy[symbol]:
            time_since_switch = now - self.last_switch_time[symbol]

            if time_since_switch < self.min_hold_seconds:
                # block switch
                return StrategyDecision(
                    self.last_strategy[symbol],
                    decision.timeframe,
                    decision.confidence * 0.8,
                )

            self._store_regime(symbol, decision.strategy_name, now)

        return decision

    def _store_regime(self, symbol: str, strategy: str, timestamp: float):
        self.last_strategy[symbol] = strategy
        self.last_switch_time[symbol] = timestamp

    # --------------------------------------------------
    # CORRELATION FILTER
    # --------------------------------------------------
    def _is_correlated(
        self,
        symbol: str,
        open_positions: Dict[str, Dict],
    ) -> bool:

        correlated_symbols = self.symbol_correlation.get(symbol, [])

        for open_symbol in open_positions.keys():
            if open_symbol in correlated_symbols:
                return True

        return False

    # --------------------------------------------------
    # ML DECISION (placeholder)
    # --------------------------------------------------
    def _ml_decision(self, state: MarketState) -> StrategyDecision:
        prediction = self.ml_model.predict(state)
        return StrategyDecision(
            prediction["strategy"],
            prediction["timeframe"],
            prediction["confidence"],
        )
