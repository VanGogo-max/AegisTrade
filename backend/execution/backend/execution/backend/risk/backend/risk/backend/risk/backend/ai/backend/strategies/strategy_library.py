from typing import Dict, List


class StrategyLibrary:

    def __init__(self):
        self.strategies = {
            "turtle_breakout": self.turtle_breakout,
            "trend_following": self.trend_following,
            "mean_reversion": self.mean_reversion,
            "multi_position_scale": self.multi_position_scale,
        }

    # -------------------------------------------------

    def get(self, name: str):
        return self.strategies.get(name)

    # -------------------------------------------------

    def list_strategies(self) -> List[str]:
        return list(self.strategies.keys())

    # -------------------------------------------------
    # TURTLE STRATEGY
    # -------------------------------------------------

    def turtle_breakout(self, prices: List[float]) -> Dict:

        if len(prices) < 21:
            return {"action": "HOLD"}

        highest = max(prices[-20:])
        lowest = min(prices[-20:])
        last_price = prices[-1]

        if last_price >= highest:
            return {
                "action": "BUY",
                "reason": "breakout_high"
            }

        if last_price <= lowest:
            return {
                "action": "SELL",
                "reason": "breakout_low"
            }

        return {"action": "HOLD"}

    # -------------------------------------------------
    # TREND FOLLOWING
    # -------------------------------------------------

    def trend_following(self, prices: List[float]) -> Dict:

        if len(prices) < 50:
            return {"action": "HOLD"}

        ema_fast = sum(prices[-10:]) / 10
        ema_slow = sum(prices[-50:]) / 50

        if ema_fast > ema_slow:
            return {
                "action": "BUY",
                "reason": "uptrend"
            }

        if ema_fast < ema_slow:
            return {
                "action": "SELL",
                "reason": "downtrend"
            }

        return {"action": "HOLD"}

    # -------------------------------------------------
    # MEAN REVERSION
    # -------------------------------------------------

    def mean_reversion(self, prices: List[float]) -> Dict:

        if len(prices) < 30:
            return {"action": "HOLD"}

        avg = sum(prices[-30:]) / 30
        last = prices[-1]

        deviation = (last - avg) / avg

        if deviation < -0.02:
            return {
                "action": "BUY",
                "reason": "oversold"
            }

        if deviation > 0.02:
            return {
                "action": "SELL",
                "reason": "overbought"
            }

        return {"action": "HOLD"}

    # -------------------------------------------------
    # MULTI POSITION SCALE
    # -------------------------------------------------

    def multi_position_scale(self, prices: List[float]) -> Dict:

        if len(prices) < 10:
            return {"action": "HOLD"}

        last = prices[-1]
        avg = sum(prices[-10:]) / 10

        diff = (last - avg) / avg

        if diff < -0.01:
            return {
                "action": "BUY_SCALE",
                "levels": 5
            }

        if diff > 0.01:
            return {
                "action": "SELL_SCALE",
                "levels": 5
            }

        return {"action": "HOLD"}
