
"""
Responsibility:
- Sign KCEX orders and transactions
- Abstract cryptographic layer (no real private keys here)
"""

import hashlib
import json
from typing import Dict

from kcex_order_builder import KCEXOrder


class KCEXSigner:
    def __init__(self, api_key: str = "demo_key", secret: str = "demo_secret"):
        self.api_key = api_key
        self.secret = secret

    def sign_order(self, order: KCEXOrder) -> Dict:
        payload = {
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "price": order.price,
            "leverage": order.leverage,
            "order_type": order.order_type,
        }

        signature = self._generate_signature(payload)

        return {
            "api_key": self.api_key,
            "payload": payload,
            "signature": signature,
        }

    def _generate_signature(self, payload: Dict) -> str:
        message = json.dumps(payload, sort_keys=True)
        raw = f"{message}{self.secret}".encode()
        return hashlib.sha256(raw).hexdigest()
kcex_signer.py
