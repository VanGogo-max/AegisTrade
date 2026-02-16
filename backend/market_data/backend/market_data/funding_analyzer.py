from typing import Dict


class FundingAnalyzer:
    """
    Analyzes funding rates across DEXes
    and calculates funding advantage.
    """

    def __init__(self):
        pass

    @staticmethod
    def calculate_expected_funding_cost(
        funding_rate: float,
        position_size: float,
        side: str,
    ) -> float:
        """
        funding_rate example: 0.0001 (0.01%)
        positive funding:
            longs pay
            shorts receive
        """

        if side.lower() == "long":
            return funding_rate * position_size
        else:
            return -funding_rate * position_size

    @staticmethod
    def normalize_funding_score(expected_cost: float) -> float:
        """
        Lower cost = better.
        Negative cost (receive funding) = best.
        """

        return -expected_cost

    def analyze(
        self,
        funding_rate: float,
        position_size: float,
        side: str,
    ) -> Dict:

        expected_cost = self.calculate_expected_funding_cost(
            funding_rate,
            position_size,
            side,
        )

        funding_score = self.normalize_funding_score(expected_cost)

        return {
            "funding_rate": funding_rate,
            "expected_cost": expected_cost,
            "funding_score": funding_score,
        }
