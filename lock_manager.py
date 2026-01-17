# lock_manager.py
# Central Lock Manager for GRSM
# Thread-safe atomic locks

from threading import RLock

class LockManager:
    """
    Provides thread-safe global and per-resource locks.
    Can be extended for fine-grained locking per symbol or account.
    """

    def __init__(self):
        self.global_lock = RLock()
        self.symbol_locks = {}

    # ----------------- Global Lock -----------------
    def acquire_global(self):
        self.global_lock.acquire()

    def release_global(self):
        self.global_lock.release()

    def __enter__(self):
        self.acquire_global()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_global()

    # ----------------- Per-Symbol Lock -----------------
    def acquire_symbol(self, symbol: str):
        lock = self.symbol_locks.setdefault(symbol, RLock())
        lock.acquire()

    def release_symbol(self, symbol: str):
        lock = self.symbol_locks.get(symbol)
        if lock:
            lock.release()
