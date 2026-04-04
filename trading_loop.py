import asyncio
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich import box

from backend.execution.execution_engine import ExecutionEngine, ExecutionRequest, OrderSide, OrderType
from backend.risk.risk_engine import RiskEngine
from backend.state.state_manager import StateManager
from backend.feeds.price_feed import PriceFeed
from backend.config.config import Config

console = Console()

# ── Logging setup ────────────────────────────────────────
logger.remove()
logger.add(
    "logs/aegistrade.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    lambda msg: console.print(msg, end=""),
    level="DEBUG",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)


class TradingLoop:

    def __init__(self):
        self.execution_engine = ExecutionEngine()
        self.risk_engine = RiskEngine()
        self.price_feed = PriceFeed()
        self.state = StateManager()
        self.symbol = Config.SYMBOL
        self.running = True

    async def run(self):
        logger.info(f"AegisTrade started | symbol={self.symbol} | dry_run={Config.DRY_RUN}")
        while self.running:
            try:
                await self.step()
                await asyncio.sleep(Config.LOOP_INTERVAL)
            except Exception as e:
                logger.exception(f"Loop error: {e}")
                await asyncio.sleep(Config.LOOP_INTERVAL)

    async def step(self):
        price = await self.price_feed.get_price(self.symbol)
        if not price:
            logger.warning(f"No price available for {self.symbol}")
            return

        position = self.state.get_position()
        decision = self._decide(price, position)

        self._log_status(price, position, decision)
        await self._execute(decision, price)

    def _decide(self, price, position):
        size = position.get("size_usd", 0)
        entry = position.get("entry_price", 0)
        if size == 0:
            return {"action": "open_long"}
        if size > 0 and entry > 0:
            change = (price - entry) / entry
            if change <= -0.02 or change >= 0.03:
                return {"action": "close"}
        return {"action": "hold"}

    async def _execute(self, decision, price):
        action = decision.get("action")

        if Config.DRY_RUN:
            logger.debug(f"DRY RUN | action={action} | price={price}")

        if action == "hold":
            return

        if action == "open_long":
            self.state.update_position({"size_usd": Config.TRADE_SIZE, "entry_price": price})
            self.state.add_trade({"type": "buy", "price": price})
            logger.success(f"OPEN LONG | size=${Config.TRADE_SIZE} | entry={price}")

        elif action == "close":
            entry = self.state.get_position().get("entry_price", price)
            pnl_pct = (price - entry) / entry * 100
            self.state.clear_position()
            self.state.add_trade({"type": "sell", "price": price})
            logger.success(f"CLOSE | exit={price} | pnl={pnl_pct:+.2f}%")

    def _log_status(self, price, position, decision):
        size = position.get("size_usd", 0)
        entry = position.get("entry_price", 0)
        action = decision.get("action", "?")

        pnl_str = ""
        if size > 0 and entry > 0:
            pnl_pct = (price - entry) / entry * 100
            pnl_str = f"{pnl_pct:+.2f}%"

        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column(style="cyan")
        table.add_column(style="white")
        table.add_row("Symbol", self.symbol)
        table.add_row("Price", f"${price:,.2f}")
        table.add_row("Position", f"${size:,.0f}" if size else "flat")
        table.add_row("PnL", pnl_str if pnl_str else "-")
        table.add_row("Action", f"[bold yellow]{action}[/bold yellow]")

        console.print(table)
        logger.info(f"step | price={price} | size={size} | action={action} | pnl={pnl_str or '-'}")

    def stop(self):
        self.running = False
        logger.info("Trading loop stopped")


if __name__ == "__main__":
    loop = TradingLoop()
    asyncio.run(loop.run())
