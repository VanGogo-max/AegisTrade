from dataclasses import dataclass
from typing import List, Dict
from backend.backtest.backtest_engine import BacktestEngine


@dataclass
class WalkForwardConfig:
    train_window: int = 500
    test_window: int = 200
    step_size: int = 200


class WalkForwardEngine:

    def __init__(
        self,
        backtest_engine: BacktestEngine,
        config: WalkForwardConfig,
    ):
        self.backtest_engine = backtest_engine
        self.config = config

    # -------------------------------------------------
    # MAIN ENTRY
    # -------------------------------------------------
    def run(
        self,
        prices: List[float],
        signals_generator,
    ) -> Dict:

        results = []
        start = 0

        while start + self.config.train_window + self.config.test_window <= len(prices):

            train_end = start + self.config.train_window
            test_end = train_end + self.config.test_window

            train_prices = prices[start:train_end]
            test_prices = prices[train_end:test_end]

            # Strategy generates signals using training data
            signals = signals_generator(train_prices, test_prices)

            metrics = self.backtest_engine.run(
                test_prices,
                signals
            )

            results.append(metrics)

            start += self.config.step_size

        return self._aggregate_results(results)

    # -------------------------------------------------
    # AGGREGATE METRICS
    # -------------------------------------------------
    def _aggregate_results(self, results: List[Dict]) -> Dict:

        if not results:
            return {}

        avg_return = sum(r["total_return"] for r in results) / len(results)
        avg_sharpe = sum(r["sharpe_ratio"] for r in results) / len(results)
        avg_drawdown = sum(r["max_drawdown"] for r in results) / len(results)
        approval_rate = sum(1 for r in results if r["approved"]) / len(results)

        return {
            "avg_return": avg_return,
            "avg_sharpe": avg_sharpe,
            "avg_drawdown": avg_drawdown,
            "approval_rate": approval_rate,
            "segments_tested": len(results),
        }
