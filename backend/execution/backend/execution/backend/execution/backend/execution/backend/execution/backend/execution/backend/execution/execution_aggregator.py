from typing import List, Dict


class ExecutionAggregator:

    # ------------------------------------------------
    # PUBLIC
    # ------------------------------------------------

    def aggregate(
        self,
        execution_results: List[Dict],
    ) -> Dict:
        """
        execution_results example:
        [
            {
                "exchange": "hyperliquid",
                "filled_size": 3.5,
                "avg_price": 50200,
                "fees": 12.5,
            }
        ]
        """

        total_size = 0.0
        total_cost = 0.0
        total_fees = 0.0

        exchanges_used = []

        for result in execution_results:

            filled = result.get("filled_size", 0.0)
            price = result.get("avg_price", 0.0)
            fees = result.get("fees", 0.0)

            total_size += filled
            total_cost += filled * price
            total_fees += fees

            exchanges_used.append(result.get("exchange"))

        if total_size == 0:
            return {
                "success": False,
                "reason": "No fills",
            }

        weighted_avg_price = total_cost / total_size

        return {
            "success": True,
            "total_filled_size": total_size,
            "weighted_avg_price": weighted_avg_price,
            "total_fees": total_fees,
            "effective_cost": total_cost + total_fees,
            "exchanges_used": exchanges_used,
        }

    # ------------------------------------------------
    # SLIPPAGE CALCULATION
    # ------------------------------------------------

    def calculate_slippage(
        self,
        expected_price: float,
        actual_price: float,
    ) -> float:

        if expected_price == 0:
            return 0.0

        return abs((actual_price - expected_price) / expected_price)

    # ------------------------------------------------
    # PNL IMPACT
    # ------------------------------------------------

    def estimate_pnl_impact(
        self,
        entry_price: float,
        mark_price: float,
        size: float,
        side: str,
    ) -> float:

        if side == "buy":
            return (mark_price - entry_price) * size
        else:
            return (entry_price - mark_price) * size
