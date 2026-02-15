from dataclasses import dataclass
from typing import Dict


@dataclass
class VolatilityConfig:
    target_volatility: float = 0.15      # 15% годишна целева волатилност
    max_volatility: float = 0.60         # 60% защитен лимит
    min_leverage: float = 0.5
    max_leverage: float = 5.0
    smoothing_factor: float = 0.9       # EMA smoothing


class VolatilityController:

    def __init__(self, config: VolatilityConfig):
        self.config = config
        self.smoothed_volatility: Dict[str, float] = {}

    # -------------------------------------------------
    # PUBLIC ENTRY
    # -------------------------------------------------
    def adjust_leverage(
        self,
        symbol: str,
        realized_volatility: float,
        base_leverage: float,
    ) -> float:
        """
        Returns adjusted leverage based on volatility targeting.
        """

        vol = self._smooth_volatility(symbol, realized_volatility)

        if vol <= 0:
            return base_leverage

        # Protective shutdown if extreme volatility
        if vol >= self.config.max_volatility:
            return self.config.min_leverage

        # Volatility targeting formula:
        # leverage = target_vol / realized_vol
        target_leverage = self.config.target_volatility / vol

        adjusted = base_leverage * target_leverage

        return self._clamp_leverage(adjusted)

    # -------------------------------------------------
    # EMA SMOOTHING
    # -------------------------------------------------
    def _smooth_volatility(
        self,
        symbol: str,
        current_vol: float,
    ) -> float:

        if symbol not in self.smoothed_volatility:
            self.smoothed_volatility[symbol] = current_vol
            return current_vol

        prev = self.smoothed_volatility[symbol]
        smoothed = (
            self.config.smoothing_factor * prev +
            (1 - self.config.smoothing_factor) * current_vol
        )

        self.smoothed_volatility[symbol] = smoothed
        return smoothed

    # -------------------------------------------------
    # LEVERAGE LIMITS
    # -------------------------------------------------
    def _clamp_leverage(self, leverage: float) -> float:
        return max(
            self.config.min_leverage,
            min(leverage, self.config.max_leverage)
        )
