# ================================
# main.py – Multi-Strategy Runner
# ================================

import asyncio

from market_data_layer import MarketDataLayer
from risk_engine import RiskEngine
from execution_engine import ExecutionEngine
from portfolio_pnl import PortfolioPnL

from first_candle_bot import FirstCandleBot
from spot_strategy import SpotStrategy
from futures_strategy import FuturesStrategy


# ================================
# FIRST CANDLE STRATEGY
# ================================
async def run_first_candle(symbol, market_data, risk_engine, execution, portfolio):
    bot = FirstCandleBot(
        symbol=symbol,
        market_data=market_data,
        risk_engine=risk_engine,
        execution=execution,
        portfolio=portfolio,
        risk_pct_per_trade=0.01,
        profit_factor=2.6,
        trading_time_msk="17:30"
    )

    while True:
        try:
            await bot.capture_first_candle()
            breakout = await bot.check_breakout()

            if breakout:
                await bot.open_trade(breakout)

            await bot.check_exit_conditions()

        except Exception as e:
            print(f"[FirstCandle ERROR] {symbol}: {e}")

        await asyncio.sleep(1)


# ================================
# SPOT STRATEGY
# ================================
async def run_spot(symbol, market_data, risk_engine, execution, portfolio):
    strategy = SpotStrategy(
        symbol=symbol,
        market_data=market_data,
        risk_engine=risk_engine,
        execution=execution,
        portfolio=portfolio
    )

    while True:
        try:
            await strategy.run_cycle()
        except Exception as e:
            print(f"[Spot ERROR] {symbol}: {e}")

        await asyncio.sleep(1)


# ================================
# FUTURES STRATEGY
# ================================
async def run_futures(symbol, market_data, risk_engine, execution, portfolio):
    strategy = FuturesStrategy(
        symbol=symbol,
        market_data=market_data,
        risk_engine=risk_engine,
        execution=execution,
        portfolio=portfolio
    )

    while True:
        try:
            await strategy.run_cycle()
        except Exception as e:
            print(f"[Futures ERROR] {symbol}: {e}")

        await asyncio.sleep(1)


# ================================
# MAIN ENTRY POINT
# ================================
async def main():
    # =========================
    # CONFIG
    # =========================
    symbols = ["BTC/USDT", "ETH/USDT"]
    exchanges = ["binance", "bybit"]

    # =========================
    # CORE COMPONENTS
    # =========================
    market_data = MarketDataLayer(exchanges)
    risk_engine = RiskEngine(
        max_exposure_pct=0.2,
        max_daily_loss=1000
    )
    execution = ExecutionEngine(market_data.clients)
    portfolio = PortfolioPnL(initial_capital=100000)

    # =========================
    # TASKS
    # =========================
    tasks = []

    for symbol in symbols:
        tasks.append(run_first_candle(symbol, market_data, risk_engine, execution, portfolio))
        tasks.append(run_spot(symbol, market_data, risk_engine, execution, portfolio))
        tasks.append(run_futures(symbol, market_data, risk_engine, execution, portfolio))

    print(f"🚀 Стартирани стратегии за: {symbols}")

    await asyncio.gather(*tasks)


# ================================
# RUN
# ================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ БОТ СПРЯН ОТ ПОТРЕБИТЕЛЯ")
