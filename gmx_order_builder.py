# gmx_order_builder.py
# Updated GMX Order Builder with build_open/build_close + trade_logger

from decimal import Decimal
from loguru import logger
from trade_logger import log_trade

class GMXOrderBuilder:
    """
    Строи и валидира ордери за GMX с възможност за log в trade_logger.
    """

    def __init__(self, strategy_name: str = "default_strategy", chain: str = "arbitrum"):
        self.strategy = strategy_name
        self.chain = chain

    # ----------------------------
    # Build Open Order
    # ----------------------------
    def build_open(self, trade_intent: dict) -> dict:
        order = {
            "strategy": self.strategy,
            "market": trade_intent["market"],
            "side": trade_intent["side"],
            "size_usd": float(trade_intent["size_usd"]),
            "leverage": float(trade_intent.get("leverage", 1)),
            "order_type": trade_intent.get("order_type", "market"),
            "slippage": float(trade_intent.get("slippage", 0.005)),
            "chain": self.chain,
        }
        logger.info(f"🟢 Build OPEN order: {order}")
        return order

    # ----------------------------
    # Build Close Order
    # ----------------------------
    def build_close(self, trade_intent: dict) -> dict:
        order = {
            "strategy": self.strategy,
            "market": trade_intent["market"],
            "side": "close_" + trade_intent["side"],
            "size_usd": float(trade_intent["size_usd"]),
            "order_type": trade_intent.get("order_type", "market"),
            "chain": self.chain,
        }
        logger.info(f"🔴 Build CLOSE order: {order}")
        return order

    # ----------------------------
    # Log order to trade_logger
    # ----------------------------
    def log_order(self, order: dict, entry_price: float = 0.0, exit_price: float = 0.0, pnl: float = 0.0):
        log_trade(
            strategy=order["strategy"],
            symbol=order["market"],
            side=order["side"],
            entry_price=entry_price,
            exit_price=exit_price,
            size=order["size_usd"],
            pnl=pnl,
            chain=order.get("chain", self.chain),
            notes="Built order"
        )
        logger.info(f"📄 Trade logged: {order['market']} | {order['side']}")
