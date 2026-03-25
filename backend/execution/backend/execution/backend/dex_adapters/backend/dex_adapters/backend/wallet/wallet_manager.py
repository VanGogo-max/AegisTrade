from backend.wallet.signer import Signer


class WalletManager:
    def __init__(self, private_key: str):
        self.signer = Signer(private_key)

    def sign_transaction(self, tx_data: dict):
        return self.signer.sign(tx_data)
