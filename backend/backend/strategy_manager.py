# ================================
# strategy_manager.py (PRO)
# ================================

import asyncio
from typing import Dict, Any, List


class StrategyManager:
    def __init__(self, risk_engine, execution, portfolio):
        self.risk_engine = risk_engine
        self.execution = execution
        self.portfolio = portfolio

        # symbol -> list of positions
        self.positions: Dict[str, List[Dict[str, Any]]] = {}

        # symbol locks
        self.locks: Dict[str, asyncio.Lock] = {}

        # strategy priority (по-голямо = по-важно)
        self.strategy_priority = {
            "first_candle": 3,
            "futures": 2,
            "spot": 1
        }

    # =========================
    def _get_lock(self, symbol):
        if symbol not in self.locks:
            self.locks[symbol] = asyncio.Lock()
        return self.locks[symbol]

    # =========================
    def get_positions(self, symbol):
        return self.positions.get(symbol, [])

    # =========================
    def has_position(self, symbol):
        return len(self.get_positions(symbol)) > 0

    # =========================
    def register_position(self, symbol, data):
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(data)

    # =========================
    def remove_position(self, symbol, order_id):
        if symbol not in self.positions:
            return

        self.positions[symbol] = [
            p for p in self.positions[symbol]
            if p["order_id"] != order_id
        ]

    # =========================
    def can_open_new_position(self, symbol, strategy):
        existing = self.get_positions(symbol)

        if not existing:
            return True

        # проверка за приоритет
        highest = max(existing, key=lambda x: self.strategy_priority.get(x["strategy"], 0))

        return self.strategy_priority.get(strategy, 0) >= self.strategy_priority.get(highest["strategy"], 0)

    # =========================
    async def process_signal(self, signal: Dict[str, Any]):
        symbol = signal["symbol"]
        strategy = signal["strategy"]

        lock = self._get_lock(symbol)

        async with lock:

            # =========================
            # PRIORITY CHECK
            # =========================
            if not self.can_open_new_position(symbol, strategy):
                print(f"[BLOCKED:LOW PRIORITY] {symbol} {strategy}")
                return False

            # =========================
            # RISK CHECK
            # =========================
            if not self.risk_engine.approve_trade(signal):
                print(f"[RISK BLOCKED] {symbol}")
                return False

            # =========================
            # EXECUTION
            # =========================
            try:
                order = await self.execution.execute_order(signal)

                position = {
                    "order_id": order.get("id"),
                    "symbol": symbol,
                    "side": signal["side"],
                    "size": signal["size"],
                    "strategy": strategy
                }

                self.register_position(symbol, position)

                print(f"[OPENED] {symbol} ({strategy})")
                return True

            except Exception as e:
                print(f"[EXEC ERROR] {symbol}: {e}")
                return False

    # =========================
    async def process_exit(self, symbol, order_id, exit_data=None):
        lock = self._get_lock(symbol)

        async with lock:
            try:
                await self.execution.close_position(symbol, exit_data)

                self.remove_position(symbol, order_id)

                print(f"[CLOSED] {symbol} order={order_id}")

            except Exception as e:
                print(f"[EXIT ERROR] {symbol}: {e}")
