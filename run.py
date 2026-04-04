import sys
sys.path.insert(0, "/workspaces/AegisTrade")

from backend.bot.trading_loop import TradingLoop
import asyncio

asyncio.run(TradingLoop().run())
