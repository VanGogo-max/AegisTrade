import os
import aiohttp
from typing import Dict, Any


class HyperliquidExecutor:
    """
    Hyperliquid DEX execution engine.
    Uses official REST endpoint.
    """

    BASE_URL = "https://api.hyperliquid.xyz"

    def __init__(self):
        self.private_key = os.getenv("DEX_PRIVATE_KEY")
        self.wallet_address = os.getenv("DEX_WALLET_ADDRESS")

        if not self.private_key or not self.wallet_address:
            raise ValueError("Missing DEX wallet credentials")

    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "market",
        price: float = None,
    ) -> Dict[str, Any]:

        payload = {
            "action": "order",
            "orders": [
                {
                    "coin": symbol,
                    "is_buy": True if side.upper() == "BUY" else False,
                    "sz": str(size),
                    "limit_px": str(price) if price else None,
                    "order_type": order_type,
                }
            ],
            "address": self.wallet_address
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/exchange",
                json=payload
            ) as response:

                data = await response.json()

                if response.status != 200:
                    raise Exception(f"Hyperliquid error: {data}")

                return data

    async def cancel_order(
        self,
        symbol: str,
        order_id: str
    ) -> Dict[str, Any]:

        payload = {
            "action": "cancel",
            "cancels": [
                {
                    "coin": symbol,
                    "oid": order_id
                }
            ],
            "address": self.wallet_address
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/exchange",
                json=payload
            ) as response:

                data = await response.json()

                if response.status != 200:
                    raise Exception(f"Hyperliquid cancel error: {data}")

                return data
