# backend/execution/fill_handler.py

from typing import Dict, Any


class FillHandler:
    """
    Handles trade fills coming from exchanges.
    Updates position manager and execution statistics.
    """

    def __init__(self, position_manager):

        self.position_manager = position_manager

        self.trade_history = []

    async def on_fill(self, fill: Dict[str, Any]):

        """
        Expected fill format:

        {
            "exchange": "hyperliquid",
            "symbol": "BTC",
            "side": "buy",
            "price": 43000,
            "size": 0.1,
            "order_id": "abc123",
            "timestamp": 123456789
        }
        """

        self.trade_history.append(fill)

        await self.position_manager.update_from_fill(fill)

    def get_trade_history(self):

        return self.trade_history

    def get_total_volume(self):

        volume = 0

        for trade in self.trade_history:
            volume += trade["size"]

        return volume
