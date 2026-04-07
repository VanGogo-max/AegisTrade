import hashlib
import hmac
import time
from decimal import Decimal

import aiohttp
from loguru import logger

from backend.execution.execution_engine import (
    BaseExecutionAdapter,
    ExecutionRequest,
    ExecutionResult,
    OrderSide,
    OrderType,
)
from backend.config.config import Config


class HyperliquidAdapter(BaseExecutionAdapter):

    BASE_URL = "https://api.hyperliquid.xyz"

    def __init__(self):
        self.private_key = Config.HYPERLIQUID_PRIVATE_KEY
        self.wallet = Config.DEX_WALLET_ADDRESS

    async def place_order(self, request: ExecutionRequest) -> ExecutionResult:
        if Config.DRY_RUN:
            logger.debug(f"[DRY RUN] place_order {request.side} {request.quantity} {request.symbol}")
            return ExecutionResult(
                exchange="hyperliquid",
                symbol=request.symbol,
                order_id=f"dry-{int(time.time())}",
                status="filled",
                filled_quantity=request.quantity,
                avg_price=request.price or Decimal("0"),
                raw_response={},
            )

        payload = {
            "action": {
                "type": "order",
                "orders": [{
                    "a": self._asset_index(request.symbol),
                    "b": request.side == OrderSide.BUY,
                    "p": str(request.price or "0"),
                    "s": str(request.quantity),
                    "r": False,
                    "t": {"limit": {"tif": "Gtc"}} if request.order_type == OrderType.LIMIT
                         else {"market": {}},
                }],
                "grouping": "na",
            },
            "nonce": int(time.time() * 1000),
            "signature": self._sign(),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/exchange",
                json=payload,
            ) as resp:
                data = await resp.json()
                logger.debug(f"Hyperliquid response: {data}")
                order_id = str(
                    data.get("response", {})
                    .get("data", {})
                    .get("statuses", [{}])[0]
                    .get("resting", {})
                    .get("oid", "0")
                )
                return ExecutionResult(
                    exchange="hyperliquid",
                    symbol=request.symbol,
                    order_id=order_id,
                    status=data.get("status", "unknown"),
                    filled_quantity=request.quantity,
                    avg_price=request.price,
                    raw_response=data,
                )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        if Config.DRY_RUN:
            logger.debug(f"[DRY RUN] cancel_order {order_id}")
            return True

        payload = {
            "action": {
                "type": "cancel",
                "cancels": [{"a": self._asset_index(symbol), "o": int(order_id)}],
            },
            "nonce": int(time.time() * 1000),
            "signature": self._sign(),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE_URL}/exchange", json=payload) as resp:
                data = await resp.json()
                return data.get("status") == "ok"

    def _asset_index(self, symbol: str) -> int:
        mapping = {"BTC": 0, "ETH": 1, "SOL": 2, "ARB": 3}
        base = symbol.split("-")[0].upper()
        return mapping.get(base, 0)

    def _sign(self) -> str:
        if not self.private_key:
            return ""
        msg = f"{self.wallet}{int(time.time() * 1000)}"
        return hmac.new(
            self.private_key.encode(),
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()
