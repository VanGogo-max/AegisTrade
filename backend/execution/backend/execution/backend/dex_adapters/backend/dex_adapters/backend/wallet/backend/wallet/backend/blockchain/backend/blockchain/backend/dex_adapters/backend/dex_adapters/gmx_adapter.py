import json
from web3 import Web3
from backend.dex_adapters.base_adapter import BaseDexAdapter
from backend.wallet.wallet_manager import WalletManager


class GMXAdapter(BaseDexAdapter):

    def __init__(self):
        self.rpc = "https://arb1.arbitrum.io/rpc"
        self.web3 = Web3(Web3.HTTPProvider(self.rpc))

        self.wallet = WalletManager("YOUR_PRIVATE_KEY")
        self.account = self.wallet.signer.account.address

        self.position_router = self.web3.eth.contract(
            address=Web3.to_checksum_address("0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868"),
            abi=self._load_abi()
        )

    def _load_abi(self):
        with open("backend/blockchain/abi/gmx_position_router.json") as f:
            return json.load(f)

    async def place_order(self, symbol, side, size, price, order_type):

        is_long = True if side == "buy" else False

        # ⚠️ Примерни адреси (ETH/USDC)
        path = [
            Web3.to_checksum_address("0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"),  # USDC
            Web3.to_checksum_address("0x82af49447d8a07e3bd95bd0d56f35241523fbab1")   # WETH
        ]

        index_token = path[1]

        amount_in = self.web3.to_wei(10, "mwei")  # 10 USDC
        size_delta = self.web3.to_wei(size, "ether")

        acceptable_price = self.web3.to_wei(3000, "ether")  # пример

        execution_fee = self.web3.to_wei(0.0003, "ether")

        txn = self.position_router.functions.createIncreasePosition(
            path,
            index_token,
            amount_in,
            0,
            size_delta,
            is_long,
            acceptable_price,
            execution_fee,
            b"0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000"
        ).build_transaction({
            "from": self.account,
            "value": execution_fee,
            "gas": 700000,
            "gasPrice": self.web3.to_wei("1", "gwei"),
            "nonce": self.web3.eth.get_transaction_count(self.account),
        })

        signed_tx = self.wallet.sign_transaction(txn)

        tx_hash = self.web3.eth.send_raw_transaction(signed_tx)

        return {
            "status": "submitted",
            "tx_hash": tx_hash.hex()
        }

    async def cancel_order(self, order_id):
        return {"status": "not_supported"}

    async def get_position(self, symbol):
        return {"status": "not_implemented"}
