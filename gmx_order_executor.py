# gmx_order_executor.py
"""
GMX Order Executor

Роля:
- Последен слой преди on-chain изпращане
- Не съдържа стратегия
- Не съдържа риск логика
- Само изпълнява вече валидирани ордери

Поток:
Strategy -> Risk Engine -> GMXOrderBuilder -> GMXOrderExecutor -> GMXTxSender -> Chain
"""

from typing import Dict, Any
from loguru import logger
from trade_logger import log_trade


class GMXExecutionError(Exception):
    pass


class GMXOrderExecutor:
    def __init__(self, order_builder, tx_sender):
        self.order_builder = order_builder
        self.tx_sender = tx_sender

    # ----------------------------
    # OPEN POSITION
    # ----------------------------
    def execute_open(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        order = self.order_builder.build_open(trade_intent)
        receipt = self.tx_sender.send_open(order)
        result = self._build_result("OPEN", order, receipt)
        self._log(order, result)
        return result

    # ----------------------------
    # CLOSE POSITION
    # ----------------------------
    def execute_close(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        order = self.order_builder.build_close(trade_intent)
        receipt = self.tx_sender.send_close(order)
        result = self._build_result("CLOSE", order, receipt)
        self._log(order, result)
        return result

    # ----------------------------
    # RESULT FORMAT
    # ----------------------------
    def _build_result(self, action: str, order: dict, receipt: dict) -> dict:
        if "tx_hash" not in receipt:
            raise GMXExecutionError("Transaction broadcast failed")

        return {
            "status": "SUBMITTED",
            "exchange": "GMX",
            "action": action,
            "market": order["market"],
            "side": order["side"],
            "size_usd": order["size_usd"],
            "chain": order["chain"],
            "tx_hash": receipt["tx_hash"],
            "block": receipt.get("block_number"),
        }

    # ----------------------------
    # TRADE LOGGING
    # ----------------------------
    def _log(self, order: dict, result: dict):
        log_trade(
            strategy=order["strategy"],
            symbol=order["market"],
            side=order["side"],
            entry_price=order.get("entry_price", 0.0),
            exit_price=order.get("exit_price", 0.0),
            size=order["size_usd"],
            pnl=order.get("pnl", 0.0),
            chain=order["chain"],
            notes=f"{result['action']} via GMXExecutor | tx={result['tx_hash']}"
        )
        logger.info(
            f"📤 GMX {result['action']} | {order['market']} | {order['side']} | "
            f"{order['size_usd']}$ | Tx: {result['tx_hash']}"
        )
