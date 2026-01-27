# ================================
# first_candle_bot.py – интеграция с текущия Prop Trading Stack
# ================================

import asyncio
import datetime
import pytz
from typing import Optional
from enum import Enum
from dataclasses import dataclass

# Импорти от съществуващия stack
from market_data_layer import MarketDataLayer
from risk_engine import RiskEngine
from execution_engine import ExecutionEngine
from portfolio_pnl import PortfolioPnL

# ====================================================
# ENUMS & DATACLASSES
# ====================================================
class TradeDirection(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

@dataclass
class Trade:
    direction: TradeDirection
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    entry_time: datetime.datetime
    exit_time: Optional[datetime.datetime] = None
    exit_price: Optional[float] = None
    profit: Optional[float] = None
    status: str = "OPEN"

# ====================================================
# First Candle Bot
# ====================================================
class FirstCandleBot:
    def __init__(self,
                 symbol: str,
                 market_data: MarketDataLayer,
                 risk_engine: RiskEngine,
                 execution: ExecutionEngine,
                 portfolio: PortfolioPnL,
                 risk_pct_per_trade: float = 0.01,
                 profit_factor: float = 2.6,
                 trading_time_msk: str = "17:30"):

        self.symbol = symbol
        self.market_data = market_data
        self.risk_engine = risk_engine
        self.execution = execution
        self.portfolio = portfolio
        self.risk_pct_per_trade = risk_pct_per_trade
        self.profit_factor = profit_factor
        self.trading_time_msk = trading_time_msk

        # Състояние
        self.first_candle = None
        self.active_trade: Optional[Trade] = None
        self.is_first_candle_captured = False

    # ====================================================
    # Логика за първата свещ
    # ====================================================
    async def capture_first_candle(self):
        if self.is_first_candle_captured:
            return
        now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
        trading_hour, trading_minute = map(int, self.trading_time_msk.split(':'))
        if now.hour == trading_hour and now.minute < trading_minute + 5:
            candles = self.market_data.fetch_ohlcv(self.symbol)
            if candles:
                # избираме последната свещ с най-голям обем
                self.first_candle = max(candles, key=lambda c: c[1]['volume'].iloc[-1])[1].iloc[-1]
                self.is_first_candle_captured = True
                self.log(f"✅ Първа свещ хваната за {self.symbol}")

    async def check_breakout(self) -> Optional[TradeDirection]:
        if not self.first_candle or self.active_trade:
            return None
        candles = self.market_data.fetch_ohlcv(self.symbol)
        if not candles:
            return None
        current_price = candles[-1][1]['close'].iloc[-1]
        if current_price > self.first_candle['high']:
            return TradeDirection.LONG
        elif current_price < self.first_candle['low']:
            return TradeDirection.SHORT
        return None

    # ====================================================
    # Позиция и управление на сделката
    # ====================================================
    async def open_trade(self, direction: TradeDirection):
        if self.active_trade:
            return

        candles = self.market_data.fetch_ohlcv(self.symbol)
        current_price = candles[-1][1]['close'].iloc[-1]

        risk_amount = self.portfolio.capital * self.risk_pct_per_trade
        if not self.risk_engine.can_open(self.symbol, direction, risk_amount):
            self.log(f"⛔ Trade rejected by RiskEngine for {self.symbol}")
            return

        if direction == TradeDirection.LONG:
            entry = self.first_candle['high']
            stop = self.first_candle['low']
            take = entry + (entry - stop) * self.profit_factor
        else:
            entry = self.first_candle['low']
            stop = self.first_candle['high']
            take = entry - (stop - entry) * self.profit_factor

        position_size = round(risk_amount / abs(entry - stop), 2)
        self.active_trade = Trade(direction, entry, stop, take, position_size, datetime.datetime.now(pytz.timezone('Europe/Moscow')))

        # Изпращане на ордер към Execution Engine
        self.execution.place_order(self.symbol, direction.value, position_size, entry)
        self.log(f"🚀 Trade OPEN {self.symbol} {direction.value}")

    async def check_exit_conditions(self):
        if not self.active_trade:
            return
        candles = self.market_data.fetch_ohlcv(self.symbol)
        current_price = candles[-1][1]['close'].iloc[-1]
        trade = self.active_trade

        if trade.direction == TradeDirection.LONG:
            if current_price >= trade.take_profit:
                await self.close_trade(current_price, "WIN - TP")
            elif current_price <= trade.stop_loss:
                await self.close_trade(current_price, "LOSS - SL")
        else:
            if current_price <= trade.take_profit:
                await self.close_trade(current_price, "WIN - TP")
            elif current_price >= trade.stop_loss:
                await self.close_trade(current_price, "LOSS - SL")

    async def close_trade(self, exit_price: float, reason: str):
        trade = self.active_trade
        trade.exit_price = exit_price
        trade.exit_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
        trade.profit = (exit_price - trade.entry_price if trade.direction == TradeDirection.LONG else trade.entry_price - exit_price) * trade.position_size
        trade.status = "WIN" if trade.profit > 0 else "LOSS"

        self.portfolio.update([trade])
        self.risk_engine.update_after_trade(trade.profit)
        self.active_trade = None
        self.log(f"🏁 Trade CLOSED {self.symbol} Profit={trade.profit:.2f} Reason={reason}")

    def log(self, message: str):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {message}")
