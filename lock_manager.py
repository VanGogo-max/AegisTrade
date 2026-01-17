# core/risk/lock_manager.py

from threading import RLock

class LockManager:
    """
    Централен мениджър за lock-ове.
    Може да се разширява за multi-resource locking или per-symbol locking.
    """

    def __init__(self):
        self.global_lock = RLock()
        # Може да се добави dict за per-symbol lock:
        # self.symbol_locks = {}

    def acquire(self):
        """
        Acquire глобален lock
        """
        self.global_lock.acquire()

    def release(self):
        """
        Release глобален lock
        """
        self.global_lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
