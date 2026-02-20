from typing import Dict, List
from backend.exchange_connectors.exchange_registry import ExchangeRegistry
from backend.execution.adaptive_scoring_engine import AdaptiveScoringEngine


class ExchangeScoringEngine:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry
        self.adaptive_engine = AdaptiveScoringEngine()

    # ============================================================
    # MAIN RANKING METHOD
    # ============================================================

    async def rank_exchanges(
        self,
        symbol: str,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
    ) -> List[str]:

        raw_scores = {}

        for name in self.registry.list():

            if not self.registry.is_healthy(name):
                continue

            spread_score = 1 / (spreads.get(name, 1e-6))
            funding_score = abs(funding_rates.get(name, 0.0))

            # Базов комбиниран score
            score = (spread_score * 0.7) + (funding_score * 0.3)

            raw_scores[name] = score

        if not raw_scores:
            return []

        # 🔥 Adaptive adjustment
        adjusted_scores = self.adaptive_engine.apply_dynamic_weights(raw_scores)

        # Sort descending
        ranked = sorted(
            adjusted_scores.keys(),
            key=lambda x: adjusted_scores[x],
            reverse=True,
        )

        return ranked

    # ============================================================
    # PERFORMANCE FEEDBACK
    # ============================================================

    def update_performance(
        self,
        exchange: str,
        slippage: float,
        latency_ms: float,
        success: bool,
    ):
        self.adaptive_engine.update_from_execution(
            exchange=exchange,
            slippage=slippage,
            latency_ms=latency_ms,
            success=success,
        )

    def get_dynamic_weights(self):
        return self.adaptive_engine.get_weights()
