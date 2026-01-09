"""
GMX Transaction Signer Interface (FINAL)

Роля:
- Дефинира ясен интерфейс за подписване и изпращане на GMX транзакции
- Отделя execution логиката от wallet / signing механизма
- Позволява различни имплементации:
  - MetaMask / WalletConnect
  - Hardware wallet
  - External signer service

❌ НЕ съдържа private keys
❌ НЕ имплементира конкретен wallet
❌ НЕ зависи от GMX adapter-а

Проверими концепции:
- Separation of concerns (signing vs execution)
- Used in trading systems & blockchain clients

Източници:
- EIP-155: https://eips.ethereum.org/EIPS/eip-155
- Web3 signing concepts: https://docs.metamask.io/wallet/concepts/signing/
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class GMXTxSignerInterface(ABC):
    """
    Абстрактен интерфейс за GMX transaction signing.
    """

    @abstractmethod
    def sign_transaction(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Подписва подадения transaction payload.

        Вход:
            tx_payload – резултат от GMXExchangeAdapter
        Изход:
            подписана транзакция (raw tx или structured dict)
        """
        raise NotImplementedError

    @abstractmethod
    def send_transaction(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Изпраща вече подписаната транзакция към blockchain мрежата.

        Вход:
            signed_tx – резултат от sign_transaction()
        Изход:
            резултат от изпращането (tx_hash, status, errors)
        """
        raise NotImplementedError

    def sign_and_send(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience метод:
        sign → send в една стъпка.
        """
        signed_tx = self.sign_transaction(tx_payload)
        return self.send_transaction(signed_tx)
