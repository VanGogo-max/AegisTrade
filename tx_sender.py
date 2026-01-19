# tx_sender.py
# Transaction sender for multi-chain DEX trades

import os
from web3 import Web3
from loguru import logger

# ----------------------------
# Configuration
# ----------------------------
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    logger.error("Private key not found in environment variables.")
    raise EnvironmentError("Set PRIVATE_KEY in your .env file.")

GAS_PRICE_MULTIPLIER = float(os.getenv("GAS_PRICE_MULTIPLIER", 1.1))

# ----------------------------
# Tx Sender Class
# ----------------------------
class TxSender:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.account = self.web3.eth.account.from_key(PRIVATE_KEY)
        logger.info(f"TxSender initialized for account {self.account.address}")

    # ----------------------------
    # Build and Send Raw Transaction
    # ----------------------------
    def send_tx(self, to: str, value: float = 0.0, data: bytes = b"", gas: int = 200_000, chain: str = ""):
        """
        Send a transaction to the blockchain.
        - to: contract or recipient address
        - value: ETH / native token amount
        - data: encoded call data
        - gas: gas limit
        - chain: optional, for logging
        """
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        gas_price = int(self.web3.eth.gas_price * GAS_PRICE_MULTIPLIER)
        tx = {
            "to": to,
            "value": self.web3.to_wei(value, "ether"),
            "data": data,
            "gas": gas,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": self.web3.eth.chain_id
        }
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info(f"🚀 Transaction sent | Chain: {chain or 'unknown'} | To: {to} | TxHash: {tx_hash.hex()}")
        return tx_hash.hex()

    # ----------------------------
    # Convenience: send_swap using DEXRouter
    # ----------------------------
    def send_swap(self, dex_router, from_token: str, to_token: str, amount: float, slippage: float = 0.003):
        """
        Execute a swap via the provided DEXRouter.
        - dex_router: instance of DEXRouter
        """
        # Placeholder: generate encoded calldata for swap
        # TODO: Implement actual router swap method call encoding
        data = b""  # encoded swap
        to_address = dex_router.router_address
        tx_hash = self.send_tx(to=to_address, value=0, data=data, chain=dex_router.chain)
        logger.info(f"💱 Swap submitted | {amount} {from_token} → {to_token} | TxHash: {tx_hash}")
        return tx_hash

# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    from dex_router import DEXRouter

    router = DEXRouter("ethereum")
    sender = TxSender(router.web3)
    tx_hash = sender.send_swap(router, from_token="0xTokenA", to_token="0xTokenB", amount=0.01)
    print(f"Swap TxHash: {tx_hash}")
