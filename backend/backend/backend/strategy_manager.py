import asyncio
from typing import Dict, Any, List


class StrategyManager:
    def __init__(self, risk_engine, execution, portfolio):
        self.risk_engine = risk_engine
        self.execution = execution
        self.portfolio = portfolio

        self.positions: Dict[str, List[Dict[str, Any]]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    def _get_lock(self, symbol):
        if symbol not in self.locks:
            self.locks[symbol] = asyncio.Lock()
        return self.locks[symbol]

    def register_position(self, symbol, position):
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(position)

    def remove_position(self, symbol, order_id):
        if symbol in self.positions:
            self.positions[symbol] = [
                p for p in self.positions[symbol]
                if p["order_id"] != order_id
            ]

    async def process_signal(self, signal: Dict[str, Any]):
        symbol = signal["symbol"]
        lock = self._get_lock(symbol)

        async with lock:

            if not self.risk_engine.approve_trade(signal):
                print(f"[RISK BLOCKED] {symbol}")
                return False

            atr = signal.get("atr", 0)
            if atr == 0:
                print(f"[SKIP] No ATR {symbol}")
                return False

            capital = self.portfolio.get_total_equity()
            risk_amount = capital * 0.01

            stop_distance = atr * 2
            size = risk_amount / stop_distance

            signal["size"] = size

            order = await self.execution.execute_order(signal)
            entry_price = order.get("price")

            if signal["side"] == "buy":
                stop_loss = entry_price - stop_distance
                take_profit = entry_price + stop_distance * 2
            else:
                stop_loss = entry_price + stop_distance
                take_profit = entry_price - stop_distance * 2

            position = {
                "order_id": order.get("id"),
                "symbol": symbol,
                "side": signal["side"],
                "size": size,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }

            self.register_position(symbol, position)

            print(f"[OPENED] {symbol}")
            return True

    async def process_exit(self, symbol, order_id):
        lock = self._get_lock(symbol)

        async with lock:
            await self.execution.close_position(symbol)

            self.remove_position(symbol, order_id)

            print(f"[CLOSED] {symbol}")

    async def monitor_positions(self, market_data):
        while True:
            for symbol, positions in self.positions.items():
                price = await market_data.get_price(symbol)

                for pos in positions[:]:
                    if pos["side"] == "buy":
                        if price <= pos["stop_loss"] or price >= pos["take_profit"]:
                            await self.process_exit(symbol, pos["order_id"])
                    else:
                        if price >= pos["stop_loss"] or price <= pos["take_profit"]:
                            await self.process_exit(symbol, pos["order_id"])

            await asyncio.sleep(1)
