# vertex_signer.py
"""
Vertex Signer (FINAL)

Responsibility:
- Cryptographically sign Vertex order payloads
- Isolated from RPC, execution, and strategy layers
- Works with external key backend (HSM, Wallet, Vault, Ledger, etc.)

No network calls.
No transaction broadcasting.
"""

from typing import Dict, Any


class VertexSigningError(Exception):
    pass


class VertexSigner:
    def __init__(self, key_backend):
        """
        key_backend must implement:
            sign(message: bytes) -> bytes
        """
        if key_backend is None:
            raise VertexSigningError("Key backend is required")

        self._backend = key_backend

    def sign_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(order_payload, dict):
            raise VertexSigningError("Order payload must be dict")

        message = self._serialize(order_payload)
        signature = self._backend.sign(message)

        return {
            "exchange": "Vertex",
            "signed": True,
            "payload": order_payload,
            "signature": signature.hex(),
        }

    def _serialize(self, payload: Dict[str, Any]) -> bytes:
        try:
            items = sorted(payload.items(), key=lambda x: x[0])
            raw = "|".join(f"{k}={v}" for k, v in items)
            return raw.encode("utf-8")
        except Exception as exc:
            raise VertexSigningError("Serialization failed") from exc
