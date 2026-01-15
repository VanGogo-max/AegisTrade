# main.py

import time
from web3 import Web3
from gmx_tx_sender import GMXTxSender
from gmx_gas_optimizer import GMXGasOptimizer
from gmx_sandwich_guard import GMXSandwichGuard
from gmx_mempool_watcher import GMXMempoolWatcher
from gmx_liquidity_monitor import GMXLiquidityMonitor

# --- Настройки ---
RPC_URL = "https://arb1.arbitrum.io/rpc"  # или testnet
PRIVATE_KEY = "0xYOUR_PRIVATE_KEY"
CHAIN_ID = 42161  # Arbitrum mainnet
POOL_ADDRESS = "0xPoolAddress"
PAIR = "ETH/USDC"

# --- Инициализация Web3 ---
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# --- Инициализация защитни модули ---
gas_optimizer = GMXGasOptimizer(web3)
sandwich_guard = GMXSandwichGuard(web3, watched_pairs=[PAIR])
mempool_watcher = GMXMempoolWatcher(web3, gmx_contract_addresses=["0xRouter"])
liquidity_monitor = GMXLiquidityMonitor(web3, pool_addresses=[POOL_ADDRESS])

# --- Tx Sender ---
tx_sender = GMXTxSender(
    web3=web3,
    private_key=PRIVATE_KEY,
    gas_optimizer=gas_optimizer,
    sandwich_guard=sandwich_guard,
    mempool_watcher=mempool_watcher,
    liquidity_monitor=liquidity_monitor,
    chain_id=CHAIN_ID
)

# --- Примерна стратегия ---
def strategy():
    # Тук се определя кога да купуваме / продаваме
    # Може да се вгради RSI / Turtle / Grid и т.н.
    current_price = 2010.0  # взето от oracle / price feed
    expected_price = 2000.0
    expected_size = 0.1  # ETH
    return {
        "to": "0xRouterAddress",
        "data": b"",  # encode swap data ако имаш
        "pair": PAIR,
        "expected_price": expected_price,
        "expected_size": expected_size,
        "current_price": current_price,
        "pool_address": POOL_ADDRESS,
        "value": 0
    }

# --- Основен loop ---
def main_loop():
    while True:
        try:
            order = strategy()
            tx_hash = tx_sender.send_transaction(**order)
            print(f"Transaction sent successfully: {tx_hash}")
        except Exception as e:
            print(f"Transaction blocked or failed: {e}")

        time.sleep(10)  # интервал между проверките

if __name__ == "__main__":
    main_loop()
