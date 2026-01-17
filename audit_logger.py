# audit_logger.py
import hashlib
import json
import os
import threading
import time
from typing import Dict, Any


class AuditLogger:
    """
    Tamper-proof audit log for all critical system events.
    Each record is hash-chained to the previous one (blockchain-like).
    """

    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self.lock = threading.Lock()
        self.last_hash = self._load_last_hash()

    def _load_last_hash(self) -> str:
        if not os.path.exists(self.log_file):
            return "0" * 64
        try:
            with open(self.log_file, "rb") as f:
                last_line = f.readlines()[-1]
                record = json.loads(last_line.decode())
                return record["hash"]
        except Exception:
            return "0" * 64

    def _hash_record(self, record: Dict[str, Any]) -> str:
        payload = json.dumps(record, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def log_event(self, event_type: str, data: Dict[str, Any]):
        with self.lock:
            record = {
                "timestamp": time.time(),
                "event_type": event_type,
                "data": data,
                "prev_hash": self.last_hash
            }
            record_hash = self._hash_record(record)
            record["hash"] = record_hash

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

            self.last_hash = record_hash

    def verify_chain(self) -> bool:
        """
        Verifies the integrity of the audit log chain.
        """
        if not os.path.exists(self.log_file):
            return True

        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        prev_hash = "0" * 64
        for line in lines:
            record = json.loads(line)
            expected = record["hash"]
            current = record.copy()
            del current["hash"]
            calc_hash = self._hash_record(current)
            if calc_hash != expected or record["prev_hash"] != prev_hash:
                return False
            prev_hash = expected

        return True
