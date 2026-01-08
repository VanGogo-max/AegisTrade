# startup_guard.py
"""
Startup initialization guard.

Purpose:
- Enforce strict, ordered application startup
- Prevent partial or unsafe initialization
- Fail-fast on missing or out-of-order steps

No business logic.
Standard library only.
"""

from enum import Enum, auto


class StartupError(Exception):
    """Raised when startup sequence is violated."""


class StartupStep(Enum):
    CONFIG_LOADED = auto()
    ENV_VALIDATED = auto()
    SECRETS_LOADED = auto()
    OBSERVABILITY_READY = auto()
    SYSTEM_READY = auto()


class StartupGuard:
    _current_index: int = 0
    _locked: bool = False

    _ORDER = (
        StartupStep.CONFIG_LOADED,
        StartupStep.ENV_VALIDATED,
        StartupStep.SECRETS_LOADED,
        StartupStep.OBSERVABILITY_READY,
        StartupStep.SYSTEM_READY,
    )

    @classmethod
    def complete(cls, step: StartupStep) -> None:
        """
        Mark a startup step as completed.
        Must follow strict order.
        """
        if cls._locked:
            raise StartupError("Startup already completed")

        expected = cls._ORDER[cls._current_index]
        if step is not expected:
            raise StartupError(
                f"Startup order violation: expected {expected.name}, "
                f"got {step.name}"
            )

        cls._current_index += 1

        if step is StartupStep.SYSTEM_READY:
            cls._locked = True

    @classmethod
    def is_ready(cls) -> bool:
        return cls._locked

    @classmethod
    def assert_ready(cls) -> None:
        if not cls._locked:
            raise StartupError("System accessed before startup completion")
