import os
import hmac
import hashlib
import time
import asyncio
from typing import Dict, Any, Optional

import aiohttp


BASE_URL = "https://fapi.binance.com"


class BinanceFuturesExecutor:
    """
    Production-ready Binance USDT-M Futures execution client.
    """

    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials")

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

    async def _request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:

        params["timestamp"] = int(time.time() * 1000)

        query_string = "&".join(
            f"{key}={value}" for key, value in params.items()
            if value is not None
        )

        signature = self._sign(query_string)
        query_string += f"&signature={signature}"

        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        url = f"{BASE_URL}{path}?{query_string}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    raise Exception(f"Binance error: {data}")

                return data

    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        POST /fapi/v1/leverage
        """
        return await self._request(
            "POST",
            "/fapi/v1/leverage",
            {
                "symbol": symbol,
                "leverage": leverage
            }
        )

    async def place_order(
        self,
        symbol: str,
        side: str,  # BUY / SELL
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """
        POST /fapi/v1/order
        https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
        """

        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "reduceOnly": "true" if reduce_only else "false",
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("LIMIT order requires price")

            params["price"] = price
            params["timeInForce"] = "GTC"

        return await self._request(
            "POST",
            "/fapi/v1/order",
            params
        )

    async def cancel_order(
        self,
        symbol: str,
        order_id: int
    ) -> Dict[str, Any]:
        """
        DELETE /fapi/v1/order
        """

        return await self._request(
            "DELETE",
            "/fapi/v1/order",
            {
                "symbol": symbol,
                "orderId": order_id
            }
        )
