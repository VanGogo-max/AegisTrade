# onchain_payment_checker.py
"""
On-Chain Payment Checker for USDT (ERC20) on Polygon

- Проверява дали даден адрес е получил точно определена сума USDT
- Филтрира по from, to, amount
- Работи чрез RPC и ERC20 Transfer events
"""

from web3 import Web3
from decimal import Decimal
from typing import Optional, Dict


class OnChainPaymentChecker:
    def __init__(self, rpc_url: str, usdt_contract: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.usdt = self.w3.eth.contract(
            address=Web3.to_checksum_address(usdt_contract),
            abi=self._erc20_abi()
        )

    def find_payment(
        self,
        from_address: str,
        to_address: str,
        amount_usdt: float,
        token: str,
        chain: str,
        lookback_blocks: int = 200_000,
    ) -> Optional[Dict]:

        decimals = self.usdt.functions.decimals().call()
        amount_raw = int(Decimal(amount_usdt) * (10 ** decimals))

        to_address = Web3.to_checksum_address(to_address)
        from_address = Web3.to_checksum_address(from_address)

        latest = self.w3.eth.block_number
        start = max(0, latest - lookback_blocks)

        events = self.usdt.events.Transfer.get_logs(
            fromBlock=start,
            toBlock=latest,
            argument_filters={
                "from": from_address,
                "to": to_address
            }
        )

        for ev in events:
            if ev["args"]["value"] == amount_raw:
                return {
                    "tx_hash": ev["transactionHash"].hex(),
                    "block_number": ev["blockNumber"],
                    "from": ev["args"]["from"],
                    "to": ev["args"]["to"],
                    "amount": float(amount_usdt),
                    "token": token,
                    "chain": chain,
                }

        return None

    @staticmethod
    def _erc20_abi():
        return [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"},
                ],
                "name": "Transfer",
                "type": "event",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            },
        ]
