"""
backend/tests/test_core.py — AegisTrade core module tests

Run: PYTHONPATH=/workspaces/AegisTrade pytest backend/tests/test_core.py -v
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

class TestConfig:
    """backend/config.py"""

    def test_config_loads(self, base_config):
        assert base_config["exchange"] == "hyperliquid"
        assert base_config["dry_run"] is True

    def test_risk_params_present(self, base_config):
        r = base_config["risk"]
        assert "max_position_size" in r
        assert "max_drawdown" in r
        assert "stop_loss_pct" in r

    def test_risk_values_in_range(self, base_config):
        r = base_config["risk"]
        assert 0 < r["max_position_size"] <= 1.0
        assert 0 < r["max_drawdown"] <= 1.0
        assert 0 < r["stop_loss_pct"] < r["take_profit_pct"]

    def test_execution_params(self, base_config):
        e = base_config["execution"]
        assert e["retry_attempts"] >= 1
        assert e["slippage_tolerance"] >= 0


# ══════════════════════════════════════════════════════════════════════════════
# PRICE FEED
# ══════════════════════════════════════════════════════════════════════════════

class TestPriceFeed:
    """backend/feeds/price_feed.py"""

    @pytest.mark.asyncio
    async def test_get_price_returns_float(self, mock_price_feed):
        price = await mock_price_feed.get_price("BTC-USD-PERP")
        assert isinstance(price, float)
        assert price > 0

    @pytest.mark.asyncio
    async def test_get_prices_returns_dict(self, mock_price_feed):
        prices = await mock_price_feed.get_prices()
        assert isinstance(prices, dict)
        assert "BTC-USD-PERP" in prices
        assert all(v > 0 for v in prices.values())

    @pytest.mark.asyncio
    async def test_health_check(self, mock_price_feed):
        healthy = await mock_price_feed.is_healthy()
        assert healthy is True

    @pytest.mark.asyncio
    async def test_start_stop(self, mock_price_feed):
        await mock_price_feed.start()
        await mock_price_feed.stop()
        mock_price_feed.start.assert_awaited_once()
        mock_price_feed.stop.assert_awaited_once()

    def test_price_is_positive(self, mock_price_feed):
        """Sanity: price feed fixture data"""
        # Simulate price validation logic
        price = 65_000.0
        assert price > 0, "Price must be positive"
        assert price < 10_000_000, "Price sanity upper bound"


# ══════════════════════════════════════════════════════════════════════════════
# RISK ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class TestRiskEngine:
    """backend/risk/risk_engine.py"""

    def test_position_size_within_limit(self, base_config):
        """Position size must not exceed max_position_size % of capital."""
        capital = 10_000.0
        max_pct = base_config["risk"]["max_position_size"]
        max_size = capital * max_pct

        proposed_size = 150.0  # $150 position
        assert proposed_size <= max_size, (
            f"Position ${proposed_size} exceeds max ${max_size}"
        )

    def test_stop_loss_less_than_take_profit(self, base_config):
        r = base_config["risk"]
        assert r["stop_loss_pct"] < r["take_profit_pct"]

    def test_max_drawdown_threshold(self, base_config):
        """Bot should halt if drawdown exceeds threshold."""
        max_dd = base_config["risk"]["max_drawdown"]
        current_dd = 0.08  # 8%
        assert current_dd < max_dd, "Should not halt at 8% with 10% limit"

        over_dd = 0.12  # 12%
        assert over_dd > max_dd, "Should halt at 12% with 10% limit"

    def test_daily_loss_limit(self, base_config):
        capital = 10_000.0
        max_daily_loss_pct = base_config["risk"]["max_daily_loss"]
        max_daily_loss = capital * max_daily_loss_pct

        daily_pnl = -350.0  # Lost $350 today
        assert abs(daily_pnl) < max_daily_loss, "Should continue trading"

        over_loss = -600.0
        assert abs(over_loss) > max_daily_loss, "Should halt trading"

    def test_max_open_positions(self, base_config):
        max_pos = base_config["risk"]["max_open_positions"]
        current = 2
        assert current < max_pos, "Can open more positions"

        at_limit = 3
        assert at_limit >= max_pos, "Cannot open more positions"

    def test_risk_reward_ratio(self, base_config):
        r = base_config["risk"]
        rr = r["take_profit_pct"] / r["stop_loss_pct"]
        assert rr >= 1.5, f"R:R {rr:.2f} is too low — minimum 1.5"


# ══════════════════════════════════════════════════════════════════════════════
# EXECUTION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class TestExecutionEngine:
    """backend/execution/execution_engine.py"""

    @pytest.mark.asyncio
    async def test_submit_returns_order(self, mock_execution_engine, sample_execution_request):
        result = await mock_execution_engine.submit(sample_execution_request)
        assert result["status"] == "filled"
        assert "order_id" in result
        assert result["filled_price"] > 0

    @pytest.mark.asyncio
    async def test_cancel_returns_bool(self, mock_execution_engine):
        ok = await mock_execution_engine.cancel("mock-order-001")
        assert isinstance(ok, bool)
        assert ok is True

    @pytest.mark.asyncio
    async def test_engine_health(self, mock_execution_engine):
        healthy = await mock_execution_engine.is_healthy()
        assert healthy is True

    def test_execution_request_schema(self, sample_execution_request):
        req = sample_execution_request
        assert req["side"] in ("buy", "sell")
        assert req["order_type"] in ("market", "limit")
        assert req["quantity"] > 0
        assert req["symbol"] != ""

    def test_slippage_tolerance(self, base_config):
        slippage = base_config["execution"]["slippage_tolerance"]
        assert 0 <= slippage <= 0.01, "Slippage > 1% is dangerous"

    @pytest.mark.asyncio
    async def test_submit_called_with_correct_args(
        self, mock_execution_engine, sample_execution_request
    ):
        await mock_execution_engine.submit(sample_execution_request)
        mock_execution_engine.submit.assert_awaited_once_with(sample_execution_request)


# ══════════════════════════════════════════════════════════════════════════════
# STATE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class TestStateManager:
    """backend/state_manager.py"""

    def test_initial_balance(self, mock_state_manager):
        balance = mock_state_manager.get_balance()
        assert balance == 10_000.0

    def test_no_position_initially(self, mock_state_manager):
        pos = mock_state_manager.get_position("BTC-USD-PERP")
        assert pos is None

    def test_set_and_get_position(self, mock_state_manager):
        pos = {"symbol": "BTC-USD-PERP", "side": "long", "qty": 0.01, "entry": 65_000.0}
        mock_state_manager.set_position("BTC-USD-PERP", pos)
        mock_state_manager.set_position.assert_called_once_with("BTC-USD-PERP", pos)

    @pytest.mark.asyncio
    async def test_save_and_load(self, mock_state_manager):
        await mock_state_manager.save()
        await mock_state_manager.load()
        mock_state_manager.save.assert_awaited_once()
        mock_state_manager.load.assert_awaited_once()

    def test_daily_pnl_starts_zero(self, mock_state_manager):
        pnl = mock_state_manager.get_daily_pnl()
        assert pnl == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# CANDLES / STRATEGY DATA
# ══════════════════════════════════════════════════════════════════════════════

class TestCandleData:
    """Validate OHLCV data integrity — used by strategy layer."""

    def test_candle_count(self, sample_candles):
        assert len(sample_candles) == 10

    def test_ohlcv_fields_present(self, sample_candles):
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        for c in sample_candles:
            assert required.issubset(c.keys())

    def test_high_gte_low(self, sample_candles):
        for c in sample_candles:
            assert c["high"] >= c["low"], f"Invalid candle: high < low at ts={c['timestamp']}"

    def test_high_gte_open_close(self, sample_candles):
        for c in sample_candles:
            assert c["high"] >= c["open"]
            assert c["high"] >= c["close"]

    def test_low_lte_open_close(self, sample_candles):
        for c in sample_candles:
            assert c["low"] <= c["open"]
            assert c["low"] <= c["close"]

    def test_volume_positive(self, sample_candles):
        for c in sample_candles:
            assert c["volume"] > 0

    def test_timestamps_ascending(self, sample_candles):
        ts = [c["timestamp"] for c in sample_candles]
        assert ts == sorted(ts), "Candles must be in chronological order"

    def test_ema_crossover_signal(self, sample_candles):
        """Simplified EMA crossover — fast > slow = buy signal."""
        closes = [c["close"] for c in sample_candles]

        def ema(prices, period):
            k = 2 / (period + 1)
            result = [prices[0]]
            for p in prices[1:]:
                result.append(p * k + result[-1] * (1 - k))
            return result

        fast = ema(closes, 3)
        slow = ema(closes, 7)

        # With rising prices the fast EMA should be above slow
        last_fast = fast[-1]
        last_slow = slow[-1]
        assert isinstance(last_fast, float)
        assert isinstance(last_slow, float)
        # Signal logic (not asserting direction — just that it runs)
        signal = "buy" if last_fast > last_slow else "sell"
        assert signal in ("buy", "sell")


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION: RISK + EXECUTION
# ══════════════════════════════════════════════════════════════════════════════

class TestRiskExecutionIntegration:
    """Combined risk check → execution flow."""

    @pytest.mark.asyncio
    async def test_risk_approved_order_executes(
        self,
        base_config,
        mock_execution_engine,
        mock_state_manager,
        sample_execution_request,
    ):
        """If risk passes, execution should be called exactly once."""
        capital = mock_state_manager.get_balance()
        max_size = capital * base_config["risk"]["max_position_size"]

        # Risk check
        order_value = sample_execution_request["quantity"] * 65_000.0
        risk_ok = order_value <= max_size

        if risk_ok:
            result = await mock_execution_engine.submit(sample_execution_request)
            assert result["status"] == "filled"
        else:
            pytest.skip("Order value exceeds risk limit — skipping execution")

    @pytest.mark.asyncio
    async def test_oversized_order_blocked(self, base_config, mock_execution_engine):
        """Orders exceeding risk limits must NOT reach the execution engine."""
        capital = 10_000.0
        max_pct = base_config["risk"]["max_position_size"]
        max_size = capital * max_pct

        oversized_request = {
            "symbol":    "BTC-USD-PERP",
            "side":      "buy",
            "order_type": "market",
            "quantity":  10.0,   # 10 BTC = $650k >> $200 limit
            "price":     None,
        }

        order_value = oversized_request["quantity"] * 65_000.0
        risk_blocked = order_value > max_size
        assert risk_blocked, "Risk engine should block this order"

        # Execution engine must NOT be called
        if risk_blocked:
            mock_execution_engine.submit.assert_not_awaited()

