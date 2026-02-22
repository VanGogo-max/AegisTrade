import logging
import time
from typing import Dict, Any


class AlertEngine:

    def __init__(self):

        self.last_alert_time: Dict[str, float] = {}
        self.cooldown = 60  # секунди

        logging.basicConfig(level=logging.INFO)

    def _can_send(self, key: str) -> bool:

        now = time.time()

        if key not in self.last_alert_time:
            self.last_alert_time[key] = now
            return True

        if now - self.last_alert_time[key] > self.cooldown:
            self.last_alert_time[key] = now
            return True

        return False

    def alert(self, level: str, message: str, data: Dict[str, Any] | None = None):

        key = f"{level}:{message}"

        if not self._can_send(key):
            return

        payload = {
            "level": level,
            "message": message,
            "data": data or {},
            "timestamp": time.time()
        }

        if level == "CRITICAL":
            logging.error(payload)

        elif level == "WARNING":
            logging.warning(payload)

        else:
            logging.info(payload)

    def exchange_down(self, exchange: str):

        self.alert(
            "CRITICAL",
            "Exchange connection lost",
            {"exchange": exchange}
        )

    def high_slippage(self, symbol: str, slippage: float):

        self.alert(
            "WARNING",
            "High slippage detected",
            {
                "symbol": symbol,
                "slippage": slippage
            }
        )

    def risk_limit_hit(self, reason: str):

        self.alert(
            "CRITICAL",
            "Risk limit triggered",
            {"reason": reason}
        )

    def strategy_changed(self, symbol: str, strategy: str):

        self.alert(
            "INFO",
            "Strategy switched",
            {
                "symbol": symbol,
                "strategy": strategy
            }
        )
