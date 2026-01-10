# gmx_order_executor.py
"""
GMX Order Executor (FINAL)

Role:
- Final execution layer before on-chain submission
- Connects:
    execution_engine
    exchange_router
    gmx_order_builder
    gmx_real_signer / gmx_simulated_signer
    gmx_tx_sender
- Supports:
    - paper trading
    - real trading
- Guarantees:
    - deterministic execution flow
    - no strategy logic
    - no risk logic (already validated)
"""

from typing import Dict, Any


class GMXExecutionError(Exception):
    pass


class GMXOrderExecutor:
    def __init__(
        self,
        order_builder,
        signer,
        tx_sender,
    ):
        self.order_builder = order_builder
        self.signer = signer
        self.tx_sender = tx_sender

    def execute_open(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        tx = self.order_builder.build_open(trade_intent)
        signed_tx = self.signer.sign(tx)
        receipt = self.tx_sender.send(signed_tx)
        return self._result("OPEN", trade_intent, receipt)

    def execute_close(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        tx = self.order_builder.build_close(trade_intent)
        signed_tx = self.signer.sign(tx)
        receipt = self.tx_sender.send(signed_tx)
        return self._result("CLOSE", trade_intent, receipt)

    def _result(self, action: str, intent: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, Any]:
        if not receipt.get("tx_hash"):
            raise GMXExecutionError("Transaction failed to broadcast")

        return {
            "status": "SUBMITTED",
            "action": action,
            "exchange": "GMX",
            "market": intent["market"],
            "side": intent["side"],
            "size_usd": intent["size_usd"],
            "tx_hash": receipt["tx_hash"],
            "block": receipt.get("block_number"),
        }
