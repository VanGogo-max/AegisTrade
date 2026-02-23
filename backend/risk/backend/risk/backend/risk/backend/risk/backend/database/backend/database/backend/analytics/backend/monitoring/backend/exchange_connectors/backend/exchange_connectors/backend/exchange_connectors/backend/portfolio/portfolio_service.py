"""
Portfolio Service

Responsibilities:
- Aggregate positions across multiple DEXes and strategies
- Compute total balance, margin usage, leverage, and exposure
- Interface with risk engine for pre-trade and portfolio-level checks
- Provide data to analytics and liquidation engine
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class Position:
    symbol: str
    size: float  # positive for long, negative for short
    avg_entry_price: float
    unrealized_pnl: float = 0.0


@dataclass
class Portfolio:
    positions: Dict[str, Position] = None
    total_balance: float = 0.0
    used_margin: float = 0.0
    leverage: float = 0.0

    def __post_init__(self):
        if self.positions is None:
            self.positions = {}


class PortfolioService:

    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}  # strategy_id -> portfolio
        self._lock = asyncio.Lock()

    # ---------------------------------------------------
    # Portfolio lifecycle
    # ---------------------------------------------------

    async def create_portfolio(self, strategy_id: str, initial_balance: float = 0.0):
        async with self._lock:
            self.portfolios[strategy_id] = Portfolio(total_balance=initial_balance)

    async def get_portfolio(self, strategy_id: str) -> Optional[Portfolio]:
        async with self._lock:
            return self.portfolios.get(strategy_id)

    # ---------------------------------------------------
    # Position management
    # ---------------------------------------------------

    async def update_position(
        self, strategy_id: str, symbol: str, size_delta: float, price: float
    ):
        async with self._lock:
            portfolio = self.portfolios.get(strategy_id)
            if not portfolio:
                portfolio = Portfolio()
                self.portfolios[strategy_id] = portfolio

            pos = portfolio.positions.get(symbol)
            if pos:
                # Update avg entry
                new_size = pos.size + size_delta
                if new_size != 0:
                    pos.avg_entry_price = (
                        pos.avg_entry_price * pos.size + price * size_delta
                    ) / new_size
                    pos.size = new_size
                else:
                    # Position closed
                    pos.size = 0.0
                    pos.avg_entry_price = 0.0
            else:
                # New position
                portfolio.positions[symbol] = Position(symbol=symbol, size=size_delta, avg_entry_price=price)

            # Update unrealized PnL
            for p in portfolio.positions.values():
                p.unrealized_pnl = (price - p.avg_entry_price) * p.size

            # Update total portfolio metrics
            portfolio.used_margin = sum(abs(p.size * p.avg_entry_price) for p in portfolio.positions.values())
            portfolio.leverage = portfolio.used_margin / max(1e-9, portfolio.total_balance)

    # ---------------------------------------------------
    # Portfolio metrics
    # ---------------------------------------------------

    async def get_total_balance(self, strategy_id: str) -> float:
        async with self._lock:
            portfolio = self.portfolios.get(strategy_id)
            if not portfolio:
                return 0.0
            unrealized = sum(p.unrealized_pnl for p in portfolio.positions.values())
            return portfolio.total_balance + unrealized

    async def get_exposure(self, strategy_id: str) -> Dict[str, float]:
        async with self._lock:
            portfolio = self.portfolios.get(strategy_id)
            if not portfolio:
                return {}
            return {s.symbol: s.size for s in portfolio.positions.values()}
