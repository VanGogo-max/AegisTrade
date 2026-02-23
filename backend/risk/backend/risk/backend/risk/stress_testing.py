"""
Stress Testing Engine

Simulates extreme market scenarios and estimates portfolio impact.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Position:
    symbol: str
    size: float
    price: float


@dataclass
class StressScenario:
    name: str
    price_shocks: Dict[str, float]  # percentage change


class StressEngine:

    def __init__(self):

        self.positions: Dict[str, Position] = {}
        self.scenarios: List[StressScenario] = []

    # ---------------------------------------------------
    # Portfolio
    # ---------------------------------------------------

    def update_position(
        self,
        symbol: str,
        size: float,
        price: float,
    ):

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
    # Scenario management
    # ---------------------------------------------------

    def add_scenario(
        self,
        name: str,
        price_shocks: Dict[str, float],
    ):

        """
        price_shocks example:
        {"BTC": -0.30, "ETH": -0.40}
        """

        self.scenarios.append(
            StressScenario(name, price_shocks)
        )

    # ---------------------------------------------------
    # Simulation
    # ---------------------------------------------------

    def run(self):

        results = []

        base_value = self.portfolio_value()

        for scenario in self.scenarios:

            stressed_value = 0.0

            for symbol, pos in self.positions.items():

                shock = scenario.price_shocks.get(symbol, 0)

                stressed_price = pos.price * (1 + shock)

                stressed_value += pos.size * stressed_price

            pnl = stressed_value - base_value

            results.append({
                "scenario": scenario.name,
                "portfolio_value": stressed_value,
                "pnl": pnl,
            })

        return results

    # ---------------------------------------------------
    # Worst case
    # ---------------------------------------------------

    def worst_case_loss(self):

        results = self.run()

        worst = min(results, key=lambda x: x["pnl"])

        return worst
