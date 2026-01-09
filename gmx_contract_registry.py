"""
GMX Contract Registry (FINAL)

Роля:
- Централизира всички GMX smart contract адреси и ABI signatures
- Поддържа multi-network и multi-version
- Използва се от:
    - GMXExchangeAdapter
    - GMXAbiEncoder
    - GMXWalletConnectSigner / GMXSimulatedSigner
- НЕ изпраща транзакции
- НЕ съдържа стратегия или риск логика

Проверими източници:
- GMX GitHub: https://github.com/gmx-io/gmx-contracts
- GMX Docs: https://docs.gmx.io
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class GMXContract:
    name: str
    address: str
    abi_signature: str  # function signature for ABI encoding


# Network -> contract list
GMX_CONTRACTS: Dict[str, List[GMXContract]] = {
    "arbitrum": [
        GMXContract(
            name="Router",
            address="ENV_GMX_ROUTER",
            abi_signature="",
        ),
        GMXContract(
            name="Vault",
            address="ENV_GMX_VAULT",
            abi_signature="",
        ),
        GMXContract(
            name="PositionRouter",
            address="ENV_GMX_POSITION_ROUTER",
            abi_signature="",
        ),
    ],
    "avalanche": [
        GMXContract(
            name="Router",
            address="ENV_GMX_ROUTER",
            abi_signature="",
        ),
        GMXContract(
            name="Vault",
            address="ENV_GMX_VAULT",
            abi_signature="",
        ),
        GMXContract(
            name="PositionRouter",
            address="ENV_GMX_POSITION_ROUTER",
            abi_signature="",
        ),
    ],
}


def get_contract_address(network: str, contract_name: str) -> str:
    """
    Връща адрес на contract по име и мрежа
    """
    contracts = GMX_CONTRACTS.get(network, [])
    for c in contracts:
        if c.name == contract_name:
            return c.address
    raise ValueError(f"Contract '{contract_name}' not found on network '{network}'")


def get_contract_abi_signature(network: str, contract_name: str) -> str:
    """
    Връща ABI signature на contract по име и мрежа
    """
    contracts = GMX_CONTRACTS.get(network, [])
    for c in contracts:
        if c.name == contract_name:
            return c.abi_signature
    raise ValueError(f"Contract '{contract_name}' not found on network '{network}'")
