import json


class ContractLoader:
    def __init__(self, web3):
        self.w3 = web3

    def load_contract(self, address: str, abi_path: str):
        with open(abi_path) as f:
            abi = json.load(f)

        return self.w3.eth.contract(address=address, abi=abi)
