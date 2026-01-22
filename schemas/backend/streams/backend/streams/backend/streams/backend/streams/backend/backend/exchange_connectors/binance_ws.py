import asyncio
import json
import time
import websockets
from typing import List, Dict, Callable
from dataclasses import dataclass, asdict


BINANCE_WS_URL = "wss://stream.binance.com:9443/stream"


# ========== Normalized Schemas ==========

@dataclass
class NormalizedTrade:
    exchange: str
    symbol: str
    price: float
    quantity: float
    side: str
    timestamp: int


@dataclass
class NormalizedOrderBook:
    exchange: str
    symbol: str
    bids: List[List[float]]
    asks: List[List[float]]
    timestamp: int


@dataclass
class NormalizedOHLCV:
    exchange: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    start_ts: int
    end_ts: int
    interval: str


# ========== Binance WebSocket Connector ==========

class BinanceWSConnector:
    def __init__(
        self,
        symbols: List[str],
        intervals: List[str],
        on_message: Callable[[Dict], None],
        reconnect_delay: int = 5
    ):
        self.symbols = [s.lower() for s in symbols]
        self.intervals = intervals
        self.on_message = on_message
        self.reconnect_delay = reconnect_delay
        self.ws = None
        self.running = False

    def build_streams(self) -> List[str]:
        streams = []
        for symbol in self.symbols:
            streams.append(f"{symbol}@trade")
            streams.append(f"{symbol}@depth20@100ms")
            for interval in self.intervals:
                streams.append(f"{symbol}@kline_{interval}")
        return streams

    def build_url(self) -> str:
        streams = "/".join(self.build_streams())
        return f"{BINANCE_WS_URL}?streams={streams}"

    async def connect(self):
        self.running = True
        while self.running:
            try:
                url = self.build_url()
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    self.ws = ws
                    print("[BinanceWS] Connected")
                    async for msg in ws:
                        await self.handle_message(msg)
            except Exception as e:
                print(f"[BinanceWS] Connection error: {e}")
                print(f"[BinanceWS] Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)

    async def handle_message(self, raw: str):
        data = json.loads(raw)
        stream = data.get("stream")
        payload = data.get("data")

        if not payload:
            return

        event_type = payload.get("e")

        if event_type == "trade":
            normalized = self.normalize_trade(payload)
        elif event_type == "depthUpdate":
            normalized = self.normalize_orderbook(payload)
        elif event_type == "kline":
            normalized = self.normalize_ohlcv(payload)
        else:
            return

        self.on_message(asdict(normalized))

    # ========== Normalizers ==========

    def normalize_trade(self, t: Dict) -> NormalizedTrade:
        return NormalizedTrade(
            exchange="binance",
            symbol=t["s"],
            price=float(t["p"]),
            quantity=float(t["q"]),
            side="buy" if t["m"] is False else "sell",
            timestamp=int(t["T"])
        )

    def normalize_orderbook(self, d: Dict) -> NormalizedOrderBook:
        return NormalizedOrderBook(
            exchange="binance",
            symbol=d["s"],
            bids=[[float(p), float(q)] for p, q in d["b"]],
            asks=[[float(p), float(q)] for p, q in d["a"]],
            timestamp=int(time.time() * 1000)
        )

    def normalize_ohlcv(self, k: Dict) -> NormalizedOHLCV:
        kline = k["k"]
        return NormalizedOHLCV(
            exchange="binance",
            symbol=kline["s"],
            open=float(kline["o"]),
            high=float(kline["h"]),
            low=float(kline["l"]),
            close=float(kline["c"]),
            volume=float(kline["v"]),
            start_ts=int(kline["t"]),
            end_ts=int(kline["T"]),
            interval=kline["i"]
        )

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()


# ========== Example bootstrap (ще го махнем по-късно) ==========

if __name__ == "__main__":
    def printer(msg):
        print(msg)

    connector = BinanceWSConnector(
        symbols=["BTCUSDT", "ETHUSDT"],
        intervals=["1m", "5m"],
        on_message=printer
    )

    asyncio.run(connector.connect())
