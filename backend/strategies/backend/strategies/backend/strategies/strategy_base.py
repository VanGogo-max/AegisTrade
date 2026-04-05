from abc import ABC, abstractmethod


class StrategyBase(ABC):
    NAME: str = "base"

    @abstractmethod
    def on_price(self, price: float) -> str:
        """Returns BUY / SELL / HOLD"""
        ...
