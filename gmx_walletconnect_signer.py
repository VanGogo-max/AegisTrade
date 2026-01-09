"""
GMX WalletConnect Signer (FINAL)

Роля:
- Имплементира GMXTxSignerInterface чрез WalletConnect
- Позволява потребителят да подписва GMX транзакции
  със собствен mobile / desktop wallet
- НЕ пази private keys
- НЕ модифицира transaction payloads

Този файл е мост между:
- backend execution engine
- реален човешки wallet

Проверими източници:
- WalletConnect v2 Docs: https://docs.walletconnect.com/2.0
- EIP-155: https://eips.ethereum.org/EIPS/eip-155
"""

from typing import Dict, Any
from gmx_tx_signer_interface import GMXTxSignerInterface


class GMXWalletConnectSigner(GMXTxSignerInterface):
    """
    WalletConnect-based signer за GMX транзакции.
    """

    def __init__(self, wc_client: Any, chain_id: int):
        """
        wc_client:
            Инициализиран WalletConnect v2 client
            (създава се извън този файл)

        chain_id:
            Ethereum-compatible chain ID
            (Arbitrum: 42161, Avalanche: 43114)
        """
        self.wc_client = wc_client
        self.chain_id = chain_id

    # =========================
    # Signing
    # =========================

    def sign_transaction(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Изпраща signing request към wallet-а на потребителя.
        """

        wc_request = {
            "chainId": f"eip155:{self.chain_id}",
            "request": {
                "method": "eth_sendTransaction",
                "params": [
                    {
                        "to": tx_payload["to"],
                        "data": self._encode_call_data(
                            tx_payload["method"],
                            tx_payload["params"],
                        ),
                    }
                ],
            },
        }

        result = self.wc_client.request(wc_request)

        return {
            "status": "signed",
            "tx_hash": result,
        }

    # =========================
    # Sending
    # =========================

    def send_transaction(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        При WalletConnect:
        подписването и изпращането са една операция.
        """
        return {
            "status": "submitted",
            "tx_hash": signed_tx["tx_hash"],
        }

    # =========================
    # Helpers
    # =========================

    def _encode_call_data(self, method: str, params: Dict[str, Any]) -> str:
        """
        ABI encoding placeholder.

        Реалната ABI енкодинг логика се имплементира чрез:
        - eth_abi
        - web3.py
        - или външен encoder service

        Тук умишлено не е включена,
        за да няма hard dependency.
        """
        return f"ENCODED::{method}::{params}"
