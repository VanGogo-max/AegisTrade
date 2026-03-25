from abc import ABC, abstractmethod


class BaseDexAdapter(ABC):

    @abstractmethod
    async def place_order(self, symbol, side, size, price, order_type):
        pass

    @abstractmethod
    async def cancel_order(self, order_id):
        pass

    @abstractmethod
    async def get_position(self, symbol):
        pass
