from eth_account import Account


class Signer:
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)

    def sign(self, tx_data: dict):
        signed_tx = self.account.sign_transaction(tx_data)
        return signed_tx.rawTransaction
