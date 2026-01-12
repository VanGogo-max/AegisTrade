# vertex_tx_sender.py
"""
Vertex Transaction Sender (FINAL)

Responsibility:
- Broadcast signed Vertex transactions to the network
- Handle submission and return tx hash / status
- No signing, no strategy, no risk logic
"""

from typing import Dict, Any


class VertexTxSendError(Exception):
    pass


class VertexTxSender:
    def __init__(self, rpc_client):
        """
        rpc_client must implement:
            send_raw_transaction(tx_hex: str) -> str
        """
        if rpc_client is None:
            raise VertexTxSendError("RPC client is required")

        self._rpc = rpc_client

    def send(self, signed_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not signed_payload.get("signed"):
            raise VertexTxSendError("Payload is not signed")

        try:
            raw_tx = self._build_raw_tx(signed_payload)
            tx_hash = self._rpc.send_raw_transaction(raw_tx)

            return {
                "exchange": "Vertex",
                "status": "SUBMITTED",
                "tx_hash": tx_hash,
            }

        except Exception as exc:
            raise VertexTxSendError("Vertex transaction submission failed") from exc

    def _build_raw_tx(self, signed_payload: Dict[str, Any]) -> str:
        payload = signed_payload["payload"]
        signature = signed_payload["signature"]
        return f"VERTEX_TX|{payload}|SIG:{signature}"
