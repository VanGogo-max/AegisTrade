from typing import Dict, List
import time


class ExecutionMonitor:

    def __init__(self):
        self.execution_history: List[Dict] = []

    # ============================================================
    # RECORD EXECUTION
    # ============================================================

    def record_execution(
        self,
        symbol: str,
        side: str,
        expected_price: float,
        aggregated_result: Dict,
    ) -> Dict:

        """
        aggregated_result expected:
        {
            "total_filled_size": float,
            "weighted_avg_price": float,
            "total_fees": float,
            "exchanges_used": [...]
        }
        """

        actual_price = aggregated_result.get("weighted_avg_price", 0.0)
        filled_size = aggregated_result.get("total_filled_size", 0.0)

        slippage = self._calculate_slippage(
            expected_price,
            actual_price,
        )

        execution_report = {
            "timestamp": time.time(),
            "symbol": symbol,
            "side": side,
            "filled_size": filled_size,
            "expected_price": expected_price,
            "actual_price": actual_price,
            "slippage": slippage,
            "fees": aggregated_result.get("total_fees", 0.0),
            "exchanges": aggregated_result.get("exchanges_used", []),
        }

        self.execution_history.append(execution_report)

        return execution_report

    # ============================================================
    # METRICS
    # ============================================================

    def _calculate_slippage(
        self,
        expected_price: float,
        actual_price: float,
    ) -> float:

        if expected_price == 0:
            return 0.0

        return abs((actual_price - expected_price) / expected_price)

    def average_slippage(self, symbol: str = None) -> float:

        relevant = self.execution_history

        if symbol:
            relevant = [
                e for e in self.execution_history
                if e["symbol"] == symbol
            ]

        if not relevant:
            return 0.0

        return sum(e["slippage"] for e in relevant) / len(relevant)

    def max_slippage(self, symbol: str = None) -> float:

        relevant = self.execution_history

        if symbol:
            relevant = [
                e for e in self.execution_history
                if e["symbol"] == symbol
            ]

        if not relevant:
            return 0.0

        return max(e["slippage"] for e in relevant)

    def execution_summary(self) -> Dict:

        if not self.execution_history:
            return {
                "total_executions": 0
            }

        total_slippage = sum(e["slippage"] for e in self.execution_history)
        total_fees = sum(e["fees"] for e in self.execution_history)

        return {
            "total_executions": len(self.execution_history),
            "average_slippage": total_slippage / len(self.execution_history),
            "total_fees": total_fees,
        }
