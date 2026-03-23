import asyncio

from market_data_layer import MarketDataLayer
from risk_engine import RiskEngine
from execution_engine import ExecutionEngine
from portfolio_pnl import PortfolioPnL

from strategy_manager import StrategyManager
from funding_engine import FundingEngine

from spot_strategy import SpotStrategy
from futures_strategy import FuturesStrategy
from first_candle_bot import FirstCandleBot


async def run_strategy(strategy):
    while True:
        try:
            await strategy.run_cycle()
        except Exception as e:
            print(f"[ERROR] {e}")
        await asyncio.sleep(1)


async def main():
    symbols = ["BTC/USDT", "ETH/USDT"]

    market_data = MarketDataLayer(["binance"])
    risk_engine = RiskEngine(0.2, 1000)
    execution = ExecutionEngine(market_data.clients)
    portfolio = PortfolioPnL(100000)

    manager = StrategyManager(risk_engine, execution, portfolio)

    funding = FundingEngine(market_data.clients)
    manager.set_funding_engine(funding)

    tasks = []

    for s in symbols:
        tasks.append(run_strategy(SpotStrategy(s, market_data, manager)))
        tasks.append(run_strategy(FuturesStrategy(s, market_data, manager)))
        tasks.append(run_strategy(FirstCandleBot(s, market_data, manager)))

    tasks.append(manager.monitor_positions(market_data))
    tasks.append(funding.run(symbols))

    print("ENGINE STARTED")

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
