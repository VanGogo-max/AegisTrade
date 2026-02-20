from typing import Dict
import math


class AdaptiveScoringEngine:

    def __init__(
        self,
        base_weights: Dict[str, float] = None,
        learning_rate: float = 0.1,
        min_weight: float = 0.1,
        max_weight: float = 3.0,
    ):
        """
        learning_rate: колко агресивно се адаптира (0.05–0.2 разумен диапазон)
        """
        self.base_weights = base_weights or {}
        self.dynamic_weights: Dict[str, float] = {}
        self.learning_rate = learning_rate
        self.min_weight = min_weight
        self.max_weight = max_weight

    # ============================================================
    # UPDATE BASE EXCHANGES
    # ============================================================

    def register_exchange(self, name: str):
        if name not in self.dynamic_weights:
            self.dynamic_weights[name] = 1.0

    # ============================================================
    # UPDATE PERFORMANCE FEEDBACK
    # ============================================================

    def update_from_execution(
        self,
        exchange: str,
        slippage: float,
        latency_ms: float,
        success: bool,
    ):
        """
        Адаптира weight според:
        - slippage
        - latency
        - success/failure
        """

        self.register_exchange(exchange)

        weight = self.dynamic_weights[exchange]

        # Нормализиране на факторите
        slippage_penalty = slippage * 10  # 1% slippage → 0.1 penalty
        latency_penalty = latency_ms / 10000  # 100ms → 0.01 penalty
        failure_penalty = 0.2 if not success else 0.0

        total_penalty = slippage_penalty + latency_penalty + failure_penalty

        # EMA update
        adjustment = - total_penalty * self.learning_rate

        new_weight = weight + adjustment

        # clamp
        new_weight = max(self.min_weight, min(self.max_weight, new_weight))

        self.dynamic_weights[exchange] = new_weight

    # ============================================================
    # APPLY TO SCORES
    # ============================================================

    def apply_dynamic_weights(
        self,
        raw_scores: Dict[str, float],
    ) -> Dict[str, float]:

        adjusted = {}

        for exchange, score in raw_scores.items():

            self.register_exchange(exchange)

            dynamic_weight = self.dynamic_weights.get(exchange, 1.0)

            adjusted[exchange] = score * dynamic_weight

        return adjusted

    # ============================================================
    # DIAGNOSTICS
    # ============================================================

    def get_weights(self) -> Dict[str, float]:
        return self.dynamic_weights.copy()
