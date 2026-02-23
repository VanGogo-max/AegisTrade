"""
Value-at-Risk Engine

Supports:
• Historical Simulation
• Variance-Covariance (Parametric)
• Monte Carlo

Portfolio-based risk estimation.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class Position:
    symbol: str
    size: float
    price: float


class VaREngine:

    def __init__(self, confidence: float = 0.99):
        self.confidence = confidence
        self.positions: Dict[str, Position] = {}

    # ---------------------------------------------------
    # Portfolio management
    # ---------------------------------------------------

    def update_position(self, symbol: str, size: float, price: float):
        self.positions[symbol] = Position(symbol, size, price)

    def remove_position(self, symbol: str):
        if symbol in self.positions:
            del self.positions[symbol]

    def portfolio_value(self) -> float:

        value = 0.0

        for p in self.positions.values():
            value += p.size * p.price

        return value

    # ---------------------------------------------------
    # Historical VaR
    # ---------------------------------------------------

    def historical_var(
        self,
        returns: Dict[str, List[float]],
    ) -> float:
        """
        returns = {symbol: [daily returns]}
        """

        portfolio_returns = []

        length = min(len(r) for r in returns.values())

        for i in range(length):

            r = 0.0

            for symbol, series in returns.items():

                if symbol not in self.positions:
                    continue

                pos = self.positions[symbol]

                r += pos.size * pos.price * series[i]

            portfolio_returns.append(r)

        percentile = np.percentile(
            portfolio_returns,
            (1 - self.confidence) * 100,
        )

        return abs(percentile)

    # ---------------------------------------------------
    # Variance Covariance
    # ---------------------------------------------------

    def parametric_var(
        self,
        returns: Dict[str, List[float]],
    ) -> float:

        symbols = [
            s for s in returns
            if s in self.positions
        ]

        if not symbols:
            return 0.0

        matrix = np.array([returns[s] for s in symbols])

        cov = np.cov(matrix)

        weights = np.array([
            self.positions[s].size * self.positions[s].price
            for s in symbols
        ])

        portfolio_var = weights @ cov @ weights.T

        z = self._z_score(self.confidence)

        return z * math.sqrt(portfolio_var)

    # ---------------------------------------------------
    # Monte Carlo
    # ---------------------------------------------------

    def monte_carlo_var(
        self,
        returns: Dict[str, List[float]],
        simulations: int = 10000,
    ) -> float:

        symbols = [
            s for s in returns
            if s in self.positions
        ]

        if not symbols:
            return 0.0

        means = [
            np.mean(returns[s])
            for s in symbols
        ]

        cov = np.cov([returns[s] for s in symbols])

        weights = np.array([
            self.positions[s].size * self.positions[s].price
            for s in symbols
        ])

        results = []

        for _ in range(simulations):

            simulated = np.random.multivariate_normal(
                means,
                cov,
            )

            pnl = weights @ simulated

            results.append(pnl)

        percentile = np.percentile(
            results,
            (1 - self.confidence) * 100,
        )

        return abs(percentile)

    # ---------------------------------------------------
    # Helpers
    # ---------------------------------------------------

    def _z_score(self, confidence: float) -> float:

        table = {
            0.90: 1.28,
            0.95: 1.65,
            0.99: 2.33,
        }

        return table.get(confidence, 2.33)
