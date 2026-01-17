# global_risk_state_manager.py
# Central Risk State Manager for GRSM
# Coordinates RiskMonitor, ShadowLedger, and LockManager

import threading

class GlobalRiskStateManager:
    """
    Provides a single interface for updating and querying global risk state.
    Ensures thread-safe access and atomic updates.
    """

    def __init__(self, risk_monitor, shadow_ledger, lock_manager):
        self.risk_monitor = risk_monitor
        self.shadow_ledger = shadow_ledger
        self.lock_manager = lock_manager
        self._lock = threading.RLock()

    # ----------------- Equity and Risk Updates -----------------
    def update_equity(self, new_equity: float):
        with self._lock:
            self.risk_monitor.update_equity(new_equity)

    def update_daily_pnl(self, pnl: float):
        with self._lock:
            self.risk_monitor.update_daily_pnl(pnl)

    def update_positions(self, positions: dict, leverage: float):
        with self._lock:
            self.risk_monitor.update_positions(positions, leverage)

    # ----------------- Risk Queries -----------------
    def is_trading_halted(self):
        with self._lock:
            return self.risk_monitor.is_halted()

    def get_risk_snapshot(self):
        with self._lock:
            state = self.risk_monitor.state
            return {
                "equity": state.equity,
                "peak_equity": state.peak_equity,
                "daily_pnl": state.daily_pnl,
                "open_exposure": state.open_exposure.copy(),
                "leverage": state.leverage,
                "halted": state.halted
            }

    # ----------------- Atomic Operations -----------------
    def atomic_update(self, func, *args, **kwargs):
        """
        Execute a function atomically with respect to risk state and shadow ledger
        """
        with self.lock_manager.global_lock:
            return func(*args, **kwargs)
