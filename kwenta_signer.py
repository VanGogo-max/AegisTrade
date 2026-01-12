# kwenta_signer.py
"""
Kwenta Signer (FINAL)

Responsibility:
- Signs Kwenta transaction payloads
- Isolated cryptographic layer
- No RPC sending, no strategy, no business logic

Design:
- Accepts raw order payload
- Returns signed transaction blob
- Key handling abstracted (HSM / Vault / WalletConnect / Local)

References:
- Synthetix / Kwenta Perps: https://docs.kwenta.io
"""

from typing import Dict, Any


class KwentaSigningError(Exception):
    pass


class KwentaSigner:
    def __init__(self, signer_backend):
        """
        signer_backend: abstraction over private key / wallet / HSM
        Must implement: sign(message: bytes) -> bytes
        """
        if signer_backend is None:
            raise KwentaSigningError("Signer backend is required")

        self._backend = signer_backend

    def sign_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signs Kwenta order payload.

        Returns:
            {
                "signed": True,
                "payload": original_payload,
                "signature": hex_string
            }
        """
        if not isinstance(order_payload, dict):
            raise KwentaSigningError("order_payload must be a dict")

        message = self._serialize(order_payload)
        signature = self._backend.sign(message)

        return {
            "signed": True,
            "payload": order_payload,
            "signature": signature.hex(),
        }

    def _serialize(self, payload: Dict[str, Any]) -> bytes:
        """
        Deterministic serialization for signing.
        """
        try:
            sorted_items = sorted(payload.items(), key=lambda x: x[0])
            raw = "|".join(f"{k}={v}" for k, v in sorted_items)
            return raw.encode("utf-8")
        except Exception as exc:
            raise KwentaSigningError("Failed to serialize payload") from exc
