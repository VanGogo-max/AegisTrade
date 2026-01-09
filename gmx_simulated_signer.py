"""
GMX Simulated Signer (FINAL)

Роля:
- Симулира подписване и изпращане на GMX транзакции
- За демо / paper trading
- НЕ изпраща реални сделки on-chain
- Имплементира GMXTxSignerInterface
- Позволява тестване на стратегии без риск

Проверими концепции:
- Separation of concerns
- Sandbox / paper trading практики
- Used in trading systems: safe simulation before real execution
"""

from typing import Dict, Any
from gmx_tx_signer_interface import GMXTxSignerInterface
import time
import hashlib


class GMXSimulatedSigner(GMXTxSignerInterface):
    """
    Simulated signer за GMX (paper trading / demo)
    """

    def __init__(self, user_id: str = "demo_user"):
        """
        user_id: опционално, за да различава fake tx hash-ове
        """
        self.user_id = user_id

    def sign_transaction(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        „Подписва“ транзакцията, но всъщност генерира fake tx hash
        """
        tx_repr = f"{self.user_id}:{tx_payload}:{time.time()}"
        fake_hash = hashlib.sha256(tx_repr.encode()).hexdigest()
        return {
            "status": "simulated_signed",
            "tx_hash": fake_hash,
            "tx_payload": tx_payload,
        }

    def send_transaction(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        „Изпраща“ транзакцията, но реално връща симулиран резултат
        """
        return {
            "status": "simulated_submitted",
            "tx_hash": signed_tx["tx_hash"],
            "executed_at": int(time.time()),
            "tx_payload": signed_tx["tx_payload"],
            "result": {
                "profit_loss": 0,  # по избор: може да се random-изчислява за демо
                "executed": True,
            },
        }

    def sign_and_send(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience метод: sign → send
        """
        signed_tx = self.sign_transaction(tx_payload)
        return self.send_transaction(signed_tx)
