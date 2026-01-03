import json
import os
import threading
from datetime import datetime
from typing import Dict, Any, List


class AuditLogger:
    """
    Append-only audit лог.
    Използва се за compliance, сигурност и админ панел.
    """

    def __init__(self, log_file: str = "audit_log.jsonl"):
        self.log_file = log_file
        self._lock = threading.Lock()

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8"):
                pass

    def _write(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log(self, level: str, event_type: str, payload: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "event_type": event_type,
            "payload": payload
        }
        self._write(entry)

    # === Convenience methods ===

    def info(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.log("INFO", event_type, payload)

    def warning(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.log("WARNING", event_type, payload)

    def error(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.log("ERROR", event_type, payload)

    def read_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
