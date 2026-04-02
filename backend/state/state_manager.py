import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Dict


class StateManager:
    """
    Пази състоянието на бота:
    - текуща позиция
    - история на сделките с timestamps
    - баланс
    - атомарно записване (без риск от корупция)
    """

    def __init__(self, file_path: str = "backend/state/state.json"):
        self.file_path = file_path
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if not os.path.exists(self.file_path):
            return self._default_state()
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception:
            return self._default_state()

    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        tmp = self.file_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.state, f, indent=4)
        os.replace(tmp, self.file_path)

    def _default_state(self) -> Dict:
        return {
            "balance": 1000.0,
            "position": {"size_usd": 0, "entry_price": 0},
            "history": []
        }

    # ---------------- BALANCE ----------------

    def get_balance(self) -> float:
        return self.state.get("balance", 0.0)

    def update_balance(self, new_balance: float):
        self.state["balance"] = new_balance
        self.save()

    # ---------------- POSITION ----------------

    def get_position(self) -> Dict:
        return self.state.get("position", {})

    def update_position(self, position: Dict):
        self.state["position"] = position
        self.save()

    def clear_position(self):
        self.state["position"] = {"size_usd": 0, "entry_price": 0}
        self.save()

    # ---------------- HISTORY ----------------

    def add_trade(self, trade: Dict):
        trade["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.state.setdefault("history", []).append(trade)
        if len(self.state["history"]) > 500:
            self.state["history"] = self.state["history"][-500:]
        self.save()

    def get_history(self):
        return self.state.get("history", [])

    def get_last_trade(self):
        history = self.get_history()
        return history[-1] if history else None
