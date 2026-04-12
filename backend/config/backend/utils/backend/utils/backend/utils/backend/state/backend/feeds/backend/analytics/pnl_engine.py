"""
AegisTrade — PnL Engine
"""
from __future__ import annotations
import math
from typing import List, Dict

from backend.utils.logger import get_logger

log = get_logger(__name__)


class PnLEngine:

    @staticmethod
    def win_rate(trades: List[dict]) -> float:
        if not trades:
            return 0.0
        wins = sum(1 for t in trades if t["pnl"] > 0)
        return wins / len(trades)

    @staticmethod
    def profit_factor(trades: List[dict]) -> float:
        gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
        gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    @staticmethod
    def total_pnl(trades: List[dict]) -> float:
        return sum(t["pnl"] for t in trades)

    @staticmethod
    def max_drawdown(equity_curve: List[float]) -> float:
        if len(equity_curve) < 2:
            return 0.0
        peak = equity_curve[0]
        max_dd = 0.0
        for v in equity_curve:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        return max_dd

    @staticmethod
    def sharpe_ratio(returns: List[float], rf: float = 0.0) -> float:
        if len(returns) < 2:
            return 0.0
        n = len(returns)
        mean = sum(returns) / n
        variance = sum((r - mean) ** 2 for r in returns) / (n - 1)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        bars_per_year = 365 * 24 * 4
        return ((mean - rf) / std) * math.sqrt(bars_per_year)

    def full_report(
        self,
        trades: List[dict],
        starting_balance: float,
    ) -> dict:
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "max_drawdown_pct": 0.0,
                "sharpe_ratio": 0.0,
                "avg_pnl_per_trade": 0.0,
            }

        pnl_list = [t["pnl"] for t in trades]
        equity = starting_balance
        equity_curve = [equity]
        returns = []
        for pnl in pnl_list:
            returns.append(pnl / equity if equity else 0)
            equity += pnl
            equity_curve.append(equity)

        return {
            "total_trades": len(trades),
            "total_pnl": round(self.total_pnl(trades), 4),
            "win_rate": round(self.win_rate(trades), 4),
            "profit_factor": round(self.profit_factor(trades), 4),
            "max_drawdown_pct": round(self.max_drawdown(equity_curve) * 100, 2),
            "sharpe_ratio": round(self.sharpe_ratio(returns), 4),
            "avg_pnl_per_trade": round(self.total_pnl(trades) / len(trades), 4),
        }

    def by_symbol(self, trades: List[dict]) -> Dict[str, dict]:
        groups: Dict[str, List[dict]] = {}
        for t in trades:
            groups.setdefault(t["symbol"], []).append(t)
        return {sym: self.full_report(g, 0) for sym, g in groups.items()}

    def by_strategy(self, trades: List[dict]) -> Dict[str, dict]:
        groups: Dict[str, List[dict]] = {}
        for t in trades:
            groups.setdefault(t["strategy"], []).append(t)
        return {s: self.full_report(g, 0) for s, g in groups.items()}
