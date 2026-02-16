from typing import Dict, Any

from backend.execution.smart_dex_router import SmartDexRouter
from backend.risk.risk_engine import RiskEngine


class TradingOrchestrator:

    def __init__(self, dex_clients: Dict[str, Any]):

        self.router = SmartDexRouter(dex_clients)
        self.risk_engine = RiskEngine()

    async def execute_signal(
        self,
        symbol: str,
        side: str,
        size: float,
        leverage: int,
        strategy_name: str,
        account_balance: float,
    ):

        # 1️⃣ Risk validation
        risk_ok = self.risk_engine.validate_trade(
            symbol=symbol,
            size=size,
            leverage=leverage,
            balance=account_balance,
        )

        if not risk_ok:
            return {
                "status": "rejected",
                "reason": "Risk validation failed"
            }

        # 2️⃣ Smart routing (Liquidity + Funding + Split)
        execution_result = await self.router.route_order(
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage,
        )

        return {
            "status": "executed",
            "strategy": strategy_name,
            "result": execution_result,
        }
