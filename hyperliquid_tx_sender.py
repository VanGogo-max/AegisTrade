# hyperliquid_tx_sender.py
"""
Hyperliquid TX Sender (FINAL)

Role:
- Send signed orders to Hyperliquid REST / WebSocket API
- Handle network I/O only
- No signing
- No strategy
- No risk logic

Used by:
- hyperliquid_order_executor
- hyperliquid_failover_manager
"""

import requests
from typing import Dict, Any


class HyperliquidTxSendError(Exception):
    pass


class HyperliquidTxSender:
    def __init__(self, api_url: str, timeout: int = 10):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def send(self, signed_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast signed order to Hyperliquid.
        """
        try:
            response = requests.post(
                url=f"{self.api_url}/order",
                json=signed_payload,
                timeout=self.timeout,
            )
        except Exception as exc:
            raise HyperliquidTxSendError(f"Network error: {exc}") from exc

        if response.status_code != 200:
            raise HyperliquidTxSendError(
                f"Hyperliquid API error {response.status_code}: {response.text}"
            )

        data = response.json()
        if "order_id" not in data:
            raise HyperliquidTxSendError("Invalid Hyperliquid response (missing order_id)")

        return {
            "status": "SUBMITTED",
            "order_id": data["order_id"],
            "raw": data,
        }
