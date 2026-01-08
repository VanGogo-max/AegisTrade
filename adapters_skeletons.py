"""
Skeleton adapters for KCEX, Hyperliquid, dYdX, GMX, Kwenta, Vertex, Apex
All inherit RealExchangeAdapterBase, ready for production.
No API keys, no actual execution, just method signatures.
"""

from real_exchange_adapter_base import RealExchangeAdapterBase


class KCEXAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("KCEX")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("KCEXAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("KCEXAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("KCEXAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("KCEXAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("KCEXAdapter.fetch_market_data not implemented")


class HyperliquidAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("Hyperliquid")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("HyperliquidAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("HyperliquidAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("HyperliquidAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("HyperliquidAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("HyperliquidAdapter.fetch_market_data not implemented")


class dYdXAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("dYdX")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("dYdXAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("dYdXAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("dYdXAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("dYdXAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("dYdXAdapter.fetch_market_data not implemented")


class GMXAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("GMX")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("GMXAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("GMXAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("GMXAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("GMXAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("GMXAdapter.fetch_market_data not implemented")


class KwentaAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("Kwenta")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("KwentaAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("KwentaAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("KwentaAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("KwentaAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("KwentaAdapter.fetch_market_data not implemented")


class VertexAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("Vertex")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("VertexAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("VertexAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("VertexAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("VertexAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("VertexAdapter.fetch_market_data not implemented")


class ApexAdapter(RealExchangeAdapterBase):
    def __init__(self):
        super().__init__("Apex")

    def place_order(self, order: dict) -> dict:
        raise NotImplementedError("ApexAdapter.place_order not implemented")

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError("ApexAdapter.cancel_order not implemented")

    def get_balance(self) -> dict:
        raise NotImplementedError("ApexAdapter.get_balance not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("ApexAdapter.get_order_status not implemented")

    def fetch_market_data(self, symbol: str) -> dict:
        raise NotImplementedError("ApexAdapter.fetch_market_data not implemented")
