# main.py

import time
import pandas as pd
from position_manager import PositionManager
from gmx_tx_sender import GMXTxSender
from strategies.ict_strategy import ICTStrategy
from strategies.liquidity_strategy import UniversalLiquidityStrategy
from strategies.grid_strategy import Grid5EntryStrategy
from web3 import Web3

# ====== Web3 / GMX setup ======
web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
web3.eth.default_account = web3.eth.account.from_key("YOUR_PRIVATE_KEY").address
gmxtx_sender = GMXTxSender(web3, "GMX_CONTRACT_ADDRESS", "YOUR_PRIVATE_KEY")

# ====== Pipeline setup ======
position_manager = PositionManager()

strategies = [
    ICTStrategy(),
    UniversalLiquidityStrategy(),
    Grid5EntryStrategy()
]

# ====== Main loop ======
while True:
    try:
        # 1) Получаваме последни свещи (примерно от API)
        candles_df = pd.DataFrame()  # TODO: зареждане на OHLCV данни

        # 2) Всеки strategy проверява сигнал
        for strat in strategies:
            signal = strat.check_signal(candles_df)
            if signal:
                # Отваряне само ако няма активна позиция
                if position_manager.get_status()["status"] == "NO_POSITION":
                    open_cmd = position_manager.open_position(signal, candles_df)
                    gmxtx_sender.execute(open_cmd)

        # 3) Update на отворена позиция
        status = position_manager.get_status()
        if status["status"] == "OPEN":
            last_price = candles_df.iloc[-1]["close"]
            update_cmd = position_manager.on_price_update(last_price, candles_df)
            if update_cmd:
                gmxtx_sender.execute(update_cmd)

        # 4) Sleep / Rate limit
        time.sleep(5)

    except Exception as e:
        print(f"[MAIN] Exception: {e}")
        # Emergency exit при сериозна грешка
        if position_manager.get_status()["status"] == "OPEN":
            close_cmd = position_manager.close_position("ERROR")
            gmxtx_sender.execute(close_cmd)
        time.sleep(10)
