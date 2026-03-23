import asyncio

from market_data_layer import MarketDataLayer
from risk_engine import RiskEngine
from execution_engine import ExecutionEngine
from portfolio_pnl import PortfolioPnL

from strategy_manager import StrategyManager

from first_candle_bot import FirstCandleBot
from spot_strategy import SpotStrategy
from futures_strategy import FuturesStrategy


async def run_strategy(strategy):
    while True:
        try:
            await strategy.run_cycle()
        except Exception as e:
            print(f"[ERROR] {e}")
        await asyncio.sleep(1)


async def main():
    symbols = ["BTC/USDT", "ETH/USDT"]
    exchanges = ["binance", "bybit"]

    market_data = MarketDataLayer(exchanges)
    risk_engine = RiskEngine(max_exposure_pct=0.2, max_daily_loss=1000)
    execution = ExecutionEngine(market_data.clients)
    portfolio = PortfolioPnL(initial_capital=100000)

    manager = StrategyManager(risk_engine, execution, portfolio)

    tasks = []

    for symbol in symbols:
        tasks.append(run_strategy(FirstCandleBot(symbol, market_data, manager)))
        tasks.append(run_strategy(SpotStrategy(symbol, market_data, manager)))
        tasks.append(run_strategy(FuturesStrategy(symbol, market_data, manager)))

    tasks.append(manager.monitor_positions(market_data))

    print("🚀 ENGINE STARTED")

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
