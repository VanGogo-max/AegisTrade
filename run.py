import asyncio
import signal
import sys

sys.path.insert(0, "/workspaces/AegisTrade")

from loguru import logger
from backend.bot.trading_loop import TradingLoop


async def main():
    loop = TradingLoop()

    def handle_shutdown(sig, frame):
        logger.warning(f"Signal {sig} received — shutting down...")
        loop.stop()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        await loop.run()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    finally:
        logger.info("AegisTrade stopped cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
