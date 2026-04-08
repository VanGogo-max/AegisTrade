import aiohttp
from loguru import logger
from backend.config.config import Config


class TelegramNotifier:

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)

    async def send(self, message: str) -> None:
        if not self.enabled:
            logger.debug("Telegram not configured — skipping")
            return
        try:
            url = f"{self.BASE_URL}{self.token}/sendMessage"
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                })
        except Exception as e:
            logger.warning(f"Telegram error: {e}")

    async def notify_buy(self, symbol, price, size):
        await self.send(
            f"🟢 <b>OPEN LONG</b>\n"
            f"Symbol: {symbol}\n"
            f"Price: ${price:,.2f}\n"
            f"Size: ${size}"
        )

    async def notify_sell(self, symbol, price, pnl):
        emoji = "✅" if pnl >= 0 else "🔴"
        await self.send(
            f"{emoji} <b>CLOSE</b>\n"
            f"Symbol: {symbol}\n"
            f"Price: ${price:,.2f}\n"
            f"PnL: {pnl:+.2f}%"
        )

    async def notify_error(self, error: str):
        await self.send(f"⚠️ <b>ERROR</b>\n{error}")
