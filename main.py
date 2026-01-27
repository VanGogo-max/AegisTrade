# ================================
# main.py – интеграция на First Candle Bot
# ================================

import asyncio
from market_data_layer import MarketDataLayer
from risk_engine import RiskEngine
from execution_engine import ExecutionEngine
from portfolio_pnl import PortfolioPnL
from first_candle_bot import FirstCandleBot

async def run_first_candle(symbol: str, market_data, risk_engine, execution, portfolio):
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
        await bot.capture_first_candle()
        breakout = await bot.check_breakout()
        if breakout:
            await bot.open_trade(breakout)
        await bot.check_exit_conditions()
        await asyncio.sleep(1)  # 1 секунда между итерациите

async def main():
    # =========================
    # Инициализация на компонентите
    # =========================
    symbols = ["ES/USDT", "BTC/USDT"]  # Добави още символи по желание
    exchanges = ["binance", "bybit"]

    market_data = MarketDataLayer(exchanges)
    risk_engine = RiskEngine(max_exposure_pct=0.2, max_daily_loss=1000)
    execution = ExecutionEngine(market_data.clients)
    portfolio = PortfolioPnL(initial_capital=100000)

    # Стартиране на един async task за всеки символ
    tasks = [run_first_candle(symbol, market_data, risk_engine, execution, portfolio) for symbol in symbols]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ БОТ СПРЯН ОТ ПОТРЕБИТЕЛЯ")
