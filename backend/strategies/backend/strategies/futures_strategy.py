import numpy as np


class FuturesStrategy:
    def __init__(self, capital=100):
        self.capital = capital
        self.ema_period = 20
        self.rsi_period = 14
        self.risk_per_trade = 0.01
        self.stop_loss_pct = 0.02
        self.leverage = 2

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

    def stop_loss(self, price, direction):
        if direction == "LONG":
            return price * (1 - self.stop_loss_pct)
        return price * (1 + self.stop_loss_pct)

    def position_size(self, entry, stop):
        risk_amount = self.capital * self.risk_per_trade
        distance = abs(entry - stop)

        if distance == 0:
            return 0

        return risk_amount / (distance * self.leverage)

    def generate_signal(self, prices):
        if len(prices) < 50:
            return None

        ema = self.ema(prices)[-1]
        rsi = self.rsi(prices)
        price = prices[-1]

        if price > ema and rsi < 70:
            direction = "LONG"
        elif price < ema and rsi > 30:
            direction = "SHORT"
        else:
            return None

        stop = self.stop_loss(price, direction)
        size = self.position_size(price, stop)

        return {
            "signal": direction,
            "entry_price": price,
            "stop_loss": stop,
            "position_size": size,
            "leverage": self.leverage
        }
