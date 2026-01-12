# kwenta_tx_sender.py
"""
Kwenta Transaction Sender (FINAL)

Responsibility:
- Broadcast signed Kwenta transactions to the network
- Handle RPC submission
- Track tx hash
- No signing, no strategy, no risk logic

References:
- Kwenta / Synthetix Perps V2: https://docs.kwenta.io
"""

from typing import Dict, Any


class KwentaTxSendError(Exception):
    pass


class KwentaTxSender:
    def __init__(self, rpc_client):
        """
        rpc_client must implement:
            send_raw_transaction(tx_hex: str) -> str (tx_hash)
        """
        if rpc_client is None:
            raise KwentaTxSendError("RPC client is required")

        self._rpc = rpc_client

    def send(self, signed_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast signed transaction.

        Expected signed_payload:
            {
                "signed": True,
                "payload": {...},
                "signature": "0x..."
            }
        """
        if not signed_payload.get("signed"):
            raise KwentaTxSendError("Payload is not signed")

        try:
            tx_hex = self._build_raw_tx(signed_payload)
            tx_hash = self._rpc.send_raw_transaction(tx_hex)

            return {
                "status": "SUBMITTED",
                "tx_hash": tx_hash,
                "exchange": "Kwenta",
            }

        except Exception as exc:
            raise KwentaTxSendError("Failed to send Kwenta transaction") from exc

    def _build_raw_tx(self, signed_payload: Dict[str, Any]) -> str:
        """
        Assemble raw transaction bytes (simplified abstraction).
        Real implementation would use EIP-1559 encoding.
        """
        payload = signed_payload["payload"]
        signature = signed_payload["signature"]

        raw = f"KWENTA_TX|{payload}|SIG:{signature}"
        return raw
