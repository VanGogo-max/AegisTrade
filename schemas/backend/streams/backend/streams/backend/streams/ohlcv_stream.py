# streams/ohlcv_stream.py

import random
from datetime import datetime, timedelta
from schemas.messages import Candle, OHLCVMessage


class OHLCVStream:
    def __init__(self, symbol: str, timeframe: str = "1m", last_close: float = 30000.0):
        self.symbol = symbol
        self.timeframe = timeframe
        self.last_close = last_close
        self.last_timestamp = datetime.utcnow()

    def _next_timestamp(self):
        return self.last_timestamp + timedelta(minutes=1)

    def tick(self) -> OHLCVMessage:
        open_price = self.last_close
        high = open_price + random.uniform(0, 50)
        low = open_price - random.uniform(0, 50)
        close = random.uniform(low, high)
        volume = random.uniform(10, 500)

        self.last_close = close
        self.last_timestamp = self._next_timestamp()

        candle = Candle(
            timestamp=self.last_timestamp,
            open=round(open_price, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(close, 2),
            volume=round(volume, 2)
        )

        return OHLCVMessage(
            symbol=self.symbol,
            timeframe=self.timeframe,
            candles=[candle]
        )
