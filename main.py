"""
AegisTrade — Main Entrypoint
Starts trading loop + admin panel concurrently.
"""
from __future__ import annotations
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.bot.trading_loop import get_loop
from backend.referral.referral_system import ReferralSystem
from backend.admin.admin_panel import run_admin_server
from backend.utils.logger import get_logger

log = get_logger("main")


async def main() -> None:
    bot = get_loop()
    referral = ReferralSystem(bot.state)

    await asyncio.gather(
        bot.run(),
        run_admin_server(bot, referral),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("AegisTrade shut down by user")






