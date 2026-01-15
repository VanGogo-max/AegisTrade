# gmx_mempool_watcher.py

import time
from typing import List, Dict
from web3 import Web3
from eth_typing import HexStr


class GMXMempoolWatcher:
    """
    Monitors mempool for GMX-related transactions and detects front-run risks.
    """

    def __init__(
        self,
        web3: Web3,
        gmx_contract_addresses: List[str],
        gas_spike_threshold_gwei: float = 50,
        lookback_seconds: int = 20
    ):
        self.web3 = web3
        self.gmx_contracts = [addr.lower() for addr in gmx_contract_addresses]
        self.gas_spike_threshold = self.web3.to_wei(gas_spike_threshold_gwei, "gwei")
        self.lookback_seconds = lookback_seconds

        self.recent_pending: List[Dict] = []

    def _is_gmx_tx(self, tx: Dict) -> bool:
        to_addr = tx.get("to")
        if not to_addr:
            return False
        return to_addr.lower() in self.gmx_contracts

    def _record_pending(self, tx: Dict):
        self.recent_pending.append({
            "hash": tx["hash"],
            "gasPrice": tx.get("gasPrice", 0),
            "maxFeePerGas": tx.get("maxFeePerGas", 0),
            "timestamp": time.time()
        })

        cutoff = time.time() - self.lookback_seconds
        self.recent_pending = [
            t for t in self.recent_pending if t["timestamp"] >= cutoff
        ]

    def scan_pending_block(self):
        block = self.web3.eth.get_block("pending", full_transactions=True)

        for tx in block.transactions:
            if self._is_gmx_tx(tx):
                self._record_pending(tx)

    def detect_gas_attack(self) -> bool:
        if not self.recent_pending:
            return False

        gas_values = []
        for tx in self.recent_pending:
            gas = tx["maxFeePerGas"] or tx["gasPrice"]
            if gas:
                gas_values.append(gas)

        if not gas_values:
            return False

        avg_gas = sum(gas_values) / len(gas_values)
        latest_gas = gas_values[-1]

        spike = latest_gas - avg_gas
        return spike > self.gas_spike_threshold

    def get_front_run_risk(self) -> Dict[str, float]:
        if not self.recent_pending:
            return {"risk": 0.0, "avg_gas": 0, "latest_gas": 0}

        gas_values = [
            tx["maxFeePerGas"] or tx["gasPrice"]
            for tx in self.recent_pending
            if tx["maxFeePerGas"] or tx["gasPrice"]
        ]

        avg_gas = sum(gas_values) / len(gas_values)
        latest_gas = gas_values[-1]

        risk_ratio = latest_gas / avg_gas if avg_gas else 0

        return {
            "risk": round(risk_ratio, 2),
            "avg_gas": int(avg_gas),
            "latest_gas": int(latest_gas)
        }

    def should_emergency_boost(self) -> bool:
        risk = self.get_front_run_risk()
        return risk["risk"] >= 1.5
