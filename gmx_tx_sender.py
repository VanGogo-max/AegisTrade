# gmx_tx_sender.py

from typing import Dict, Any
from web3 import Web3
from eth_account import Account

from gmx_gas_optimizer import GMXGasOptimizer
from gmx_sandwich_guard import GMXSandwichGuard


class GMXTxSender:
    """
    Builds, signs and sends GMX transactions with:
    - EIP-1559 gas optimization
    - MEV sandwich protection (pre-trade risk check)
    """

    def __init__(
        self,
        web3: Web3,
        private_key: str,
        gas_optimizer: GMXGasOptimizer,
        sandwich_guard: GMXSandwichGuard,
        chain_id: int
    ):
        self.web3 = web3
        self.account = Account.from_key(private_key)
        self.gas_optimizer = gas_optimizer
        self.sandwich_guard = sandwich_guard
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

    def _mev_precheck(
        self,
        pair: str,
        expected_price: float,
        expected_size: float,
        current_price: float
    ):
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

        # ако рискът е повишен, вдигаме газ агресивно
        if risk["risk_score"] >= 0.4:
            self.gas_optimizer.emergency_boost(multiplier=1.5)

    def send_transaction(
        self,
        to: str,
        data: bytes,
        pair: str,
        expected_price: float,
        expected_size: float,
        current_price: float,
        value: int = 0
    ) -> str:
        """
        Full protected send:
        1) MEV sandwich check
        2) Gas optimization / boost if needed
        3) Build, sign, send
        """

        # 1) MEV защита
        self._mev_precheck(
            pair=pair,
            expected_price=expected_price,
            expected_size=expected_size,
            current_price=current_price
        )

        # 2) Build TX
        tx = self._build_base_tx(to=to, data=data, value=value)
        tx = self._estimate_gas(tx)

        # 3) Sign
        signed = self.account.sign_transaction(tx)

        # 4) Send
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
