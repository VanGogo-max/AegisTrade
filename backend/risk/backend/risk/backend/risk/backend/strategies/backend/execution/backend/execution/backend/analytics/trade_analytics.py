# backend/analytics/trade_analytics.py

from typing import List, Dict


class TradeAnalytics:

    def __init__(self):

        self.trades: List[Dict] = []

    def record_trade(self, trade: Dict):

        """
        trade example

        {
            "symbol": "BTC",
            "side": "buy",
            "price": 43000,
            "size": 0.1,
            "exchange": "hyperliquid",
            "timestamp": 123456789
        }
        """

        self.trades.append(trade)

    def total_trades(self):

        return len(self.trades)

    def total_volume(self):

        volume = 0

        for t in self.trades:
            volume += t["size"]

        return volume

    def pnl(self):

        pnl = 0

        for t in self.trades:

            if t["side"] == "buy":
                pnl -= t["price"] * t["size"]

            if t["side"] == "sell":
                pnl += t["price"] * t["size"]

        return pnl

    def trades_by_symbol(self, symbol: str):

        return [t for t in self.trades if t["symbol"] == symbol]

    def win_rate(self):

        wins = 0
        losses = 0

        for t in self.trades:

            if "pnl" not in t:
                continue

            if t["pnl"] > 0:
                wins += 1
            else:
                losses += 1

        total = wins + losses

        if total == 0:
            return 0

        return wins / total
