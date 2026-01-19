# performance_analyzer.py
# Анализ на търговските резултати: PnL, drawdowns, стратегии, performance metrics

from trade_logger import fetch_trades
import pandas as pd
from datetime import datetime
from loguru import logger

# ----------------------------
# Performance Analyzer Class
# ----------------------------
class PerformanceAnalyzer:
    def __init__(self, limit: int = 1000):
        """
        Инициализация:
        - limit: брой последни сделки за анализ
        """
        self.limit = limit
        self.df = self._load_trades()

    def _load_trades(self):
        trades = fetch_trades(self.limit)
        if not trades:
            logger.warning("⚠️ Няма налични сделки за анализ")
            return pd.DataFrame()
        df = pd.DataFrame(trades, columns=[
            "id", "timestamp", "strategy", "symbol", "side",
            "entry_price", "exit_price", "size", "pnl", "chain", "notes"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["pnl"] = df["pnl"].astype(float)
        return df

    # ----------------------------
    # Общ PnL
    # ----------------------------
    def total_pnl(self):
        if self.df.empty:
            return 0.0
        total = self.df["pnl"].sum()
        logger.info(f"💰 Total PnL: {total:.4f}")
        return total

    # ----------------------------
    # PnL по стратегии
    # ----------------------------
    def pnl_by_strategy(self):
        if self.df.empty:
            return {}
        grouped = self.df.groupby("strategy")["pnl"].sum().to_dict()
        logger.info(f"📊 PnL by strategy: {grouped}")
        return grouped

    # ----------------------------
    # Drawdowns
    # ----------------------------
    def max_drawdown(self):
        if self.df.empty:
            return 0.0
        df_sorted = self.df.sort_values("timestamp")
        cum_pnl = df_sorted["pnl"].cumsum()
        peak = cum_pnl.cummax()
        drawdown = (cum_pnl - peak)
        max_dd = drawdown.min()
        logger.info(f"📉 Max Drawdown: {max_dd:.4f}")
        return max_dd

    # ----------------------------
    # Trades per Symbol
    # ----------------------------
    def trades_per_symbol(self):
        if self.df.empty:
            return {}
        counts = self.df["symbol"].value_counts().to_dict()
        logger.info(f"🔖 Trades per symbol: {counts}")
        return counts

    # ----------------------------
    # Summary Report
    # ----------------------------
    def summary(self):
        logger.info("================ Performance Summary ================")
        self.total_pnl()
        self.pnl_by_strategy()
        self.max_drawdown()
        self.trades_per_symbol()
        logger.info("===================================================")
        return {
            "total_pnl": self.total_pnl(),
            "pnl_by_strategy": self.pnl_by_strategy(),
            "max_drawdown": self.max_drawdown(),
            "trades_per_symbol": self.trades_per_symbol()
        }

# ----------------------------
# Example Usage (може да се импортира в Core или Research)
# ----------------------------
if __name__ == "__main__":
    analyzer = PerformanceAnalyzer(limit=500)
    summary = analyzer.summary()
    print(summary)
