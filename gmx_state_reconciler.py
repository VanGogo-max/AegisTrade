# gmx_state_reconciler.py
"""
GMX State Reconciler (FINAL)

Role:
- Reconcile on-chain GMX state with internal account state
- Detect desync between:
    - positions
    - margin
    - open orders
    - liquidation thresholds
- Acts as single source of truth validator before any execution

Works with:
- gmx_account_state.py
- gmx_margin_monitor.py
- gmx_tx_confirm_watcher.py
- gmx_reorg_protector.py
"""

from typing import Dict, Any
import time


class GMXStateDesyncError(Exception):
    pass


class GMXStateReconciler:
    def __init__(self, account_state, margin_monitor, tx_watcher, reorg_protector):
        self.account_state = account_state
        self.margin_monitor = margin_monitor
        self.tx_watcher = tx_watcher
        self.reorg_protector = reorg_protector

    def reconcile(self) -> Dict[str, Any]:
        """
        Perform full reconciliation cycle.
        """
        self.reorg_protector.assert_chain_finality()
        onchain_state = self.account_state.fetch_onchain_state()
        local_state = self.account_state.get_local_state()

        self._compare_positions(onchain_state, local_state)
        self._compare_margin(onchain_state, local_state)
        self._verify_pending_txs()
        self.margin_monitor.assert_safe_margin(onchain_state)

        return {
            "status": "RECONCILED",
            "timestamp": int(time.time()),
            "positions": onchain_state.get("positions"),
            "equity": onchain_state.get("equity"),
        }

    def _compare_positions(self, onchain: Dict, local: Dict) -> None:
        if onchain.get("positions") != local.get("positions"):
            raise GMXStateDesyncError("Position mismatch between local and on-chain state")

    def _compare_margin(self, onchain: Dict, local: Dict) -> None:
        if abs(onchain.get("margin") - local.get("margin")) > 1e-6:
            raise GMXStateDesyncError("Margin mismatch between local and on-chain state")

    def _verify_pending_txs(self) -> None:
        unconfirmed = self.tx_watcher.get_unconfirmed_transactions()
        if unconfirmed:
            raise GMXStateDesyncError(f"Pending unconfirmed transactions: {unconfirmed}")
