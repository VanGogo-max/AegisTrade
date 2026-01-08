# runtime_guard.py
"""
Runtime access guard.

Purpose:
- Prevent access to system components before full startup
- Enforce runtime safety boundaries
- Provide explicit, centralized runtime checks

No business logic.
Standard library only.
"""

from functools import wraps
from startup_guard import StartupGuard


class RuntimeGuardError(Exception):
    """Raised when runtime access is attempted before system readiness."""


class RuntimeGuard:
    @staticmethod
    def assert_ready(component: str | None = None) -> None:
        """
        Hard runtime check.
        """
        if not StartupGuard.is_ready():
            name = f" ({component})" if component else ""
            raise RuntimeGuardError(
                f"Runtime access denied{name}: system not ready"
            )

    @staticmethod
    def guarded(component: str | None = None):
        """
        Decorator enforcing runtime readiness.
        """

        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                RuntimeGuard.assert_ready(component)
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def context(component: str | None = None):
        """
        Context manager enforcing runtime readiness.
        """

        class _RuntimeContext:
            def __enter__(self):
                RuntimeGuard.assert_ready(component)

            def __exit__(self, exc_type, exc, tb):
                return False

        return _RuntimeContext()
