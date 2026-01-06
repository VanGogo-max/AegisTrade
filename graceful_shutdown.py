"""
graceful_shutdown.py

Centralized graceful shutdown handler.

Responsibilities:
- Capture OS termination signals
- Execute registered shutdown hooks
- Guarantee deterministic, single-run shutdown sequence

Notes:
- Hooks are executed in the order they were registered
- Failures in one hook do NOT stop the shutdown sequence
"""

import signal
import threading
import logging
from typing import Callable, List, Optional

ShutdownHook = Callable[[], None]


class GracefulShutdown:
    def __init__(self) -> None:
        self._hooks: List[ShutdownHook] = []
        self._lock = threading.Lock()
        self._shutdown_started = False
        self._logger = logging.getLogger("graceful_shutdown")

    def register_hook(self, hook: ShutdownHook) -> None:
        """
        Register a shutdown hook.

        Hooks are executed in the order of registration.
        """
        if not callable(hook):
            raise TypeError("Shutdown hook must be callable")

        with self._lock:
            self._hooks.append(hook)

    def _run_hooks(self) -> None:
        if not self._hooks:
            self._logger.info("No shutdown hooks registered")
            return

        for hook in self._hooks:
            try:
                hook()
            except Exception as exc:
                self._logger.exception(
                    "Shutdown hook failed",
                    extra={"error": str(exc)},
                )

    def shutdown(self, signum: Optional[int] = None, frame=None) -> None:
        """
        Initiates graceful shutdown.
        Safe to call multiple times – executes only once.
        """
        with self._lock:
            if self._shutdown_started:
                return
            self._shutdown_started = True

        self._logger.info(
            "Graceful shutdown initiated",
            extra={"signal": signum},
        )
        self._run_hooks()


_shutdown_manager = GracefulShutdown()


def register_shutdown_hook(hook: ShutdownHook) -> None:
    """
    Public API for registering shutdown hooks.
    """
    _shutdown_manager.register_hook(hook)


def setup_signal_handlers() -> None:
    """
    Attach SIGTERM and SIGINT handlers.
    """
    signal.signal(signal.SIGTERM, _shutdown_manager.shutdown)
    signal.signal(signal.SIGINT, _shutdown_manager.shutdown)
