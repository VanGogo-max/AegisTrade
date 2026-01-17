# base_strategy.py
# Base class for all strategies in GRSM
# Provides template for order generation and risk integration

from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract Base Strategy for GRSM
    All strategies should inherit from this and implement generate_orders().
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_orders(self):
        """
        Must return a list of orders to be submitted to BatchOptimizer.
        Each order is a dict:
        {
            "symbol": str,
            "size": float,
            "price": float,
            "direction": 1 for long, -1 for short
        }
        """
        pass
