import numpy as np


class SpotStrategy:
    def __init__(self):
        self.ema_period = 20
        self.rsi_period = 14

    def ema(self, prices):
        weights = np.ones(self.ema_period) / self.ema_period
        return np.convolve(prices, weights, mode='valid')

    def rsi(self, prices):
        deltas = np.diff(prices)
        gain = np.maximum(deltas, 0)
        loss = np.abs(np.minimum(deltas, 0))

        avg_gain = np.mean(gain[-self.rsi_period:])
        avg_loss = np.mean(loss[-self.rsi_period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def generate_signal(self, prices):
        if len(prices) < 50:
            return {"signal": "HOLD"}

        ema = self.ema(prices)[-1]
        rsi = self.rsi(prices)
        price = prices[-1]

        if price > ema and rsi < 70:
            return {"signal": "BUY", "price": price}

        if price < ema and rsi > 30:
            return {"signal": "SELL", "price": price}

        return {"signal": "HOLD"}
