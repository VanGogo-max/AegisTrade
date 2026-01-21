# ws_server.py

import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from schemas.messages import (
    OrderbookSnapshot, OrderbookLevel,
    TradesMessage, Trade,
    PositionsMessage, Position,
    OrdersMessage, Order,
    BalancesMessage, Balance,
    OHLCVMessage, Candle,
    WSMessage
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            now = datetime.utcnow()

            # ---- ORDERBOOK ----
            orderbook = OrderbookSnapshot(
                symbol="BTCUSDT",
                bids=[OrderbookLevel(price=30000 + i, size=1 + i * 0.1) for i in range(5)],
                asks=[OrderbookLevel(price=30001 + i, size=1 + i * 0.1) for i in range(5)],
                timestamp=now
            )

            # ---- TRADES ----
            trades = TradesMessage(trades=[
                Trade(
                    trade_id=str(int(now.timestamp())),
                    symbol="BTCUSDT",
                    side="buy",
                    price=30000.5,
                    size=0.01,
                    timestamp=now
                )
            ])

            # ---- POSITIONS ----
            positions = PositionsMessage(positions=[
                Position(
                    symbol="BTCUSDT",
                    side="long",
                    size=0.1,
                    entry_price=29500,
                    mark_price=30000,
                    pnl=50,
                    leverage=10
                )
            ])

            # ---- ORDERS ----
            orders = OrdersMessage(orders=[
                Order(
                    order_id="123",
                    symbol="BTCUSDT",
                    side="buy",
                    price=29900,
                    size=0.05,
                    status="open"
                )
            ])

            # ---- BALANCES ----
            balances = BalancesMessage(balances=[
                Balance(asset="USDT", available=1000, locked=50),
                Balance(asset="BTC", available=0.2, locked=0.01)
            ])

            # ---- OHLCV ----
            ohlcv = OHLCVMessage(
                symbol="BTCUSDT",
                timeframe="1m",
                candles=[
                    Candle(
                        timestamp=now,
                        open=29800,
                        high=30100,
                        low=29750,
                        close=30000,
                        volume=120.5
                    )
                ]
            )

            messages = [
                WSMessage(type="orderbook", data=orderbook.dict()),
                WSMessage(type="trades", data=trades.dict()),
                WSMessage(type="positions", data=positions.dict()),
                WSMessage(type="orders", data=orders.dict()),
                WSMessage(type="balances", data=balances.dict()),
                WSMessage(type="ohlcv", data=ohlcv.dict()),
            ]

            for msg in messages:
                await ws.send_text(json.dumps(msg.dict(), default=str))

            await asyncio.sleep(1)

    except Exception as e:
        print("WebSocket closed:", e)
