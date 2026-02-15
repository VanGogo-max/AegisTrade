from dataclasses import dataclass
from typing import Dict, List
import math


@dataclass
class PortfolioConfig:
    max_portfolio_risk: float = 0.30
    target_volatility: float = 0.15
    max_leverage: int = 10
    min_allocation_pct: float = 0.02


class PortfolioOptimizer:

    def __init__(self, config: PortfolioConfig):
        self.config = config

    # -------------------------------------------------
    # MAIN ENTRY
    # -------------------------------------------------
    def optimize(
        self,
        capital: float,
        signals: Dict[str, Dict],
        volatility: Dict[str, float],
        correlations: Dict[str, Dict[str, float]],
    ) -> Dict[str, Dict]:

        allocations = self._risk_parity_weights(signals, volatility)

        allocations = self._correlation_adjustment(
            allocations,
            correlations
        )

        allocations = self._apply_capital_allocation(
            capital,
            allocations
        )

        return allocations

    # -------------------------------------------------
    # RISK PARITY WEIGHTING
    # -------------------------------------------------
    def _risk_parity_weights(
        self,
        signals: Dict[str, Dict],
        volatility: Dict[str, float],
    ) -> Dict[str, float]:

        inverse_vol_weights = {}
        total_inverse_vol = 0.0

        for symbol in signals.keys():
            vol = volatility.get(symbol, 0.0)
            if vol == 0:
                continue

            inv_vol = 1 / vol
            inverse_vol_weights[symbol] = inv_vol
            total_inverse_vol += inv_vol

        weights = {}
        for symbol, inv_vol in inverse_vol_weights.items():
            weights[symbol] = inv_vol / total_inverse_vol

        return weights

    # -------------------------------------------------
    # CORRELATION ADJUSTMENT
    # -------------------------------------------------
    def _correlation_adjustment(
        self,
        weights: Dict[str, float],
        correlations: Dict[str, Dict[str, float]],
    ) -> Dict[str, float]:

        adjusted_weights = weights.copy()

        for symbol_a in weights:
            for symbol_b in weights:
                if symbol_a == symbol_b:
                    continue

                corr = correlations.get(symbol_a, {}).get(symbol_b, 0.0)

                if corr > 0.7:
                    adjusted_weights[symbol_a] *= 0.8

        # renormalize
        total = sum(adjusted_weights.values())
        if total > 0:
            for symbol in adjusted_weights:
                adjusted_weights[symbol] /= total

        return adjusted_weights

    # -------------------------------------------------
    # CAPITAL ALLOCATION
    # -------------------------------------------------
    def _apply_capital_allocation(
        self,
        capital: float,
        weights: Dict[str, float],
    ) -> Dict[str, Dict]:

        allocation = {}

        for symbol, weight in weights.items():

            capital_allocated = capital * weight

            if weight < self.config.min_allocation_pct:
                continue

            allocation[symbol] = {
                "capital": capital_allocated,
                "weight": weight,
                "leverage": self._adaptive_leverage(weight)
            }

        return allocation

    # -------------------------------------------------
    # ADAPTIVE LEVERAGE
    # -------------------------------------------------
    def _adaptive_leverage(self, weight: float) -> int:

        scaled = weight * self.config.max_leverage
        leverage = max(1, min(int(round(scaled)), self.config.max_leverage))

        return leverage
