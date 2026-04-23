"""
AegisTrade - PnL Engine
"""
from __future__ import annotations
from typing import List
from backend.utils.logger import get_logger

log = get_logger(__name__)


class PnLEngine:
    def full_report(self, trades: list, initial_balance: float) -> dict:
        if not trades:
            return {
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "total_trades": 0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "pnl_history": [],
            }
        wins = [t for t in trades if t.get("pnl", 0) > 0]
        losses = [t for t in trades if t.get("pnl", 0) <= 0]
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        avg_win = sum(t.get("pnl", 0) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.get("pnl", 0) for t in losses) / len(losses) if losses else 0
        history = []
        cumulative = 0.0
        for i, t in enumerate(trades):
            cumulative += t.get("pnl", 0)
            history.append({"t": str(i), "pnl": round(cumulative, 2)})
        return {
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 2),
            "total_trades": len(trades),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "pnl_history": history,
        }

    def by_symbol(self, trades: list) -> dict:
        result = {}
        for t in trades:
            sym = t.get("symbol", "unknown")
            result.setdefault(sym, 0.0)
            result[sym] += t.get("pnl", 0)
        return {k: round(v, 2) for k, v in result.items()}

    def by_strategy(self, trades: list) -> dict:
        result = {}
        for t in trades:
            strat = t.get("strategy", "unknown")
            result.setdefault(strat, 0.0)
            result[strat] += t.get("pnl", 0)
        return {k: round(v, 2) for k, v in result.items()}
