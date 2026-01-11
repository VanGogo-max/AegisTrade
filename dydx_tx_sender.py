# dydx_tx_sender.py
"""
dYdX v4 TX Sender (FINAL)

Role:
- Send signed orders to dYdX v4 API
- Handle network I/O only
- No signing
- No strategy
- No risk logic
"""

import requests
from typing import Dict, Any


class DydxTxSendError(Exception):
    pass


class DydxTxSender:
    def __init__(self, api_url: str, timeout: int = 10):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def send(self, signed_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                url=f"{self.api_url}/orders",
                json=signed_payload,
                timeout=self.timeout,
            )
        except Exception as exc:
            raise DydxTxSendError(f"Network error: {exc}") from exc

        if response.status_code != 200:
            raise DydxTxSendError(
                f"dYdX API error {response.status_code}: {response.text}"
            )

        data = response.json()
        if "orderId" not in data:
            raise DydxTxSendError("Invalid dYdX response (missing orderId)")

        return {
            "status": "SUBMITTED",
            "order_id": data["orderId"],
            "raw": data,
        }
