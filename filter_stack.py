# filter_stack.py
"""
Filter Stack

Роля:
- Филтрира сигналите преди да стигнат до RiskEngine
- Всеки филтър е модулен и може да се включва/изключва
- DEX- и стратегия-агностичен
"""

from datetime import datetime, time
from typing import Dict, Any, List
from loguru import logger


class BaseFilter:
    def allow(self, signal: Dict[str, Any]) -> bool:
        raise NotImplementedError


# ----------------------------
# Volatility Filter
# ----------------------------
class VolatilityFilter(BaseFilter):
    def __init__(self, min_vol: float, max_vol: float):
        self.min_vol = min_vol
        self.max_vol = max_vol

    def allow(self, signal: Dict[str, Any]) -> bool:
        vol = signal.get("volatility")
        if vol is None:
            return True
        ok = self.min_vol <= vol <= self.max_vol
        if not ok:
            logger.debug(f"VolatilityFilter blocked: {vol}")
        return ok


# ----------------------------
# Market Regime Filter
# ----------------------------
class RegimeFilter(BaseFilter):
    def __init__(self, allowed_regimes: List[str]):
        self.allowed_regimes = allowed_regimes  # напр. ["trend", "range"]

    def allow(self, signal: Dict[str, Any]) -> bool:
        regime = signal.get("regime")
        if regime is None:
            return True
        ok = regime in self.allowed_regimes
        if not ok:
            logger.debug(f"RegimeFilter blocked: {regime}")
        return ok


# ----------------------------
# Funding Rate Filter (perps)
# ----------------------------
class FundingFilter(BaseFilter):
    def __init__(self, max_abs_funding: float):
        self.max_abs_funding = max_abs_funding

    def allow(self, signal: Dict[str, Any]) -> bool:
        funding = signal.get("funding_rate")
        if funding is None:
            return True
        ok = abs(funding) <= self.max_abs_funding
        if not ok:
            logger.debug(f"FundingFilter blocked: {funding}")
        return ok


# ----------------------------
# Time of Day Filter
# ----------------------------
class TimeOfDayFilter(BaseFilter):
    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end

    def allow(self, signal: Dict[str, Any]) -> bool:
        now = datetime.utcnow().time()
        ok = self.start <= now <= self.end
        if not ok:
            logger.debug(f"TimeOfDayFilter blocked: {now}")
        return ok


# ----------------------------
# Filter Stack Wrapper
# ----------------------------
class FilterStack:
    def __init__(self, filters: List[BaseFilter]):
        self.filters = filters

    def allow(self, signal: Dict[str, Any]) -> bool:
        for f in self.filters:
            if not f.allow(signal):
                return False
        return True

    def apply(self, signal: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Wrapper for CoreEngine usage.
        Returns the signal if all filters pass, else None.
        """
        if self.allow(signal):
            return signal
        return None
