# gmx_sandwich_guard.py

import time
from typing import Dict, List
from web3 import Web3


class GMXSandwichGuard:
    """
    Detects potential MEV sandwich attacks on GMX swaps and position opens.
    """

    def __init__(
        self,
        web3: Web3,
        watched_pairs: List[str],
        price_impact_threshold: float = 0.3,   # %
        volume_spike_ratio: float = 3.0,
        time_window: int = 15
    ):
        self.web3 = web3
        self.watched_pairs = watched_pairs
        self.price_impact_threshold = price_impact_threshold
        self.volume_spike_ratio = volume_spike_ratio
        self.time_window = time_window

        self.recent_swaps: List[Dict] = []

    def record_swap(self, pair: str, side: str, price: float, volume: float):
        self.recent_swaps.append({
            "pair": pair,
            "side": side,  # buy / sell
            "price": price,
            "volume": volume,
            "timestamp": time.time()
        })
        self._cleanup()

    def _cleanup(self):
        cutoff = time.time() - self.time_window
        self.recent_swaps = [
            s for s in self.recent_swaps if s["timestamp"] >= cutoff
        ]

    def _detect_pattern(self, pair: str) -> bool:
        pair_swaps = [s for s in self.recent_swaps if s["pair"] == pair]
        if len(pair_swaps) < 3:
            return False

        first, middle, last = pair_swaps[-3:]

        # buy -> our tx -> sell pattern
        return first["side"] == "buy" and last["side"] == "sell"

    def _detect_volume_spike(self, pair: str) -> bool:
        pair_swaps = [s for s in self.recent_swaps if s["pair"] == pair]
        if len(pair_swaps) < 2:
            return False

        volumes = [s["volume"] for s in pair_swaps]
        avg = sum(volumes[:-1]) / (len(volumes) - 1)
        return pair_swaps[-1]["volume"] > avg * self.volume_spike_ratio

    def _detect_price_impact(self, before: float, after: float) -> bool:
        impact = abs(after - before) / before * 100
        return impact >= self.price_impact_threshold

    def evaluate_trade_risk(
        self,
        pair: str,
        expected_price: float,
        expected_volume: float,
        current_price: float
    ) -> Dict[str, object]:

        self._cleanup()

        sandwich = self._detect_pattern(pair)
        volume_attack = self._detect_volume_spike(pair)
        price_attack = self._detect_price_impact(expected_price, current_price)

        risk_score = 0
        if sandwich:
            risk_score += 0.5
        if volume_attack:
            risk_score += 0.3
        if price_attack:
            risk_score += 0.2

        return {
            "sandwich_pattern": sandwich,
            "volume_spike": volume_attack,
            "price_impact": price_attack,
            "risk_score": round(risk_score, 2),
            "block_trade": risk_score >= 0.6
        }
