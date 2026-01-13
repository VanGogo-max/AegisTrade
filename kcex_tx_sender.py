# kcex_tx_sender.py
"""
Responsibility:
- Send signed orders to KCEX (simulated)
- Return execution result
"""

from typing import Dict
import uuid
import time


class KCEXTxSender:
    def __init__(self):
        self._connected = True

    def is_connected(self) -> bool:
        return self._connected

    def send(self, signed_payload: Dict) -> Dict:
        if not self._connected:
            raise ConnectionError("KCEX API not reachable")

        # Simulate network latency
        time.sleep(0.2)

        tx_id = str(uuid.uuid4())

        return {
            "tx_id": tx_id,
            "status": "FILLED",
            "exchange": "KCEX",
            "payload": signed_payload,
            "timestamp": time.time(),
        }
