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


class GMXAdapter(BaseExecutionAdapter):

    # GMX v2 на Arbitrum
    BASE_URL = "https://arbitrum-api.gmxinfra.io"

    MARKET_IDS = {
        "BTC": "0x47c031236e19d024b42f8AE6780E44A573170703",
        "ETH": "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
        "SOL": "0x09400D9DB990D5ed3f35D7be61DfAEB900Af03C9",
        "ARB": "0xC25cEf6061Cf5dE5eb761b50E4743c1F5D7E5407",
    }

    def __init__(self):
        self.private_key = Config.DEX_PRIVATE_KEY
        self.wallet = Config.DEX_WALLET_ADDRESS
        self.rpc_url = Config.ARBITRUM_RPC_URL

    async def place_order(self, request: ExecutionRequest) -> ExecutionResult:
        if Config.DRY_RUN:
            logger.debug(f"[DRY RUN GMX] {request.side} {request.quantity} {request.symbol}")
            return ExecutionResult(
                exchange="gmx",
                symbol=request.symbol,
                order_id=f"gmx-dry-{int(time.time())}",
                status="filled",
                filled_quantity=request.quantity,
                avg_price=request.price or Decimal("0"),
                raw_response={},
            )

        market_id = self._market_id(request.symbol)
        is_long = request.side == OrderSide.BUY

        payload = {
            "market": market_id,
            "isLong": is_long,
            "sizeDeltaUsd": str(int(request.quantity * (request.price or Decimal("1")))),
            "acceptablePrice": str(request.price or "0"),
            "orderType": 2 if request.order_type == OrderType.MARKET else 3,
            "executionFee": "100000000000000",
            "account": self.wallet,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/orders",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                data = await resp.json()
                logger.debug(f"GMX response: {data}")

                return ExecutionResult(
                    exchange="gmx",
                    symbol=request.symbol,
                    order_id=str(data.get("orderKey", f"gmx-{int(time.time())}")),
                    status=data.get("status", "submitted"),
                    filled_quantity=request.quantity,
                    avg_price=request.price,
                    raw_response=data,
                )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        if Config.DRY_RUN:
            logger.debug(f"[DRY RUN GMX] cancel {order_id}")
            return True

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.BASE_URL}/orders/{order_id}",
                json={"account": self.wallet},
            ) as resp:
                data = await resp.json()
                return data.get("status") == "ok"

    def _market_id(self, symbol: str) -> str:
        base = symbol.split("-")[0].upper()
        market = self.MARKET_IDS.get(base)
        if not market:
            raise ValueError(f"GMX: unknown market for {symbol}")
        return market
