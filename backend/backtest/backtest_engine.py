from dataclasses import dataclass
from typing import List, Dict
import math


@dataclass
class BacktestConfig:
    initial_capital: float = 10000.0
    trading_fee: float = 0.0004      # 0.04%
    min_sharpe: float = 1.0
    max_drawdown_allowed: float = 0.25


class BacktestEngine:

    def __init__(self, config: BacktestConfig):
        self.config = config

    # -------------------------------------------------
    # MAIN ENTRY
    # -------------------------------------------------
    def run(
        self,
        prices: List[float],
        signals: List[int],  # 1 = long, -1 = short, 0 = flat
    ) -> Dict:

        capital = self.config.initial_capital
        equity_curve = [capital]
        position = 0
        entry_price = 0
        returns = []
        trades = []

        for i in range(1, len(prices)):

            price = prices[i]

            # Open position
            if signals[i] != 0 and position == 0:
                position = signals[i]
                entry_price = price

            # Close position
            elif signals[i] == 0 and position != 0:
                pnl = self._calculate_pnl(position, entry_price, price)
                capital += pnl
                trades.append(pnl)
                returns.append(pnl / equity_curve[-1])
                position = 0

            equity_curve.append(capital)

        metrics = self._calculate_metrics(equity_curve, returns, trades)

        return metrics

    # -------------------------------------------------
    # PNL CALCULATION
    # -------------------------------------------------
    def _calculate_pnl(self, position, entry, exit):

        gross_return = (exit - entry) / entry
        if position == -1:
            gross_return = -gross_return

        net_return = gross_return - self.config.trading_fee * 2

        return self.config.initial_capital * net_return

    # -------------------------------------------------
    # METRICS
    # -------------------------------------------------
    def _calculate_metrics(
        self,
        equity_curve: List[float],
        returns: List[float],
        trades: List[float],
    ) -> Dict:

        total_return = (equity_curve[-1] / equity_curve[0]) - 1
        max_drawdown = self._max_drawdown(equity_curve)
        sharpe = self._sharpe_ratio(returns)
        winrate = self._winrate(trades)

        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "winrate": winrate,
            "trade_count": len(trades),
            "approved": self._approve_strategy(sharpe, max_drawdown),
        }

    # -------------------------------------------------
    # MAX DRAWDOWN
    # -------------------------------------------------
    def _max_drawdown(self, equity: List[float]):

        peak = equity[0]
        max_dd = 0

        for value in equity:
            if value > peak:
                peak = value

            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)

        return max_dd

    # -------------------------------------------------
    # SHARPE RATIO
    # -------------------------------------------------
    def _sharpe_ratio(self, returns: List[float]):

        if len(returns) < 2:
            return 0.0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        std = math.sqrt(variance)

        if std == 0:
            return 0.0

        return mean / std * math.sqrt(252)

    # -------------------------------------------------
    # WINRATE
    # -------------------------------------------------
    def _winrate(self, trades: List[float]):

        if not trades:
            return 0.0

        wins = sum(1 for t in trades if t > 0)
        return wins / len(trades)

    # -------------------------------------------------
    # APPROVAL LOGIC
    # -------------------------------------------------
    def _approve_strategy(self, sharpe, max_dd):

        if sharpe < self.config.min_sharpe:
            return False

        if max_dd > self.config.max_drawdown_allowed:
            return False

        return True
