# risk_monitor.py
# Central Risk & Fail-Safe Engine for GRSM
# Production-ready, thread-safe

import threading
import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskLimits:
    max_drawdown_pct: float = 0.25        # 25%
    max_daily_loss_pct: float = 0.10      # 10%
    max_leverage: float = 5.0
    max_position_pct: float = 0.20        # 20% of equity per asset
    max_correlated_exposure_pct: float = 0.50
    volatility_spike_threshold: float = 3.0  # std dev multiplier


@dataclass
class RiskState:
    equity: float
    peak_equity: float
    daily_pnl: float = 0.0
    open_exposure: Dict[str, float] = field(default_factory=dict)
    leverage: float = 0.0
    halted: bool = False
    last_update_ts: float = field(default_factory=time.time)


class RiskMonitor:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.state = None
        self._lock = threading.RLock()
        self._halt_flag = threading.Event()

    def initialize(self, starting_equity: float):
        with self._lock:
            self.state = RiskState(
                equity=starting_equity,
                peak_equity=starting_equity
            )

    # ----------------- State Updates -----------------

    def update_equity(self, new_equity: float):
        with self._lock:
            if self._halt_flag.is_set():
                return
            self.state.equity = new_equity
            self.state.peak_equity = max(self.state.peak_equity, new_equity)
            self._check_all()

    def update_daily_pnl(self, pnl: float):
        with self._lock:
            self.state.daily_pnl = pnl
            self._check_all()

    def update_positions(self, exposure_by_asset: Dict[str, float], leverage: float):
        with self._lock:
            self.state.open_exposure = exposure_by_asset
            self.state.leverage = leverage
            self._check_all()

    # ----------------- Risk Checks -----------------

    def _check_drawdown(self):
        dd = 1.0 - (self.state.equity / self.state.peak_equity)
        return dd <= self.limits.max_drawdown_pct

    def _check_daily_loss(self):
        loss_pct = abs(self.state.daily_pnl) / self.state.peak_equity
        return loss_pct <= self.limits.max_daily_loss_pct

    def _check_leverage(self):
        return self.state.leverage <= self.limits.max_leverage

    def _check_position_size(self):
        for asset, value in self.state.open_exposure.items():
            if value / self.state.equity > self.limits.max_position_pct:
                return False
        return True

    def _check_correlated_exposure(self):
        total_exposure = sum(self.state.open_exposure.values())
        return (total_exposure / self.state.equity) <= self.limits.max_correlated_exposure_pct

    # ----------------- Global Evaluation -----------------

    def _check_all(self):
        if not self._check_drawdown():
            self._trigger_halt("MAX_DRAWDOWN_EXCEEDED")
        elif not self._check_daily_loss():
            self._trigger_halt("MAX_DAILY_LOSS_EXCEEDED")
        elif not self._check_leverage():
            self._trigger_halt("MAX_LEVERAGE_EXCEEDED")
        elif not self._check_position_size():
            self._trigger_halt("MAX_POSITION_SIZE_EXCEEDED")
        elif not self._check_correlated_exposure():
            self._trigger_halt("MAX_CORRELATED_EXPOSURE_EXCEEDED")

    # ----------------- Fail-Safe -----------------

    def _trigger_halt(self, reason: str):
        if not self._halt_flag.is_set():
            self._halt_flag.set()
            self.state.halted = True
            self._persist_state(reason)
            self._notify_shutdown_hooks(reason)

    def is_halted(self) -> bool:
        return self._halt_flag.is_set()

    # ----------------- Hooks -----------------

    def _persist_state(self, reason: str):
        # To be connected with persistence layer
        print(f"[RISK] Persisting state due to: {reason}")

    def _notify_shutdown_hooks(self, reason: str):
        # To be connected with orchestrator / GRSM / execution router
        print(f"[RISK] EMERGENCY HALT TRIGGERED: {reason}")
