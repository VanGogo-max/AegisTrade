# config.py
"""
Responsibility:
- Centralized configuration for the trading application
- Single source of truth for runtime parameters

Does NOT depend on:
- bots
- strategies
- exchange adapters
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    # Trading mode
    MODE: str = "spot"  # "spot" or "futures"

    # Exchange configuration
    EXCHANGE: str = "binance"
    SYMBOL: str = "BTC/USDT"

    # Strategy
    STRATEGY: str = "turtle_rsi"

    # Capital
    INITIAL_BALANCE: float = 1000.0

    # Runtime
    PRICE_POLL_INTERVAL_SEC: float = 1.0
    LOG_TRADES: bool = True
