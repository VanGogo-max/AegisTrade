from backend.dex_adapters.hyperliquid_adapter import HyperliquidAdapter
from backend.dex_adapters.gmx_adapter import GMXAdapter
from backend.dex_adapters.dydx_adapter import DYDXAdapter
from backend.dex_adapters.vertex_adapter import VertexAdapter
from backend.dex_adapters.apex_adapter import ApexAdapter
from backend.dex_adapters.kwenta_adapter import KwentaAdapter


class DexRouter:
    def __init__(self):
        self.adapters = {
            "hyperliquid": HyperliquidAdapter(),
            "gmx": GMXAdapter(),
            "dydx": DYDXAdapter(),
            "vertex": VertexAdapter(),
            "apex": ApexAdapter(),
            "kwenta": KwentaAdapter(),
        }

    def get_adapter(self, dex: str):
        if dex not in self.adapters:
            raise ValueError(f"Unsupported DEX: {dex}")
        return self.adapters[dex]
