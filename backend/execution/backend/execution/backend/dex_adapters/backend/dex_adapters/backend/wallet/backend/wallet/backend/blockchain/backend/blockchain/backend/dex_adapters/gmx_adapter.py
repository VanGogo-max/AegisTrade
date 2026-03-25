from web3 import Web3
from backend.dex_adapters.base_adapter import BaseDexAdapter
from backend.blockchain.web3_provider import Web3Provider
from backend.wallet.wallet_manager import WalletManager


class GMXAdapter(BaseDexAdapter):

    def __init__(self):
        self.rpc = "https://arb1.arbitrum.io/rpc"
        self.web3 = Web3Provider(self.rpc).get_web3()

        # TODO: сложи реален private key
        self.wallet = WalletManager("YOUR_PRIVATE_KEY")

        self.account = self.wallet.signer.account.address

    async def place_order(self, symbol, side, size, price, order_type):
        # ⚠️ Това е примерна структура (GMX използва сложни контракти)

        tx = {
            "to": "0x0000000000000000000000000000000000000000",  # GMX contract
            "value": 0,
            "gas": 300000,
            "gasPrice": self.web3.to_wei("1", "gwei"),
            "nonce": self.web3.eth.get_transaction_count(self.account),
        }

        signed_tx = self.wallet.sign_transaction(tx)

        tx_hash = self.web3.eth.send_raw_transaction(signed_tx)

        return {
            "status": "submitted",
            "tx_hash": tx_hash.hex(),
        }

    async def cancel_order(self, order_id):
        return {"status": "not_implemented"}

    async def get_position(self, symbol):
        return {"status": "not_implemented"}
