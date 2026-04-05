"""
conftest.py — AegisTrade root pytest configuration
Place this file at: /workspaces/AegisTrade/conftest.py

Provides shared fixtures for all test modules.
Run with: PYTHONPATH=/workspaces/AegisTrade pytest backend/tests/ -v
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Path setup ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Async event loop ────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for all async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ── Config fixture ──────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def base_config():
    """Minimal config dict that satisfies all modules."""
    return {
        "exchange": "hyperliquid",
        "symbol": "BTC-USD-PERP",
        "dry_run": True,
        "initial_capital": 10_000.0,
        "risk": {
            "max_position_size": 0.02,       # 2% per trade
            "max_drawdown": 0.10,            # 10% max drawdown
            "max_daily_loss": 0.05,          # 5% daily loss limit
            "max_open_positions": 3,
            "stop_loss_pct": 0.015,          # 1.5%
            "take_profit_pct": 0.03,         # 3%
        },
        "execution": {
            "slippage_tolerance": 0.001,
            "retry_attempts": 3,
            "order_timeout": 10.0,
        },
        "feeds": {
            "poll_interval": 1.0,
            "symbols": ["BTC-USD-PERP", "ETH-USD-PERP"],
        },
        "logging": {
            "level": "DEBUG",
            "format": "text",
        },
    }


# ── Mock price feed ─────────────────────────────────────────────────────────
@pytest.fixture
def mock_price_feed():
    """Price feed that returns deterministic BTC prices."""
    feed = AsyncMock()
    feed.get_price = AsyncMock(return_value=65_000.0)
    feed.get_prices = AsyncMock(return_value={
        "BTC-USD-PERP": 65_000.0,
        "ETH-USD-PERP": 3_500.0,
    })
    feed.is_healthy = AsyncMock(return_value=True)
    feed.start = AsyncMock()
    feed.stop = AsyncMock()
    return feed


# ── Mock execution engine ───────────────────────────────────────────────────
@pytest.fixture
def mock_execution_engine():
    """Execution engine that always succeeds in dry-run."""
    engine = AsyncMock()
    engine.submit = AsyncMock(return_value={
        "order_id": "mock-order-001",
        "status": "filled",
        "filled_price": 65_000.0,
        "filled_qty": 0.01,
        "fee": 0.65,
    })
    engine.cancel = AsyncMock(return_value=True)
    engine.is_healthy = AsyncMock(return_value=True)
    return engine


# ── Mock state manager ──────────────────────────────────────────────────────
@pytest.fixture
def mock_state_manager():
    """In-memory state manager stub."""
    sm = MagicMock()
    sm.get_position = MagicMock(return_value=None)
    sm.set_position = MagicMock()
    sm.get_balance  = MagicMock(return_value=10_000.0)
    sm.update_balance = MagicMock()
    sm.get_daily_pnl  = MagicMock(return_value=0.0)
    sm.save = AsyncMock()
    sm.load = AsyncMock()
    return sm


# ── Sample OHLCV candles ────────────────────────────────────────────────────
@pytest.fixture
def sample_candles():
    """10 BTC candles for strategy testing."""
    base = 64_000.0
    candles = []
    for i in range(10):
        o = base + i * 100
        candles.append({
            "timestamp": 1_700_000_000 + i * 60,
            "open":  o,
            "high":  o + 150,
            "low":   o - 80,
            "close": o + 100,
            "volume": 12.5 + i * 0.5,
        })
    return candles


# ── Sample ExecutionRequest ─────────────────────────────────────────────────
@pytest.fixture
def sample_execution_request():
    """Valid ExecutionRequest-compatible dict."""
    return {
        "symbol":    "BTC-USD-PERP",
        "side":      "buy",
        "order_type": "market",
        "quantity":  0.01,
        "price":     None,
        "reduce_only": False,
        "meta":      {"strategy": "ema_crossover", "signal_score": 0.82},
    }
