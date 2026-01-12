
"""
Apex Signer (FINAL)

Responsibility:
- Cryptographically sign Apex order payloads
- Isolated from RPC, execution and strategy layers
- Uses external key backend (HSM / Wallet / Vault / Ledger)

No network calls.
No transaction broadcasting.
"""

from typing import Dict, Any


class ApexSigningError(Exception):
    pass


class ApexSigner:
    def __init__(self, key_backend):
        """
        key_backend must implement:
            sign(message: bytes) -> bytes
        """
        if key_backend is None:
            raise ApexSigningError("Key backend is required")

        self._backend = key_backend

    def sign_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(order_payload, dict):
            raise ApexSigningError("Order payload must be dict")

        message = self._serialize(order_payload)
        signature = self._backend.sign(message)

        return {
            "exchange": "Apex",
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
            raise ApexSigningError("Serialization failed") from exc
apex_signer.py
