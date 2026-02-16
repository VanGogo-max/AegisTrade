from typing import Dict, Any
import os

from backend.execution.hyperliquid_execution import HyperliquidExecutionClient


class DexRouter:

    """
    Unified DEX Router.
    Chooses which DEX execution client to use.
    """

    def __init__(self):

        self.hyperliquid_enabled = os.getenv("HYPERLIQUID_ENABLED", "true") == "true"
        self.dydx_enabled = os.getenv("DYDX_ENABLED", "false") == "true"
        self.gmx_enabled = os.getenv("GMX_ENABLED", "false") == "true"
        self.apex_enabled = os.getenv("APEX_ENABLED", "false") == "true"
        self.kwenta_enabled = os.getenv("KWENTA_ENABLED", "false") == "true"
        self.vertex_enabled = os.getenv("VERTEX_ENABLED", "false") == "true"

        self.hyperliquid = None

        if self.hyperliquid_enabled:
            self.hyperliquid = HyperliquidExecutionClient()

    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        leverage: int,
    ) -> Dict[str, Any]:

        # Phase 1: simple routing logic
        # Priority order for now

        if self.hyperliquid_enabled:
            return await self.hyperliquid.place_order(
                symbol=symbol,
                side=side,
                size=size,
                price=price,
                leverage=leverage,
            )

        raise Exception("No DEX enabled")
