# exchange_router.py

from typing import Dict, Any, Optional


class ExchangeRouter:
    """
    Central router that delegates trading actions to registered exchange adapters.
    """

    def __init__(self) -> None:
        self._exchanges: Dict[str, Any] = {}

    def register_exchange(self, name: str, adapter: Any) -> None:
        """
        Registers an exchange adapter under a unique name.
        """
        self._exchanges[name] = adapter

    def list_exchanges(self) -> list:
        """
        Returns a list of registered exchange names.
        """
        return list(self._exchanges.keys())

    def get_price(self, exchange: str, symbol: str) -> float:
        """
        Returns the latest price for a symbol from a specific exchange.
        """
        adapter = self._get_adapter(exchange)
        return adapter.get_price(symbol)

    def place_order(
        self,
        exchange: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
    ) -> dict:
        """
        Places an order on the selected exchange.
        """
        adapter = self._get_adapter(exchange)
        return adapter.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
        )

    def cancel_order(self, exchange: str, order_id: str) -> bool:
        """
        Cancels an existing order on the selected exchange.
        """
        adapter = self._get_adapter(exchange)
        return adapter.cancel_order(order_id)

    def _get_adapter(self, exchange: str) -> Any:
        """
        Internal helper for adapter resolution.
        """
        if exchange not in self._exchanges:
            raise ValueError(f"Exchange '{exchange}' is not registered")
        return self._exchanges[exchange]
