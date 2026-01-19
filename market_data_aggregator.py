# market_data_aggregator.py
"""
Market Data Aggregator

Role:
- Unified interface for all market data
- Feeds:
    - strategies
    - filter_stack
    - risk_engine
- DEX / CEX agnostic
"""

from typing import Dict, Any
from datetime import datetime


class MarketDataAggregator:
    def __init__(self, price_feed, funding_feed=None, oi_feed=None, volatility_feed=None):
        self.price_feed = price_feed
        self.funding_feed = funding_feed
        self.oi_feed = oi_feed
        self.volatility_feed = volatility_feed

    def snapshot(self, market: str) -> Dict[str, Any]:
        data = {
            "market": market,
            "timestamp": datetime.utcnow().isoformat(),
            "price": self.price_feed.get_price(market),
        }

        if self.funding_feed:
            data["funding_rate"] = self.funding_feed.get_funding(market)

        if self.oi_feed:
            data["open_interest"] = self.oi_feed.get_oi(market)

        if self.volatility_feed:
            data["volatility"] = self.volatility_feed.get_volatility(market)

        return data
