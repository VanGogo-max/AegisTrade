"""
GMX ABI Encoder (FINAL)

Роля:
- Реален ABI encoder за GMX smart contract calls
- Превръща (method + params) в calldata (hex string)
- Използва стандартния Ethereum ABI механизъм
- НЕ изпраща транзакции
- НЕ подписва транзакции
- НЕ съдържа бизнес логика

Този файл е чист utility слой.

Проверими източници:
- Ethereum ABI Spec:
  https://docs.soliditylang.org/en/latest/abi-spec.html
- eth-abi (Python):
  https://eth-abi.readthedocs.io/en/latest/
- GMX Contracts:
  https://github.com/gmx-io/gmx-contracts
"""

from typing import Dict, Any, List
from eth_abi import encode as abi_encode
from eth_utils import keccak, to_hex


class GMXAbiEncoder:
    """
    ABI encoder за GMX contract calls.
    """

    @staticmethod
    def encode_function_call(
        function_signature: str,
        param_types: List[str],
        param_values: List[Any],
    ) -> str:
        """
        Кодира Solidity function call в calldata.

        Пример:
            function_signature = "createIncreasePosition(address,bool,uint256,uint256,uint256)"
            param_types = ["address", "bool", "uint256", "uint256", "uint256"]
            param_values = [...]

        Връща:
            calldata (0x...)
        """

        if len(param_types) != len(param_values):
            raise ValueError("param_types and param_values length mismatch")

        selector = GMXAbiEncoder._function_selector(function_signature)
        encoded_params = abi_encode(param_types, param_values)

        return to_hex(selector + encoded_params)

    @staticmethod
    def _function_selector(function_signature: str) -> bytes:
        """
        Изчислява 4-byte function selector:
        keccak256(function_signature)[0:4]
        """
        return keccak(text=function_signature)[:4]
