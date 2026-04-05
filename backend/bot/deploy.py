#!/usr/bin/env python3
"""
deploy.py — Deploy AegisPayment.sol to Polygon
Run once. Needs: pip install web3 py-solc-x python-dotenv

Setup:
    cp .env.example .env
    # Fill DEPLOYER_PRIVATE_KEY and TREASURY_ADDRESS
    python deploy.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_source, install_solc

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────
POLYGON_RPC        = "https://polygon-rpc.com"
USDT_POLYGON       = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
PRIVATE_KEY        = os.environ["DEPLOYER_PRIVATE_KEY"]   # Never commit!
TREASURY_ADDRESS   = os.environ["TREASURY_ADDRESS"]        # Your USDT wallet
GAS_PRICE_GWEI     = 150  # Polygon usually needs 30-200 gwei

# ── Compile ────────────────────────────────────────────────────────────────
def compile_contract():
    install_solc("0.8.20")
    source = Path("contracts/AegisPayment.sol").read_text()
    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version="0.8.20",
        optimize=True,
        optimize_runs=200,
    )
    key = "<stdin>:AegisPayment"
    return compiled[key]["abi"], compiled[key]["bin"]

# ── Deploy ─────────────────────────────────────────────────────────────────
def deploy():
    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))
    assert w3.is_connected(), "Cannot connect to Polygon RPC"

    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Deployer: {account.address}")
    print(f"Balance:  {w3.from_wei(w3.eth.get_balance(account.address), 'ether'):.4f} MATIC")

    abi, bytecode = compile_contract()
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx = Contract.constructor(
        USDT_POLYGON,
        Web3.to_checksum_address(TREASURY_ADDRESS),
    ).build_transaction({
        "from":     account.address,
        "nonce":    w3.eth.get_transaction_count(account.address),
        "gasPrice": w3.to_wei(GAS_PRICE_GWEI, "gwei"),
    })

    gas = w3.eth.estimate_gas(tx)
    tx["gas"] = int(gas * 1.2)
    print(f"Estimated gas: {gas:,}  (~{w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether'):.4f} MATIC)")

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Tx sent: {tx_hash.hex()}")
    print("Waiting for receipt...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    contract_address = receipt.contractAddress
    print(f"\n✅ AegisPayment deployed at: {contract_address}")
    print(f"   PolygonScan: https://polygonscan.com/address/{contract_address}")

    # Save for backend
    output = {
        "contract_address": contract_address,
        "deployer":         account.address,
        "treasury":         TREASURY_ADDRESS,
        "usdt":             USDT_POLYGON,
        "tx_hash":          tx_hash.hex(),
        "abi":              abi,
    }
    Path("deployment.json").write_text(json.dumps(output, indent=2))
    print("\n📄 Saved to deployment.json")
    print("\n👉 Next: copy contract_address to backend/payments/payment_verifier.py → CONTRACT_ADDRESS")

if __name__ == "__main__":
    deploy()
