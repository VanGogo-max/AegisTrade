from typing import Dict, Any


class DexExecutor:
    """
    Exchange-agnostic DEX execution router.
    Routes execution to the selected decentralized exchange.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name.lower()

        if self.exchange_name == "hyperliquid":
            from backend.execution.dex_impl.hyperliquid_executor import HyperliquidExecutor
            self.engine = HyperliquidExecutor()

        elif self.exchange_name == "dydx":
            from backend.execution.dex_impl.dydx_executor import DyDxExecutor
            self.engine = DyDxExecutor()

        elif self.exchange_name == "gmx":
            from backend.execution.dex_impl.gmx_executor import GMXExecutor
            self.engine = GMXExecutor()

        elif self.exchange_name == "apex":
            from backend.execution.dex_impl.apex_executor import ApexExecutor
            self.engine = ApexExecutor()

        elif self.exchange_name == "kwenta":
            from backend.execution.dex_impl.kwenta_executor import KwentaExecutor
            self.engine = KwentaExecutor()

        elif self.exchange_name == "vertex":
            from backend.execution.dex_impl.vertex_executor import VertexExecutor
            self.engine = VertexExecutor()

        else:
            raise ValueError(f"Unsupported DEX: {exchange_name}")

    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        **kwargs
    ) -> Dict[str, Any]:
        return await self.engine.place_order(
            symbol=symbol,
            side=side,
            size=size,
            **kwargs
        )

    async def cancel_order(
        self,
        symbol: str,
        order_id: str
    ) -> Dict[str, Any]:
        return await self.engine.cancel_order(
            symbol=symbol,
            order_id=order_id
        )
