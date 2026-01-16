# gmx_tx_sender.py

from typing import Dict, Optional
from web3 import Web3
import time

class GMXTxSender:
    """
    Интеграция с GMX Perpetuals:
    - Изпълнява ордери от PositionManager
    - Поддържа partial close, move SL, close all
    """

    def __init__(self, web3: Web3, contract_address: str, private_key: str):
        self.web3 = web3
        self.contract_address = contract_address
        self.private_key = private_key
        self.nonce = self.web3.eth.get_transaction_count(self.web3.eth.default_account)

    def execute(self, command: Dict) -> Dict:
        """
        command = {
            "action": "OPEN" | "PARTIAL_CLOSE" | "MOVE_SL" | "CLOSE_ALL",
            "entry": float,
            "sl": float,
            "percent": float (за partial close)
        }
        """
        action = command.get("action")

        if action == "OPEN":
            return self._open_position(command)

        elif action == "PARTIAL_CLOSE":
            return self._partial_close(command)

        elif action == "MOVE_SL":
            return self._move_sl(command)

        elif action == "CLOSE_ALL":
            return self._close_all(command)

        else:
            return {"status": "UNKNOWN_ACTION", "action": action}

    def _open_position(self, cmd: Dict):
        # Примерен placeholder
        # Тук се създава GMX позиция с leverage, size, entry, sl
        tx = {
            "type": "open",
            "entry": cmd["entry"],
            "sl": cmd.get("sl")
        }
        self._send_tx(tx)
        return {"status": "OPEN_SENT", "entry": cmd["entry"], "sl": cmd.get("sl")}

    def _partial_close(self, cmd: Dict):
        # cmd["percent"] = част от позицията за затваряне
        tx = {
            "type": "partial_close",
            "percent": cmd["percent"]
        }
        self._send_tx(tx)
        return {"status": "PARTIAL_CLOSE_SENT", "percent": cmd["percent"]}

    def _move_sl(self, cmd: Dict):
        tx = {
            "type": "move_sl",
            "new_sl": cmd["new_sl"]
        }
        self._send_tx(tx)
        return {"status": "SL_MOVED", "new_sl": cmd["new_sl"]}

    def _close_all(self, cmd: Dict):
        tx = {"type": "close_all"}
        self._send_tx(tx)
        return {"status": "ALL_CLOSED"}

    def _send_tx(self, tx_data: Dict):
        """
        Реално изпращане на транзакция.
        Може да се адаптира за GMX контракт: increasePosition, decreasePosition, updatePosition
        """
        # Placeholder: просто симулираме забавяне
        print(f"[GMXTxSender] Sending tx: {tx_data}")
        time.sleep(0.1)
        # В реален сценарий:
        # - encode ABI
        # - web3.eth.send_transaction(...)
        self.nonce += 1
