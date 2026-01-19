# risk_engine.py
"""
Risk Engine

Роля:
- Превръща сигнал в trade_intent
- Управлява:
  - position sizing
  - max leverage
  - SL / TP
  - max open positions
  - daily drawdown guard
"""

from typing import Dict, Any
from loguru import logger
from datetime import datetime, date


class RiskEngine:
    def __init__(
        self,
        account_equity: float,
        risk_per_trade: float = 0.01,     # 1% от капитала
        max_leverage: float = 10.0,
        max_open_positions: int = 5,
        max_daily_drawdown: float = 0.05 # 5% дневен лимит
    ):
        self.account_equity = account_equity
        self.risk_per_trade = risk_per_trade
        self.max_leverage = max_leverage
        self.max_open_positions = max_open_positions
        self.max_daily_drawdown = max_daily_drawdown

        self.open_positions = 0
        self.today = date.today()
        self.today_pnl = 0.0

    # ----------------------------
    # Main evaluation entry
    # ----------------------------
    def evaluate(self, signal: Dict[str, Any]) -> Dict[str, Any] | None:
        self._rollover_day_if_needed()

        if self._daily_drawdown_exceeded():
            logger.warning("⛔ Daily drawdown limit reached. Trading paused.")
            return None

        if self.open_positions >= self.max_open_positions:
            logger.warning("⛔ Max open positions reached.")
            return None

        size_usd = self._calc_position_size()
        leverage = min(signal.get("leverage", 1.0), self.max_leverage)

        trade_intent = {
            "exchange": signal["exchange"],   # напр. "GMX"
            "action": signal["action"],       # "OPEN" или "CLOSE"
            "market": signal["market"],
            "side": signal["side"],           # "long" / "short"
            "size_usd": size_usd,
            "leverage": leverage,
            "slippage": signal.get("slippage", 0.005),
            "order_type": signal.get("order_type", "market"),
            "strategy": signal.get("strategy", "default"),
        }

        logger.info(f"🛡 Risk approved trade: {trade_intent}")
        return trade_intent

    # ----------------------------
    # Position sizing
    # ----------------------------
    def _calc_position_size(self) -> float:
        size = self.account_equity * self.risk_per_trade
        return round(size, 2)

    # ----------------------------
    # Daily drawdown guard
    # ----------------------------
    def update_pnl(self, pnl: float):
        self._rollover_day_if_needed()
        self.today_pnl += pnl
        logger.info(f"📉 Daily PnL updated: {self.today_pnl:.2f}")

    def _daily_drawdown_exceeded(self) -> bool:
        return self.today_pnl <= -self.account_equity * self.max_daily_drawdown

    def _rollover_day_if_needed(self):
        if date.today() != self.today:
            self.today = date.today()
            self.today_pnl = 0.0
            logger.info("🔄 New trading day. Daily PnL reset.")

    # ----------------------------
    # Position counters
    # ----------------------------
    def on_position_opened(self):
        self.open_positions += 1

    def on_position_closed(self, pnl: float):
        self.open_positions = max(0, self.open_positions - 1)
        self.update_pnl(pnl)
