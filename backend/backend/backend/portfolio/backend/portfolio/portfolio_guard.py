from typing import Dict, Any


class PortfolioGuard:

    def __init__(self):

        self.initial_equity = None
        self.peak_equity = None

        self.max_drawdown_percent = 0.10  # 10% portfolio drawdown limit

    # ==============================
    # EQUITY UPDATE
    # ==============================

    def update_equity(self, current_equity: float) -> Dict[str, Any]:

        if self.initial_equity is None:
            self.initial_equity = current_equity
            self.peak_equity = current_equity
            return {"action": None}

        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        drawdown = self.calculate_drawdown(current_equity)

        if drawdown >= self.max_drawdown_percent:
            return {
                "action": "close_all",
                "reason": "portfolio_drawdown_limit",
                "drawdown": drawdown,
            }

        return {"action": None, "drawdown": drawdown}

    # ==============================
    # DRAWDOWN CALCULATION
    # ==============================

    def calculate_drawdown(self, current_equity: float) -> float:

        if self.peak_equity == 0:
            return 0.0

        return (self.peak_equity - current_equity) / self.peak_equity
