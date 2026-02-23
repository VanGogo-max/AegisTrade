import math
import statistics
from typing import List, Dict, Any


class PerformanceAnalytics:
    """
    Анализ на performance на стратегии и портфейл.
    """

    def __init__(self):
        self.trades: List[Dict[str, Any]] = []

    # -----------------------------
    # Data
    # -----------------------------

    def add_trade(self, trade: Dict[str, Any]) -> None:
        """
        trade example:
        {
            "symbol": "BTC",
            "pnl": 120.5,
            "return_pct": 0.012,
            "duration": 340,
            "strategy": "trend_follow"
        }
        """
        self.trades.append(trade)

    def reset(self):
        self.trades = []

    # -----------------------------
    # Basic metrics
    # -----------------------------

    def total_trades(self) -> int:
        return len(self.trades)

    def total_pnl(self) -> float:
        return sum(t["pnl"] for t in self.trades)

    def win_rate(self) -> float:

        if not self.trades:
            return 0.0

        wins = [t for t in self.trades if t["pnl"] > 0]

        return len(wins) / len(self.trades)

    def average_trade(self) -> float:

        if not self.trades:
            return 0.0

        return self.total_pnl() / len(self.trades)

    # -----------------------------
    # Profit metrics
    # -----------------------------

    def profit_factor(self) -> float:

        gross_profit = sum(t["pnl"] for t in self.trades if t["pnl"] > 0)
        gross_loss = abs(sum(t["pnl"] for t in self.trades if t["pnl"] < 0))

        if gross_loss == 0:
            return float("inf")

        return gross_profit / gross_loss

    def expectancy(self) -> float:

        if not self.trades:
            return 0.0

        wins = [t["pnl"] for t in self.trades if t["pnl"] > 0]
        losses = [t["pnl"] for t in self.trades if t["pnl"] <= 0]

        if not wins:
            return statistics.mean(losses)

        if not losses:
            return statistics.mean(wins)

        win_rate = len(wins) / len(self.trades)
        avg_win = statistics.mean(wins)
        avg_loss = abs(statistics.mean(losses))

        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    # -----------------------------
    # Risk metrics
    # -----------------------------

    def returns_series(self) -> List[float]:

        return [t["return_pct"] for t in self.trades]

    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:

        returns = self.returns_series()

        if len(returns) < 2:
            return 0.0

        mean_return = statistics.mean(returns)
        std = statistics.stdev(returns)

        if std == 0:
            return 0.0

        return (mean_return - risk_free_rate) / std

    def sortino_ratio(self) -> float:

        returns = self.returns_series()

        if len(returns) < 2:
            return 0.0

        mean_return = statistics.mean(returns)

        downside = [r for r in returns if r < 0]

        if not downside:
            return float("inf")

        downside_std = statistics.stdev(downside)

        if downside_std == 0:
            return float("inf")

        return mean_return / downside_std

    # -----------------------------
    # Drawdown
    # -----------------------------

    def equity_curve(self) -> List[float]:

        equity = 0
        curve = []

        for t in self.trades:
            equity += t["pnl"]
            curve.append(equity)

        return curve

    def max_drawdown(self) -> float:

        curve = self.equity_curve()

        if not curve:
            return 0.0

        peak = curve[0]
        max_dd = 0.0

        for value in curve:

            if value > peak:
                peak = value

            dd = peak - value

            if dd > max_dd:
                max_dd = dd

        return max_dd

    # -----------------------------
    # Strategy breakdown
    # -----------------------------

    def strategy_stats(self) -> Dict[str, Dict[str, float]]:

        stats: Dict[str, List[Dict[str, Any]]] = {}

        for t in self.trades:

            strategy = t.get("strategy", "unknown")

            if strategy not in stats:
                stats[strategy] = []

            stats[strategy].append(t)

        result = {}

        for strat, trades in stats.items():

            pnl = sum(t["pnl"] for t in trades)
            wins = len([t for t in trades if t["pnl"] > 0])

            result[strat] = {
                "trades": len(trades),
                "pnl": pnl,
                "win_rate": wins / len(trades)
            }

        return result

    # -----------------------------
    # Full report
    # -----------------------------

    def report(self) -> Dict[str, Any]:

        return {
            "total_trades": self.total_trades(),
            "total_pnl": self.total_pnl(),
            "win_rate": self.win_rate(),
            "profit_factor": self.profit_factor(),
            "expectancy": self.expectancy(),
            "sharpe": self.sharpe_ratio(),
            "sortino": self.sortino_ratio(),
            "max_drawdown": self.max_drawdown(),
            "average_trade": self.average_trade(),
            "strategies": self.strategy_stats()
        }
