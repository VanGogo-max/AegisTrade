# app_runner.py
"""
Responsibility:
- Entry point of the trading application
- Wires exchange, strategy and bot together
- Starts the trading loop

Does NOT depend on:
- position_state.py
- position_manager.py
- risk_manager.py
"""

from strategy_selector import StrategySelector
from exchange_adapter import ExchangeAdapter
from spot_bot import SpotBot
from futures_bot import FuturesBot


class AppRunner:
    def __init__(
        self,
        mode: str,
        exchange_name: str,
        symbol: str,
        strategy_name: str,
        initial_balance: float,
    ):
        self.mode = mode.lower()
        self.exchange_name = exchange_name
        self.symbol = symbol
        self.strategy_name = strategy_name
        self.initial_balance = initial_balance

        self.exchange = ExchangeAdapter(exchange_name)
        self.strategy = StrategySelector.select(strategy_name)

        if self.mode == "spot":
            self.bot = SpotBot(
                exchange=self.exchange,
                strategy=self.strategy,
                symbol=self.symbol,
                initial_balance=self.initial_balance,
            )
        elif self.mode == "futures":
            self.bot = FuturesBot(
                exchange=self.exchange,
                strategy=self.strategy,
                symbol=self.symbol,
                initial_balance=self.initial_balance,
            )
        else:
            raise ValueError("Mode must be 'spot' or 'futures'")

    def run(self) -> None:
        print(
            f"[APP] Mode={self.mode} | "
            f"Exchange={self.exchange_name} | "
            f"Symbol={self.symbol} | "
            f"Strategy={self.strategy_name}"
        )
        self.bot.run()


if __name__ == "__main__":
    MODE = "spot"
    EXCHANGE = "binance"
    SYMBOL = "BTC/USDT"
    STRATEGY = "turtle_rsi"
    INITIAL_BALANCE = 1000.0

    app = AppRunner(
        mode=MODE,
        exchange_name=EXCHANGE,
        symbol=SYMBOL,
        strategy_name=STRATEGY,
        initial_balance=INITIAL_BALANCE,
    )

    app.run()
