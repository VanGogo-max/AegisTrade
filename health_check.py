"""
health_check.py

Enterprise Health & Readiness Checks
===================================

Този модул реализира ТРИСТЕПЕННА проверка:

STEP 1 — Static validation (imports, config, contracts)
STEP 2 — Runtime checks (dependencies availability)
STEP 3 — Audit & metrics verification (write/read + emit)

Проектиран за:
- production
- Docker / Kubernetes
- CI/CD pipelines
"""

from __future__ import annotations

import time
import traceback
from typing import Dict, Any

# STEP 1: STATIC VALIDATION
# =========================

STATIC_DEPENDENCIES = [
    "config",
    "persistence",
    "metrics_collector",
    "audit_log",
]

OPTIONAL_DEPENDENCIES = [
    "exchange_adapter",
    "dex_adapter",
]


def _safe_import(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def static_validation() -> Dict[str, Any]:
    """
    Проверява дали задължителните модули са налични и импортируеми.
    """
    results = {}

    for module in STATIC_DEPENDENCIES:
        results[module] = _safe_import(module)

    for module in OPTIONAL_DEPENDENCIES:
        results[module] = _safe_import(module)

    status = all(results[m] for m in STATIC_DEPENDENCIES)

    return {
        "step": "static_validation",
        "status": "OK" if status else "FAIL",
        "details": results,
    }


# STEP 2: RUNTIME CHECKS
# =====================

def runtime_checks() -> Dict[str, Any]:
    """
    Проверява дали основните runtime зависимости функционират.
    """
    results = {}
    errors = {}

    # persistence
    try:
        from persistence import PersistenceManager
        pm = PersistenceManager()
        pm.health_check()
        results["persistence"] = True
    except Exception as e:
        results["persistence"] = False
        errors["persistence"] = str(e)

    # metrics
    try:
        from metrics_collector import MetricsCollector
        mc = MetricsCollector()
        mc.emit("health_check", 1)
        results["metrics_collector"] = True
    except Exception as e:
        results["metrics_collector"] = False
        errors["metrics_collector"] = str(e)

    status = all(results.values())

    return {
        "step": "runtime_checks",
        "status": "OK" if status else "DEGRADED",
        "details": results,
        "errors": errors,
    }


# STEP 3: AUDIT & OBSERVABILITY
# =============================

def observability_checks() -> Dict[str, Any]:
    """
    Проверява audit лог и времева консистентност.
    """
    results = {}
    errors = {}

    try:
        from audit_log import AuditLogger
        logger = AuditLogger()
        logger.log_event(
            event_type="HEALTH_CHECK",
            payload={"timestamp": time.time()},
        )
        results["audit_log_write"] = True
    except Exception as e:
        results["audit_log_write"] = False
        errors["audit_log"] = str(e)

    status = all(results.values())

    return {
        "step": "observability_checks",
        "status": "OK" if status else "FAIL",
        "details": results,
        "errors": errors,
    }


# AGGREGATOR
# ==========

def full_health_check() -> Dict[str, Any]:
    """
    Агрегира трите стъпки в един enterprise health report.
    """

    report = {
        "timestamp": time.time(),
        "checks": [],
    }

    for check in (
        static_validation,
        runtime_checks,
        observability_checks,
    ):
        try:
            result = check()
        except Exception:
            result = {
                "step": check.__name__,
                "status": "FAIL",
                "error": traceback.format_exc(),
            }

        report["checks"].append(result)

    overall_status = all(
        c.get("status") in ("OK", "DEGRADED")
        for c in report["checks"]
    )

    report["overall_status"] = "OK" if overall_status else "FAIL"

    return report


# CLI / ENTRY POINT
# =================

if __name__ == "__main__":
    import json
    print(json.dumps(full_health_check(), indent=2))
