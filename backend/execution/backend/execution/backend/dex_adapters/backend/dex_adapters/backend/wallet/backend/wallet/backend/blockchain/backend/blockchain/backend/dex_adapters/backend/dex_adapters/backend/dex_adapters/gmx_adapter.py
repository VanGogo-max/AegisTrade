import json
from web3 import Web3
from backend.dex_adapters.base_adapter import BaseDexAdapter
from backend.wallet.wallet_manager import WalletManager


class GMXAdapter(BaseDexAdapter):

    def __init__(self):
        self.rpc = "https://arb1.arbitrum.io/rpc"
        self.web3 = Web3(Web3.HTTPProvider(self.rpc))

        # 👉 сложи твоя private key
        self.wallet = WalletManager("YOUR_PRIVATE_KEY")
        self.account = self.wallet.signer.account.address

        # GMX contracts (Arbitrum v1)
        self.position_router_address = Web3.to_checksum_address(
            "0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868"
        )

        self.reader_address = Web3.to_checksum_address(
            "0x22199a49A999c351eF7927602CFB187ec3cae489"
        )

        self.vault_address = Web3.to_checksum_address(
            "0x489ee077994B6658eAfA855C308275EAd8097C4A"
        )

        self.position_router = self.web3.eth.contract(
            address=self.position_router_address,
            abi=self._position_router_abi()
        )

        self.reader = self.web3.eth.contract(
            address=self.reader_address,
            abi=self._reader_abi()
        )

    # ---------------- ABI ----------------

    def _position_router_abi(self):
        return [
            {
                "inputs": [
                    {"type": "address[]", "name": "_path"},
                    {"type": "address", "name": "_indexToken"},
                    {"type": "uint256", "name": "_amountIn"},
                    {"type": "uint256", "name": "_minOut"},
                    {"type": "uint256", "name": "_sizeDelta"},
                    {"type": "bool", "name": "_isLong"},
                    {"type": "uint256", "name": "_acceptablePrice"},
                    {"type": "uint256", "name": "_executionFee"},
                    {"type": "bytes32", "name": "_referralCode"},
                    {"type": "address", "name": "_callbackTarget"},
                ],
                "name": "createIncreasePosition",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function",
            }
        ]

    def _reader_abi(self):
        return [
            {
                "inputs": [
                    {"type": "address", "name": "_vault"},
                    {"type": "address", "name": "_account"},
                    {"type": "address[]", "name": "_collateralTokens"},
                    {"type": "address[]", "name": "_indexTokens"},
                    {"type": "bool[]", "name": "_isLong"},
                ],
                "name": "getPositions",
                "outputs": [{"type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function",
            }
        ]

    # ---------------- EXECUTION ----------------

    async def place_order(self, symbol, side, size, price=None, order_type="market"):

        is_long = True if side == "buy" else False

        # USDC → WETH (пример)
        USDC = Web3.to_checksum_address(
            "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
        )
        WETH = Web3.to_checksum_address(
            "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
        )

        path = [USDC, WETH]
        index_token = WETH

        amount_in = self.web3.to_wei(10, "mwei")  # 10 USDC
        size_delta = int(size * 1e30)  # GMX precision

        acceptable_price = int(3000 * 1e30)  # примерна цена
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
            b"\x00" * 32,
            "0x0000000000000000000000000000000000000000",
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

    # ---------------- POSITION ----------------

    async def get_position(self, symbol):

        WETH = Web3.to_checksum_address(
            "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
        )

        collateral_tokens = [WETH]
        index_tokens = [WETH]
        is_long = [True]

        result = self.reader.functions.getPositions(
            self.vault_address,
            self.account,
            collateral_tokens,
            index_tokens,
            is_long
        ).call()

        if len(result) == 0:
            return {"size": 0}

        return {
            "size_usd": result[0] / 1e30,
            "collateral_usd": result[1] / 1e30,
            "entry_price": result[2] / 1e30,
            "pnl_usd": result[8] / 1e30,
        }

    # ---------------- CANCEL ----------------

    async def cancel_order(self, order_id):
        return {"status": "not_supported"}
