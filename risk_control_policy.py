# risk_control_policy.py
# Responsibility: Global risk / restriction policy (kill-switch layer)
# Dependencies: None (standard library only)

from typing import Dict
from enum import Enum


class Operation(Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    WITHDRAWALS = "withdrawals"
    DEPOSITS = "deposits"


class RiskControlPolicy:
    def __init__(self) -> None:
        self._global_enabled: bool = True
        self._operation_flags: Dict[Operation, bool] = {
            Operation.SPOT_TRADING: True,
            Operation.FUTURES_TRADING: True,
            Operation.WITHDRAWALS: True,
            Operation.DEPOSITS: True,
        }
        self._blocked_exchanges: Dict[str, bool] = {}

    def disable_all(self) -> None:
        self._global_enabled = False

    def enable_all(self) -> None:
        self._global_enabled = True

    def set_operation_state(self, operation: Operation, enabled: bool) -> None:
        self._operation_flags[operation] = enabled

    def block_exchange(self, exchange_name: str) -> None:
        self._blocked_exchanges[exchange_name.lower()] = True

    def unblock_exchange(self, exchange_name: str) -> None:
        self._blocked_exchanges.pop(exchange_name.lower(), None)

    def is_operation_allowed(self, operation: Operation, exchange_name: str) -> bool:
        if not self._global_enabled:
            return False

        if not self._operation_flags.get(operation, False):
            return False

        if self._blocked_exchanges.get(exchange_name.lower(), False):
            return False

        return True
