from typing import Dict, List
from dataclasses import dataclass
from backend.risk.futures_position_manager import FuturesPositionManager


@dataclass
class GlobalRiskConfig:
    max_total_exposure_pct: float = 0.30      # 30% от капитала
    max_open_positions: int = 5
    max_daily_drawdown: float = 0.05          # 5%
    max_leverage: int = 10


class RiskEngine:
    def __init__(
        self,
        position_manager: FuturesPositionManager,
        config: GlobalRiskConfig,
    ):
        self.position_manager = position_manager
        self.config = config

        self.open_positions: Dict[str, Dict] = {}
        self.account_balance: float = 0.0
        self.daily_loss: float = 0.0

    # -----------------------------------
    # ACCOUNT UPDATE
    # -----------------------------------
    def update_account_balance(self, balance: float):
        self.account_balance = balance

    def update_daily_loss(self, loss: float):
        self.daily_loss += loss

    # -----------------------------------
    # MAIN VALIDATION ENTRY
    # -----------------------------------
    def validate_order(
        self,
        symbol: str,
        position_size: float,
        leverage: int,
    ) -> bool:

        if not self._check_daily_drawdown():
            print("Daily drawdown limit reached.")
            return False

        if not self._check_leverage(leverage):
            print("Leverage exceeds allowed limit.")
            return False

        if not self._check_position_count():
            print("Max open positions reached.")
            return False

        if not self._check_total_exposure(position_size):
            print("Total exposure too high.")
            return False

        return True

    # -----------------------------------
    # RISK CHECKS
    # -----------------------------------
    def _check_daily_drawdown(self) -> bool:
        return self.daily_loss < self.config.max_daily_drawdown

    def _check_leverage(self, leverage: int) -> bool:
        return leverage <= self.config.max_leverage

    def _check_position_count(self) -> bool:
        return len(self.open_positions) < self.config.max_open_positions

    def _check_total_exposure(self, new_position_size: float) -> bool:
        current_exposure = sum(
            pos["notional"] for pos in self.open_positions.values()
        )

        new_exposure = current_exposure + new_position_size

        if self.account_balance == 0:
            return False

        exposure_pct = new_exposure / self.account_balance
        return exposure_pct <= self.config.max_total_exposure_pct

    # -----------------------------------
    # POSITION TRACKING
    # -----------------------------------
    def register_position(
        self,
        symbol: str,
        notional: float,
        direction: str,
    ):
        self.open_positions[symbol] = {
            "notional": notional,
            "direction": direction,
        }

    def close_position(self, symbol: str, pnl: float):
        if symbol in self.open_positions:
            del self.open_positions[symbol]

        if pnl < 0:
            self.update_daily_loss(abs(pnl))

    # -----------------------------------
    # STATUS
    # -----------------------------------
    def get_risk_status(self) -> Dict:
        return {
            "balance": self.account_balance,
            "open_positions": len(self.open_positions),
            "daily_loss": self.daily_loss,
            "max_exposure_pct": self.config.max_total_exposure_pct,
        }
