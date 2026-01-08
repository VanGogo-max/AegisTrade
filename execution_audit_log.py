"""
execution_audit_log.py

Immutable execution audit log.

Purpose:
- Regulatory-grade traceability of all trade executions
- Post-incident analysis
- Compliance / forensic reconstruction
- Deterministic, append-only behavior

Design guarantees:
- NO mutation
- NO deletion
- NO external dependencies
- NO execution logic
"""

from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4
from threading import Lock


class AuditLogError(Exception):
    pass


class ExecutionAuditLog:
    """
    Append-only in-memory audit log.
    """

    _lock = Lock()
    _records: List[Dict[str, Any]] = []

    @classmethod
    def record(
        cls,
        *,
        intent_id: str,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        exchange: str,
        strategy: str,
        result: str,
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        """
        Record an execution event.

        Returns:
            audit_id (str)
        """
        if not intent_id:
            raise AuditLogError("intent_id is required")

        audit_id = str(uuid4())

        entry = {
            "audit_id": audit_id,
            "intent_id": intent_id,
            "symbol": symbol,
            "side": side,
            "quantity": float(quantity),
            "price": float(price),
            "exchange": exchange,
            "strategy": strategy,
            "result": result,
            "metadata": metadata or {},
            "timestamp_utc": datetime.utcnow().isoformat(),
        }

        with cls._lock:
            cls._records.append(entry)

        return audit_id

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        """
        Return a copy of all audit records.
        """
        with cls._lock:
            return list(cls._records)

    @classmethod
    def find_by_intent(cls, intent_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve audit records by intent_id.
        """
        with cls._lock:
            return [
                record
                for record in cls._records
                if record["intent_id"] == intent_id
            ]

    @classmethod
    def count(cls) -> int:
        """
        Total number of audit records.
        """
        with cls._lock:
            return len(cls._records)

    @classmethod
    def export_snapshot(cls) -> List[Dict[str, Any]]:
        """
        Export immutable snapshot (for persistence layer).
        """
        with cls._lock:
            return [record.copy() for record in cls._records]
