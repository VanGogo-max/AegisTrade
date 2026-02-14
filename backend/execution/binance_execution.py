# backend/execution/binance_execution.py

import time
import hmac
import hashlib
import aiohttp
from decimal import Decimal
from urllib.parse import urlencode
from typing import Dict, Any

from .execution_engine import (
    BaseExecutionAdapter,
    ExecutionRequest,
    ExecutionResult,
    OrderType,
)


BINANCE_BASE_URL = "https://api.binance.com"


class BinanceExecutionAdapter(BaseExecutionAdapter):

    def __init__(
        self,
        api_key: str,
        api_secret: str,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode()

    # ==========================================================
    # PUBLIC METHODS
    # ==========================================================

    async def place_order(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:

        endpoint = "/api/v3/order"

        params = {
            "symbol": request.symbol.replace("/", ""),
            "side": request.side.value.upper(),
            "type": request.order_type.value.upper(),
            "quantity": str(request.quantity),
            "timestamp": int(time.time() * 1000),
        }

        if request.order_type == OrderType.LIMIT:
            params["price"] = str(request.price)
            params["timeInForce"] = "GTC"

        if request.client_order_id:
            params["newClientOrderId"] = request.client_order_id

        signed_params = self._sign(params)

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                BINANCE_BASE_URL + endpoint,
                headers=headers,
                params=signed_params,
            ) as response:

                data = await response.json()

                if response.status != 200:
                    raise RuntimeError(f"Binance error: {data}")

                return self._map_response(data, request.exchange)

    # ----------------------------------------------------------

    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
    ) -> bool:

        endpoint = "/api/v3/order"

        params = {
            "symbol": symbol.replace("/", ""),
            "orderId": order_id,
            "timestamp": int(time.time() * 1000),
        }

        signed_params = self._sign(params)

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                BINANCE_BASE_URL + endpoint,
                headers=headers,
                params=signed_params,
            ) as response:

                return response.status == 200

    # ==========================================================
    # INTERNALS
    # ==========================================================

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_string = urlencode(params)

        signature = hmac.new(
            self.api_secret,
            query_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        params["signature"] = signature
        return params

    def _map_response(
        self,
        data: Dict[str, Any],
        exchange: str,
    ) -> ExecutionResult:

        return ExecutionResult(
            exchange=exchange,
            symbol=data["symbol"],
            order_id=str(data["orderId"]),
            status=data["status"],
            filled_quantity=Decimal(data.get("executedQty", "0")),
            avg_price=Decimal(data["price"]) if data.get("price") else None,
            raw_response=data,
        )
