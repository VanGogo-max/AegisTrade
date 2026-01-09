# FINAL
# Minimal GMX exchange adapter for routing

from exchange_adapter_base import ExchangeAdapterBase

class GMXAdapter(ExchangeAdapterBase):
    """
    GMX Adapter: interfaces with Execution Engine / Router.
    Does NOT execute trades directly in paper mode.
    """

    def __init__(self, name="gmx"):
        self.name = name

    def build_order(self, trade_intent):
        """
        Build order payload for GMX
        """
        return {
            "symbol": trade_intent["symbol"],
            "side": trade_intent["side"],
            "size_usd": trade_intent["size_usd"],
            "leverage": trade_intent.get("leverage", 1),
            "order_type": trade_intent.get("order_type", "market"),
        }

    def execute_order(self, order_payload, signer, tx_sender=None):
        """
        Execute the order via the given signer/tx_sender.
        If signer is simulated, returns a paper trade result.
        """
        if getattr(signer, "simulate", False):
            return {"status": "paper_executed", "order": order_payload}
        else:
            tx_result = tx_sender.send(order_payload) if tx_sender else {"tx": "dummy"}
            return {"status": "real_executed", "order": order_payload, "tx": tx_result}
