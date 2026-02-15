import os
from typing import Dict, Any, Optional

from eth_account import Account
from web3 import Web3


# ============================================================
# EVM SIGNER (GMX, Kwenta, Apex, Vertex)
# ============================================================

class EvmDexSigner:

    def __init__(self, rpc_url: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        private_key = os.getenv("DEX_PRIVATE_KEY")
        if not private_key:
            raise ValueError("DEX_PRIVATE_KEY not set")

        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def build_tx(self, to: str, data: str, value: int = 0, gas: int = 300000):
        nonce = self.web3.eth.get_transaction_count(self.address)

        return {
            "to": to,
            "value": value,
            "gas": gas,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": nonce,
            "data": data,
            "chainId": self.web3.eth.chain_id,
        }

    def sign_and_send(self, tx: Dict[str, Any]) -> str:
        signed = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()


# ============================================================
# HYPERLIQUID SIGNER
# ============================================================

class HyperliquidSigner:
    """
    Hyperliquid uses off-chain signing.
    This is placeholder structure for integration.
    """

    def __init__(self):
        private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
        if not private_key:
            raise ValueError("HYPERLIQUID_PRIVATE_KEY not set")

        self.private_key = private_key

    def sign_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Replace with real Hyperliquid signing logic
        signed_payload = {
            "payload": order_payload,
            "signature": "hyperliquid_signature_placeholder"
        }
        return signed_payload


# ============================================================
# DYDX SIGNER
# ============================================================

class DydxSigner:
    """
    dYdX v4 uses separate signing model.
    """

    def __init__(self):
        private_key = os.getenv("DYDX_PRIVATE_KEY")
        if not private_key:
            raise ValueError("DYDX_PRIVATE_KEY not set")

        self.private_key = private_key

    def sign_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Replace with real dYdX signing logic
        signed_payload = {
            "payload": order_payload,
            "signature": "dydx_signature_placeholder"
        }
        return signed_payload


# ============================================================
# UNIFIED FACTORY
# ============================================================

class UnifiedDexSigner:

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url

    def evm(self) -> EvmDexSigner:
        if not self.rpc_url:
            raise ValueError("RPC URL required for EVM signer")
        return EvmDexSigner(self.rpc_url)

    def hyperliquid(self) -> HyperliquidSigner:
        return HyperliquidSigner()

    def dydx(self) -> DydxSigner:
        return DydxSigner()
