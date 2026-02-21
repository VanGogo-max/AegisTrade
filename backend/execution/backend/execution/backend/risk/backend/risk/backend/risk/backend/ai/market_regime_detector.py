from typing import Dict
import statistics


class MarketRegimeDetector:

    def __init__(
        self,
        trend_threshold: float = 0.02,
        volatility_threshold: float = 0.03,
        strong_trend_threshold: float = 0.05,
    ):
        self.trend_threshold = trend_threshold
        self.volatility_threshold = volatility_threshold
        self.strong_trend_threshold = strong_trend_threshold

    # -----------------------------------------------------

    def detect(
        self,
        prices: list,
        volumes: list,
        funding_rate: float = 0.0,
    ) -> Dict:

        if len(prices) < 20:
            return {"regime": "UNKNOWN"}

        trend = self._calculate_trend(prices)
        volatility = self._calculate_volatility(prices)
        volume_trend = self._volume_trend(volumes)

        regime = self._classify(
            trend,
            volatility,
            volume_trend,
            funding_rate,
        )

        return {
            "regime": regime,
            "trend": trend,
            "volatility": volatility,
            "volume_trend": volume_trend,
            "funding_rate": funding_rate,
        }

    # -----------------------------------------------------

    def _calculate_trend(self, prices):

        start = prices[0]
        end = prices[-1]

        if start == 0:
            return 0

        return (end - start) / start

    # -----------------------------------------------------

    def _calculate_volatility(self, prices):

        returns = []

        for i in range(1, len(prices)):
            prev = prices[i - 1]
            curr = prices[i]

            if prev == 0:
                continue

            returns.append((curr - prev) / prev)

        if not returns:
            return 0

        return statistics.stdev(returns)

    # -----------------------------------------------------

    def _volume_trend(self, volumes):

        if len(volumes) < 2:
            return 0

        start = volumes[0]
        end = volumes[-1]

        if start == 0:
            return 0

        return (end - start) / start

    # -----------------------------------------------------

    def _classify(
        self,
        trend,
        volatility,
        volume_trend,
        funding_rate,
    ):

        if abs(trend) > self.strong_trend_threshold and volume_trend > 0:
            return "STRONG_TREND"

        if abs(trend) > self.trend_threshold:
            return "TREND"

        if volatility > self.volatility_threshold:
            return "VOLATILE"

        if abs(trend) < 0.005 and volatility < self.volatility_threshold:
            return "RANGE"

        if funding_rate > 0.03 or funding_rate < -0.03:
            return "FUNDING_EXTREME"

        return "NEUTRAL"
