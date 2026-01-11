# dydx_signer.py
"""
dYdX v4 Signer (FINAL)

Role:
- Sign dYdX v4 orders with API key / secret
- HMAC-based auth (no wallet keys here)
- No network calls
- No execution logic
"""

import hmac
import hashlib
import time
from typing import Dict, Any


class DydxSignerError(Exception):
    pass


class DydxSigner:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise DydxSignerError("API key and secret are required")
        self.api_key = api_key
        self.api_secret = api_secret.encode()

    def sign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = int(time.time() * 1000)
        message = f"{timestamp}:{payload}".encode()

        signature = hmac.new(
            self.api_secret,
            message,
            hashlib.sha256
        ).hexdigest()

        return {
            "api_key": self.api_key,
            "timestamp": timestamp,
            "signature": signature,
            "payload": payload,
        }
