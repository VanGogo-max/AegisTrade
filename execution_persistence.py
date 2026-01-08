"""
execution_persistence.py

Execution persistence layer (WAL-like).

Purpose:
- Durable storage of execution & audit snapshots
- Crash recovery support
- Regulatory-grade trace retention
- Append-only semantics

Design constraints:
- NO execution logic
- NO mutation of existing records
- NO external dependencies
"""

import json
import os
from threading import Lock
from typing import List, Dict, Any
from datetime import datetime


class ExecutionPersistenceError(Exception):
    pass


class ExecutionPersistence:
    """
    Append-only persistence engine using JSON Lines format.
    """

    _lock = Lock()

    def __init__(self, storage_dir: str = "data"):
        self._storage_dir = storage_dir
        self._file_path = os.path.join(storage_dir, "execution_log.jsonl")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """
        Ensure persistence directory and file exist.
        """
        os.makedirs(self._storage_dir, exist_ok=True)
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w", encoding="utf-8"):
                pass

    def append(self, record: Dict[str, Any]) -> None:
        """
        Append a single immutable record.

        Record must be JSON-serializable.
        """
        if not isinstance(record, dict):
            raise ExecutionPersistenceError("Record must be a dict")

        payload = {
            "persisted_at_utc": datetime.utcnow().isoformat(),
            "record": record,
        }

        with self._lock:
            try:
                with open(self._file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload, separators=(",", ":")) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
            except OSError as exc:
                raise ExecutionPersistenceError(str(exc)) from exc

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Load all persisted records.
        """
        records: List[Dict[str, Any]] = []

        with self._lock:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        records.append(json.loads(line))
            except FileNotFoundError:
                return []
            except json.JSONDecodeError as exc:
                raise ExecutionPersistenceError(
                    "Corrupted persistence file"
                ) from exc

        return records

    def snapshot(self) -> List[Dict[str, Any]]:
        """
        Return immutable snapshot for recovery or backup.
        """
        return list(self.load_all())

    def count(self) -> int:
        """
        Number of persisted records.
        """
        return len(self.load_all())
