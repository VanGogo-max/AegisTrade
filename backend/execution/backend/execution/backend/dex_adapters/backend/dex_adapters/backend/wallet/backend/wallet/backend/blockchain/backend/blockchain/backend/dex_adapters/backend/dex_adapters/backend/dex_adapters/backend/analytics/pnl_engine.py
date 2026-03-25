from typing import Dict


class PnLEngine:
    """
    Работи с GMX данни (precision 1e30)
    """

    def calculate(self, position: Dict) -> Dict:

        if not position or position.get("size_usd", 0) == 0:
            return {
                "pnl_usd": 0,
                "pnl_percent": 0,
                "leverage": 0,
                "liquidation_price": 0
            }

        size = position["size_usd"]
        collateral = position["collateral_usd"]
        entry_price = position["entry_price"]
        pnl = position["pnl_usd"]

        # 📊 1. PnL %
        pnl_percent = (pnl / collateral) * 100 if collateral > 0 else 0

        # 📊 2. Leverage
        leverage = size / collateral if collateral > 0 else 0

        # 📊 3. Approx liquidation price (опростен модел)
        # GMX реално използва по-сложна формула с funding + fees

        if leverage > 0:
            liquidation_price = entry_price * (1 - (1 / leverage))
        else:
            liquidation_price = 0

        return {
            "pnl_usd": pnl,
            "pnl_percent": pnl_percent,
            "leverage": leverage,
            "liquidation_price": liquidation_price
        }
