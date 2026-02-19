from typing import Dict, List
from backend.exchange_connectors.exchange_registry import ExchangeRegistry


class ExchangeScoringEngine:

    def __init__(self, registry: ExchangeRegistry):

        self.registry = registry

        # weights (можеш да ги настройваш динамично)
        self.w_latency = 0.3
        self.w_spread = 0.4
        self.w_funding = 0.3

    # ----------------------------------
    # MAIN SCORING METHOD
    # ----------------------------------

    async def rank_exchanges(
        self,
        symbol: str,
        spreads: Dict[str, float],
        funding_rates: Dict[str, float],
    ) -> List[str]:

        healthy = self.registry.healthy_exchanges()

        if not healthy:
            return []

        latency_map = {
            name: self.registry._status[name].latency_ms
            for name in healthy
        }

        norm_latency = self._normalize(latency_map)
        norm_spread = self._normalize(spreads)
        norm_funding = self._normalize_abs(funding_rates)

        scores = {}

        for name in healthy:

            scores[name] = (
                self.w_latency * norm_latency.get(name, 1.0)
                + self.w_spread * norm_spread.get(name, 1.0)
                + self.w_funding * norm_funding.get(name, 1.0)
            )

        ranked = sorted(scores.items(), key=lambda x: x[1])

        return [name for name, _ in ranked]

    # ----------------------------------
    # NORMALIZATION HELPERS
    # ----------------------------------

    def _normalize(self, values: Dict[str, float]) -> Dict[str, float]:

        if not values:
            return {}

        min_v = min(values.values())
        max_v = max(values.values())

        if max_v == min_v:
            return {k: 0.0 for k in values}

        return {
            k: (v - min_v) / (max_v - min_v)
            for k, v in values.items()
        }

    def _normalize_abs(self, values: Dict[str, float]) -> Dict[str, float]:
        abs_values = {k: abs(v) for k, v in values.items()}
        return self._normalize(abs_values)
