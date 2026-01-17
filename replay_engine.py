# replay_engine.py
# Replay Engine for GRSM
# Restores state from snapshots and event logs
# Thread-safe

import threading

class ReplayEngine:
    """
    Replays events to restore ShadowLedger and RiskMonitor state.
    """

    def __init__(self, state_persistence, shadow_ledger, risk_monitor):
        self.state_persistence = state_persistence
        self.shadow_ledger = shadow_ledger
        self.risk_monitor = risk_monitor
        self._lock = threading.RLock()

    def replay(self):
        """
        Load latest snapshot and replay events.
        """
        with self._lock:
            snapshot = self.state_persistence.load_latest_snapshot()
            if snapshot:
                self._restore_snapshot(snapshot)

            events = self.state_persistence.load_event_log()
            for event in events:
                self._apply_event(event)

    # ----------------- Internal -----------------
    def _restore_snapshot(self, snapshot: dict):
        """
        Restore shadow ledger and risk monitor from snapshot
        """
        with self._lock:
            account = snapshot.get("account", {})
            positions = snapshot.get("positions", {})
            self.shadow_ledger.account.update(account)
            self.shadow_ledger.positions.update(positions)

            risk_state = snapshot.get("risk_state", {})
            if risk_state:
                self.risk_monitor.state.equity = risk_state.get("equity", self.risk_monitor.state.equity)
                self.risk_monitor.state.peak_equity = risk_state.get("peak_equity", self.risk_monitor.state.peak_equity)
                self.risk_monitor.state.daily_pnl = risk_state.get("daily_pnl", self.risk_monitor.state.daily_pnl)
                self.risk_monitor.state.open_exposure = risk_state.get("open_exposure", self.risk_monitor.state.open_exposure)
                self.risk_monitor.state.leverage = risk_state.get("leverage", self.risk_monitor.state.leverage)
                self.risk_monitor.state.halted = risk_state.get("halted", self.risk_monitor.state.halted)

    def _apply_event(self, event: dict):
        """
        Apply single event to shadow ledger and risk monitor
        """
        with self._lock:
            order = event.get("order")
            if order:
                self.shadow_ledger.simulate_order(order)

            risk_updates = event.get("risk_update")
            if risk_updates:
                self.risk_monitor.update_equity(risk_updates.get("equity", self.risk_monitor.state.equity))
                self.risk_monitor.update_daily_pnl(risk_updates.get("daily_pnl", self.risk_monitor.state.daily_pnl))
                self.risk_monitor.update_positions(risk_updates.get("open_exposure", self.risk_monitor.state.open_exposure),
                                                   risk_updates.get("leverage", self.risk_monitor.state.leverage))
