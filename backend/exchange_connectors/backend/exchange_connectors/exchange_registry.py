# backend/exchange_connectors/exchange_registry.py

from typing import Dict, List
from .base_dex_connector import BaseDexConnector


class ExchangeRegistry:

    def __init__(self):
        self._exchanges: Dict[str, BaseDexConnector] = {}

    # ----------------------------------
    # REGISTER
    # ----------------------------------

    def register(self, name: str, connector: BaseDexConnector):

        if name in self._exchanges:
            raise ValueError(f"Exchange '{name}' already registered")

        self._exchanges[name] = connector

    # ----------------------------------
    # GET
    # ----------------------------------

    def get(self, name: str) -> BaseDexConnector:

        if name not in self._exchanges:
            raise ValueError(f"Exchange '{name}' not found")

        return self._exchanges[name]

    # ----------------------------------
    # LIST
    # ----------------------------------

    def list_exchanges(self) -> List[str]:
        return list(self._exchanges.keys())

    # ----------------------------------
    # ALL CONNECTORS
    # ----------------------------------

    def all(self) -> Dict[str, BaseDexConnector]:
        return self._exchanges

    # ----------------------------------
    # REMOVE (optional)
    # ----------------------------------

    def unregister(self, name: str):

        if name not in self._exchanges:
            raise ValueError(f"Exchange '{name}' not found")

        del self._exchanges[name]
