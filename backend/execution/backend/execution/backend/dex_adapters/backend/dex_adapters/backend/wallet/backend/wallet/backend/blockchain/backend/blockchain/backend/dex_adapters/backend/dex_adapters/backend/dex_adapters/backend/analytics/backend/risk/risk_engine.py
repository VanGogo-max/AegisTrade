from typing import Dict


class RiskEngine:
    """
    Risk management за DeFi trading (GMX + други DEX)
    Работи върху данни от PnL engine
    """

    def __init__(
        self,
        max_drawdown_percent: float = 20,
        stop_loss_percent: float = 10,
        take_profit_percent: float = 20,
        max_leverage: float = 5
    ):
        self.max_drawdown_percent = max_drawdown_percent
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.max_leverage = max_leverage

    # ---------------- CORE ----------------

    def evaluate(self, metrics: Dict) -> Dict:
        """
        Взима решение:
        - hold
        - close
        - reduce
        """

        pnl_percent = metrics.get("pnl_percent", 0)
        leverage = metrics.get("leverage", 0)

        # 📉 Stop Loss
        if pnl_percent <= -self.stop_loss_percent:
            return {
                "action": "close",
                "reason": "stop_loss"
            }

        # 📈 Take Profit
        if pnl_percent >= self.take_profit_percent:
            return {
                "action": "close",
                "reason": "take_profit"
            }

        # ⚠️ Over leverage
        if leverage >= self.max_leverage:
            return {
                "action": "reduce",
                "reason": "high_leverage"
            }

        return {
            "action": "hold",
            "reason": "normal"
        }

    # ---------------- POSITION SIZING ----------------

    def calculate_position_size(
        self,
        account_balance: float,
        risk_per_trade_percent: float,
        entry_price: float,
        stop_loss_price: float
    ) -> float:
        """
        Position sizing (risk-based)
        """

        risk_amount = account_balance * (risk_per_trade_percent / 100)

        price_diff = abs(entry_price - stop_loss_price)

        if price_diff == 0:
            return 0

        position_size = risk_amount / price_diff

        return position_size

    # ---------------- KILL SWITCH ----------------

    def check_max_drawdown(
        self,
        equity_start: float,
        equity_current: float
    ) -> bool:
        """
        True = STOP TRADING
        """

        drawdown = ((equity_start - equity_current) / equity_start) * 100

        return drawdown >= self.max_drawdown_percent
