"""
gmx_real_signer.py — FINAL

GMX Real Transaction Signer.

Purpose:
- Sign GMX transaction payload with a real private key
- Produce a signed transaction ready for sending
- No network calls
- No execution logic

Security model:
- Private key is provided externally (env / secrets manager)
- This file NEVER stores keys
"""

from typing import Dict, Any
from eth_account import Account
from eth_account.signers.local import LocalAccount


class GMXSignerError(Exception):
    pass


class GMXRealSigner:
    """
    Signs GMX transactions using a real Ethereum private key.
    """

    def __init__(self, private_key: str):
        if not private_key:
            raise GMXSignerError("Private key is required")

        try:
            self._account: LocalAccount = Account.from_key(private_key)
        except Exception as exc:
            raise GMXSignerError(f"Invalid private key: {exc}")

    @property
    def address(self) -> str:
        return self._account.address

    def sign_transaction(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a prepared transaction payload.

        Expects tx_payload to include:
            - to
            - data
            - gas
            - gasPrice OR maxFeePerGas / maxPriorityFeePerGas
            - nonce
            - chainId
            - value (optional)

        Returns:
            Dict with signed transaction fields
        """
        required_fields = ["to", "data", "gas", "nonce", "chainId"]
        missing = [f for f in required_fields if f not in tx_payload]
        if missing:
            raise GMXSignerError(
                f"Transaction payload missing required fields: {missing}"
            )

        try:
            signed_tx = self._account.sign_transaction(tx_payload)
        except Exception as exc:
            raise GMXSignerError(f"Transaction signing failed: {exc}")

        return {
            "raw_transaction": signed_tx.rawTransaction,
            "tx_hash": signed_tx.hash.hex(),
            "from": self.address,
        }
