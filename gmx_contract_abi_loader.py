# gmx_contract_abi_loader.py
"""
GMX Contract ABI Loader (FINAL)

Role:
- Load and cache ABI definitions for GMX smart contracts
- Supports Router, Vault, PositionRouter
- No RPC calls
- No business logic
"""

import json
from pathlib import Path
from typing import Dict, Any


class GMXABINotFound(Exception):
    pass


class GMXContractABILoader:
    def __init__(self, abi_dir: str):
        self.abi_dir = Path(abi_dir)
        if not self.abi_dir.exists():
            raise FileNotFoundError(f"ABI directory not found: {abi_dir}")

        self._cache: Dict[str, Any] = {}

    def load(self, contract_name: str) -> Any:
        if contract_name in self._cache:
            return self._cache[contract_name]

        abi_path = self.abi_dir / f"{contract_name}.json"
        if not abi_path.exists():
            raise GMXABINotFound(f"ABI file not found: {abi_path}")

        with open(abi_path, "r") as f:
            abi = json.load(f)

        self._cache[contract_name] = abi
        return abi

    def available_contracts(self) -> list[str]:
        return [p.stem for p in self.abi_dir.glob("*.json")]
