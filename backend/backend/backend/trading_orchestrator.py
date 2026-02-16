from typing import Dict, Any

from backend.execution.smart_dex_router import SmartDexRouter
from backend.risk.risk_engine import RiskEngine
from backend.portfolio.position_manager import PositionManager
from backend.portfolio.portfolio_guard import PortfolioGuard


class TradingOrchestrator:

    def __init__(self, dex_clients: Dict[str, Any]):

        self.router = SmartDexRouter(dex_clients)
        self.risk_engine = RiskEngine()
        self.position_manager = PositionManager()
        self.portfolio_guard = PortfolioGuard()

        self.dex_clients = dex_clients
        self.protective_mode = False

    # ======================================
    # EXECUTE SIGNAL (OPEN POSITION)
    # ======================================

    async def execute_signal(
        self,
        symbol: str,
        side: str,
        size: float,
        leverage: int,
        strategy_name: str,
        account_balance: float,
    ):

        # 🔴 If portfolio in protective mode → block trading
        if self.protective_mode:
            return {
                "status": "blocked",
                "reason": "portfolio_protection_active"
            }

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
                "reason": "risk_validation_failed"
            }

        # 2️⃣ Smart routing execution
        execution_result = await self.router.route_order(
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage,
        )

        # 3️⃣ Register position locally
        # (entry_price трябва да идва от execution_result реално)
        entry_price = execution_result[0]["price"] if isinstance(execution_result, list) else execution_result["price"]

        self.position_manager.register_position(
            symbol=symbol,
            entry_price=entry_price,
            size=size,
            side=side,
            leverage=leverage,
        )

        return {
            "status": "executed",
            "strategy": strategy_name,
            "execution": execution_result,
        }

    # ======================================
    # MARKET UPDATE LOOP
    # ======================================

    async def on_market_update(
        self,
        symbol: str,
        current_price: float,
        atr_value: float,
        current_equity: float,
    ):

        # 1️⃣ Portfolio-level protection
        portfolio_status = self.portfolio_guard.update_equity(current_equity)

        if portfolio_status.get("action") == "close_all":
            await self.close_all_positions()
            self.protective_mode = True
            return {"action": "portfolio_emergency_close"}

        # 2️⃣ Position-level management
        position_action = self.position_manager.update_market_price(
            symbol,
            current_price,
            atr_value,
        )

        if position_action["action"] == "close_full":
            await self.router.route_order(
                symbol=symbol,
                side="short" if self.position_manager.positions[symbol]["side"] == "long" else "long",
                size=self.position_manager.positions[symbol]["remaining_size"],
                leverage=1,
            )

        if position_action["action"] == "close_partial":
            await self.router.route_order(
                symbol=symbol,
                side="short" if self.position_manager.positions[symbol]["side"] == "long" else "long",
                size=position_action["size"],
                leverage=1,
            )

        return {"action": None}

    # ======================================
    # CLOSE ALL POSITIONS
    # ======================================

    async def close_all_positions(self):

        for symbol, position in self.position_manager.positions.items():

            if position["status"] != "open":
                continue

            await self.router.route_order(
                symbol=symbol,
                side="short" if position["side"] == "long" else "long",
                size=position["remaining_size"],
                leverage=1,
            )

            position["status"] = "closed"
