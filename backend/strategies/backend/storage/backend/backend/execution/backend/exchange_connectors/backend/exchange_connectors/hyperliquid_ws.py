import asyncio
import json
import websockets
from typing import Callable, Dict

HYPERLIQUID_WS_MAINNET = "wss://api.hyperliquid.xyz/ws"
HYPERLIQUID_WS_TESTNET = "wss://api.hyperliquid-testnet.xyz/ws"

class HyperliquidWSConnector:
    """
    Production‑ready WebSocket connector за Hyperliquid market data
    """

    def __init__(
        self,
        symbols: list[str],
        on_message: Callable[[Dict], None],
        testnet: bool = False,
        reconnect_delay: float = 5.0
    ):
        self.symbols = symbols
        self.on_message = on_message
        self.ws_url = HYPERLIQUID_WS_TESTNET if testnet else HYPERLIQUID_WS_MAINNET
        self.reconnect_delay = reconnect_delay
        self.running = False
        self.ws = None

    async def connect(self):
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.ws_url, ping_interval=20, ping_timeout=20) as ws:
                    self.ws = ws
                    await self.subscribe_all()
                    async for msg in ws:
                        await self.handle_message(msg)
            except Exception as exc:
                print(f"[HyperliquidWS] Connection error: {exc}; reconnect in {self.reconnect_delay}s")
                await asyncio.sleep(self.reconnect_delay)

    async def subscribe_all(self):
        """
        Абониране за trades и book updates за всеки символ
        (параметрите зависят от API subscription сообщения)
        """
        for symbol in self.symbols:
            # Пример: абониране за trades
            sub_trades = {
                "method": "subscribe",
                "subscription": {"type": "trades", "coin": symbol}
            }
            await self.ws.send(json.dumps(sub_trades))

            # TODO: добавяне на orderbook / други канали ако API ги поддържа
            # (check Hyperliquid API за channel types)
            # sub_book = {...}
            # await self.ws.send(json.dumps(sub_book))

    async def handle_message(self, raw: str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        # директно подаваме събитие към on_message
        # тук може да се нормализира event преди изпращане
        await self.on_message(data)

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()
