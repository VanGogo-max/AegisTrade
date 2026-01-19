# gmx_tx_sender.py
# GMX Transaction Sender — подписва и изпраща ордери чрез TxSender

from loguru import logger
from tx_sender import TxSender

class GMXTxSender:
    """
    Wrapper за TxSender специално за GMX.
    """

    def __init__(self, tx_sender: TxSender):
        self.tx_sender = tx_sender

    # ----------------------------
    # Send Open Order
    # ----------------------------
    def send_open(self, order: dict) -> dict:
        """
        Изпраща open ордер към GMX.
        """
        logger.info(f"🚀 Sending OPEN order: {order['market']} | {order['side']} | Size: {order['size_usd']}")
        signed_tx = self._sign_order(order)
        tx_hash = self.tx_sender.send(signed_tx)
        return {"tx_hash": tx_hash, "order": order}

    # ----------------------------
    # Send Close Order
    # ----------------------------
    def send_close(self, order: dict) -> dict:
        """
        Изпраща close ордер към GMX.
        """
        logger.info(f"🛑 Sending CLOSE order: {order['market']} | {order['side']} | Size: {order['size_usd']}")
        signed_tx = self._sign_order(order)
        tx_hash = self.tx_sender.send(signed_tx)
        return {"tx_hash": tx_hash, "order": order}

    # ----------------------------
    # Internal signing method
    # ----------------------------
    def _sign_order(self, order: dict) -> dict:
        """
        Placeholder за подписване на ордера.
        В реален проект трябва да се интегрира с signer / non-custodial key.
        """
        # TODO: implement actual signing logic
        logger.debug(f"🔑 Signing order: {order['market']} | {order['side']}")
        return order  # засега връща dict като mock signed_tx

# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    from tx_sender import TxSender

    mock_tx_sender = TxSender(web3=None)  # замести с реален Web3 instance
    gmx_sender = GMXTxSender(mock_tx_sender)

    test_order = {
        "market": "ETH/USD",
        "side": "long",
        "size_usd": 1000,
        "strategy": "default_strategy",
        "chain": "arbitrum",
    }

    tx_result = gmx_sender.send_open(test_order)
    print(f"Tx submitted: {tx_result['tx_hash']}")
