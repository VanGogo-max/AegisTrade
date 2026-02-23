"""
Performance Analytics Engine

Responsibilities:
- Track realized/unrealized PnL
- Compute performance metrics per strategy, symbol, or portfolio
- Risk-adjusted metrics (Sharpe ratio, max drawdown)
- Historical PnL aggregation for reporting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np


@dataclass
class Trade:
    trade_id: str
    symbol: str
    side: str  # buy/sell
    price: float
    size: float
    timestamp: float = datetime.utcnow().timestamp()


@dataclass
class StrategyMetrics:
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_trades: int = 0
    pnl_history: List[float] = field(default_factory=list)

    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        returns = np.array(self.pnl_history)
        if len(returns) < 2 or np.std(returns) == 0:
            return 0.0
        mean_excess = np.mean(returns - risk_free_rate)
        return mean_excess / np.std(returns) * np.sqrt(252)  # annualized

    def max_drawdown(self) -> float:
        cum_pnl = np.cumsum(self.pnl_history)
        peak = np.maximum.accumulate(cum_pnl)
        drawdowns = peak - cum_pnl
        return float(np.max(drawdowns)) if drawdowns.size > 0 else 0.0


class PerformanceAnalytics:

    def __init__(self):
        self.strategies: Dict[str, StrategyMetrics] = {}
        self.positions: Dict[str, float] = {}  # symbol -> current position
        self.avg_entry: Dict[str, float] = {}  # symbol -> average entry price

    # ---------------------------------------------------
    # Trade updates
    # ---------------------------------------------------

    def add_trade(self, strategy: str, trade: Trade):

        if strategy not in self.strategies:
            self.strategies[strategy] = StrategyMetrics()

        metrics = self.strategies[strategy]

        # Compute realized/unrealized PnL
        pos = self.positions.get(trade.symbol, 0.0)
        avg_price = self.avg_entry.get(trade.symbol, trade.price)

        signed_size = trade.size if trade.side == "buy" else -trade.size

        new_pos = pos + signed_size

        realized = 0.0
        if pos != 0 and np.sign(pos) != np.sign(new_pos):
            # crossing zero -> fully closed some positions
            realized = pos * (trade.price - avg_price) * np.sign(pos)

        metrics.realized_pnl += realized
        metrics.total_trades += 1

        # Update position and average entry
        if new_pos != 0:
            if pos + signed_size != 0:
                self.avg_entry[trade.symbol] = (
                    (avg_price * pos + trade.price * signed_size) / new_pos
                )
            self.positions[trade.symbol] = new_pos
        else:
            self.positions.pop(trade.symbol, None)
            self.avg_entry.pop(trade.symbol, None)

        # Track unrealized PnL
        unrealized = sum(
            self.positions[s] * (trade.price - self.avg_entry[s])
            for s in self.positions
        )
        metrics.unrealized_pnl = unrealized

        # Append to history
        metrics.pnl_history.append(metrics.realized_pnl + metrics.unrealized_pnl)

    # ---------------------------------------------------
    # Metrics access
    # ---------------------------------------------------

    def get_metrics(self, strategy: str) -> Optional[StrategyMetrics]:
        return self.strategies.get(strategy)

    def total_realized_pnl(self) -> float:
        return sum(m.realized_pnl for m in self.strategies.values())

    def total_unrealized_pnl(self) -> float:
        return sum(m.unrealized_pnl for m in self.strategies.values())

    def total_sharpe(self) -> float:
        metrics = list(self.strategies.values())
        if not metrics:
            return 0.0
        all_returns = np.concatenate([np.array(m.pnl_history) for m in metrics])
        if len(all_returns) < 2 or np.std(all_returns) == 0:
            return 0.0
        mean = np.mean(all_returns)
        std = np.std(all_returns)
        return mean / std * np.sqrt(252)

    def total_max_drawdown(self) -> float:
        metrics = list(self.strategies.values())
        if not metrics:
            return 0.0
        cum_pnl = np.cumsum(np.concatenate([np.array(m.pnl_history) for m in metrics]))
        if len(cum_pnl) == 0:
            return 0.0
        peak = np.maximum.accumulate(cum_pnl)
        drawdowns = peak - cum_pnl
        return float(np.max(drawdowns))
