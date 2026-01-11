# hyperliquid_signer.py
"""
Hyperliquid Signer (FINAL)

Role:
- Cryptographically sign Hyperliquid orders
- Uses API key / secret (NOT wallet private keys)
- Produces authenticated request payloads
- No network calls
- No execution logic

Security:
- Secrets are injected from environment / vault
- No hardcoded keys
"""

import hmac
import hashlib
import time
from typing import Dict, Any


class HyperliquidSignerError(Exception):
    pass


class HyperliquidSigner:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise HyperliquidSignerError("API key and secret are required")

        self.api_key = api_key
        self.api_secret = api_secret.encode()

    def sign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign order payload with HMAC-SHA256
        """
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
