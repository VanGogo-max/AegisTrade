# gmx_tx_sender.py

from typing import Dict, Any
from web3 import Web3
from eth_account import Account

from gmx_gas_optimizer import GMXGasOptimizer
from gmx_sandwich_guard import GMXSandwichGuard
from gmx_mempool_watcher import GMXMempoolWatcher
from gmx_liquidity_monitor import GMXLiquidityMonitor


class GMXTxSender:
    """
    Builds, signs, and sends GMX transactions with full protection:
    - Mempool frontrun detection
    - MEV sandwich protection
    - Dynamic EIP-1559 gas optimization
    - Liquidity / OI / Funding rate checks
    """

    def __init__(
        self,
        web3: Web3,
        private_key: str,
        gas_optimizer: GMXGasOptimizer,
        sandwich_guard: GMXSandwichGuard,
        mempool_watcher: GMXMempoolWatcher,
        liquidity_monitor: GMXLiquidityMonitor,
        chain_id: int
    ):
        self.web3 = web3
        self.account = Account.from_key(private_key)
        self.gas_optimizer = gas_optimizer
        self.sandwich_guard = sandwich_guard
        self.mempool_watcher = mempool_watcher
        self.liquidity_monitor = liquidity_monitor
        self.chain_id = chain_id

    def _build_base_tx(self, to: str, data: bytes, value: int = 0) -> Dict[str, Any]:
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        gas_fees = self.gas_optimizer.get_optimized_fees()

        return {
            "from": self.account.address,
            "to": to,
            "data": data,
            "value": value,
            "nonce": nonce,
            "chainId": self.chain_id,
            "type": 2,  # EIP-1559
            "maxFeePerGas": gas_fees["maxFeePerGas"],
            "maxPriorityFeePerGas": gas_fees["maxPriorityFeePerGas"],
        }

    def _estimate_gas(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx["gas"] = int(gas_limit * 1.2)  # safety margin
        return tx

    def _mempool_precheck(self):
        """
        Scan pending transactions and boost gas if frontrun risk detected.
        """
        self.mempool_watcher.scan_pending_block()
        if self.mempool_watcher.should_emergency_boost():
            self.gas_optimizer.emergency_boost(multiplier=2.0)

    def _mev_precheck(
        self,
        pair: str,
        expected_price: float,
        expected_size: float,
        current_price: float
    ):
        """
        Evaluate MEV sandwich risk before sending the transaction.
        """
        risk = self.sandwich_guard.evaluate_trade_risk(
            pair=pair,
            expected_price=expected_price,
            expected_volume=expected_size,
            current_price=current_price
        )

        if risk["block_trade"]:
            raise RuntimeError(
                f"MEV Sandwich risk too high. Trade blocked. Details: {risk}"
            )

        if risk["risk_score"] >= 0.4:
            self.gas_optimizer.emergency_boost(multiplier=1.5)

    def _liquidity_precheck(self, pool_address: str):
        """
        Evaluate liquidity, OI and funding rate risk before sending the transaction.
        """
        risk = self.liquidity_monitor.evaluate_risk(pool_address)
        if risk["overall_risk"]:
            raise RuntimeError(
                f"Liquidity/OI/Funding risk detected. Transaction blocked. Details: {risk}"
            )

    def send_transaction(
        self,
        to: str,
        data: bytes,
        pair: str,
        expected_price: float,
        expected_size: float,
        current_price: float,
        pool_address: str,
        value: int = 0
    ) -> str:
        """
        Full protected execution pipeline:
        1) Mempool frontrun check
        2) Sandwich / MEV check
        3) Liquidity / OI / Funding check
        4) Gas optimization
        5) Build, sign, send transaction
        """

        # 1) Mempool frontrun защита
        self._mempool_precheck()

        # 2) MEV sandwich защита
        self._mev_precheck(
            pair=pair,
            expected_price=expected_price,
            expected_size=expected_size,
            current_price=current_price
        )

        # 3) Liquidity / OI / Funding защита
        self._liquidity_precheck(pool_address)

        # 4) Build TX
        tx = self._build_base_tx(to=to, data=data, value=value)
        tx = self._estimate_gas(tx)

        # 5) Sign
        signed = self.account.sign_transaction(tx)

        # 6) Send
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
