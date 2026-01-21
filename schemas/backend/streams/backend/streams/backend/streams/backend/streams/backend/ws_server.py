import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from schemas.messages import WSMessage
from streams.orderbook_stream import OrderbookStream
from streams.trades_stream import TradesStream
from streams.ohlcv_stream import OHLCVStream
from streams.account_stream import AccountStream

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Streams initialization ---
orderbook_stream = OrderbookStream(symbol="BTCUSDT")
trades_stream = TradesStream(symbol="BTCUSDT")
ohlcv_stream = OHLCVStream(symbol="BTCUSDT", timeframe="1m")
account_stream = AccountStream()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            # Generate live data
            orderbook = orderbook_stream.snapshot()
            trades = trades_stream.tick()
            ohlcv = ohlcv_stream.tick()
            positions = account_stream.tick_positions()
            orders = account_stream.tick_orders()
            balances = account_stream.tick_balances()

            messages = [
                WSMessage(type="orderbook", data=orderbook.dict()),
                WSMessage(type="trades", data=trades.dict()),
                WSMessage(type="ohlcv", data=ohlcv.dict()),
                WSMessage(type="positions", data=positions.dict()),
                WSMessage(type="orders", data=orders.dict()),
                WSMessage(type="balances", data=balances.dict()),
            ]

            for msg in messages:
                await ws.send_text(json.dumps(msg.dict(), default=str))

            await asyncio.sleep(1)

    except Exception as e:
        print("WebSocket closed:", e)
