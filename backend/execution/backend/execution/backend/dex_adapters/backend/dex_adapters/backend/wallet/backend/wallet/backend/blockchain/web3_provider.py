from web3 import Web3


class Web3Provider:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    def get_web3(self):
        return self.w3
