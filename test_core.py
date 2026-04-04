import pytest
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock

from backend.execution.execution_engine import (
    ExecutionEngine, ExecutionRequest, ExecutionResult,
    BaseExecutionAdapter, OrderSide, OrderType
)
from backend.risk.risk_engine import RiskEngine, RiskLimits


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_result(**kwargs):
    defaults = dict(
        exchange="hyperliquid",
        symbol="BTC",
        order_id="123",
        status="filled",
        filled_quantity=Decimal("0.01"),
        avg_price=Decimal("67000"),
        raw_response={},
    )
    defaults.update(kwargs)
    return ExecutionResult(**defaults)


def make_request(**kwargs):
    defaults = dict(
        exchange="hyperliquid",
        symbol="BTC",
        side=OrderSide.BUY,
        quantity=Decimal("0.01"),
        order_type=OrderType.MARKET,
    )
    defaults.update(kwargs)
    return ExecutionRequest(**defaults)


class MockAdapter(BaseExecutionAdapter):
    def __init__(self, result=None):
        self._result = result or make_result()
        self.place_order = AsyncMock(return_value=self._result)
        self.cancel_order = AsyncMock(return_value=True)


# ─────────────────────────────────────────────
# EXECUTION ENGINE
# ─────────────────────────────────────────────

class TestExecutionEngine:

    def test_register_adapter(self):
        engine = ExecutionEngine()
        adapter = MockAdapter()
        engine.register_adapter("hyperliquid", adapter)
        assert engine._get_adapter("hyperliquid") is adapter

    def test_register_duplicate_raises(self):
        engine = ExecutionEngine()
        engine.register_adapter("hyperliquid", MockAdapter())
        with pytest.raises(ValueError, match="already registered"):
            engine.register_adapter("hyperliquid", MockAdapter())

    def test_get_missing_adapter_raises(self):
        engine = ExecutionEngine()
        with pytest.raises(ValueError, match="No adapter registered"):
            engine._get_adapter("gmx")

    @pytest.mark.asyncio
    async def test_execute_market_order(self):
        engine = ExecutionEngine()
        adapter = MockAdapter()
        engine.register_adapter("hyperliquid", adapter)
        req = make_request()
        result = await engine.execute(req)
        assert result.status == "filled"
        adapter.place_order.assert_called_once_with(req)

    @pytest.mark.asyncio
    async def test_execute_limit_order_without_price_raises(self):
        engine = ExecutionEngine()
        engine.register_adapter("hyperliquid", MockAdapter())
        req = make_request(order_type=OrderType.LIMIT, price=None)
        with pytest.raises(ValueError, match="Limit order requires price"):
            await engine.execute(req)

    @pytest.mark.asyncio
    async def test_execute_limit_order_with_price(self):
        engine = ExecutionEngine()
        engine.register_adapter("hyperliquid", MockAdapter())
        req = make_request(order_type=OrderType.LIMIT, price=Decimal("67000"))
        result = await engine.execute(req)
        assert result.status == "filled"

    @pytest.mark.asyncio
    async def test_cancel_order(self):
        engine = ExecutionEngine()
        adapter = MockAdapter()
        engine.register_adapter("hyperliquid", adapter)
        result = await engine.cancel("hyperliquid", "BTC", "order_123")
        assert result is True
        adapter.cancel_order.assert_called_once_with("BTC", "order_123")


# ─────────────────────────────────────────────
# RISK ENGINE
# ─────────────────────────────────────────────

class TestRiskEngine:

    def setup_method(self):
        self.risk = RiskEngine()
        self.risk.set_account_equity(10000.0)
        self.risk.set_symbol_limits(
            symbol="BTC",
            max_position_size=1.0,
            max_notional=50000.0,
            max_leverage=5.0,
        )

    def test_valid_buy_order(self):
        assert self.risk.validate_order("BTC", "buy", 67000, 0.1, 0.0) is True

    def test_exceeds_position_size(self):
        # max_position_size = 1.0, trying to open 1.5
        assert self.risk.validate_order("BTC", "buy", 67000, 1.5, 0.0) is False

    def test_exceeds_notional(self):
        # 0.8 * 67000 = 53600 > max_notional 50000
        assert self.risk.validate_order("BTC", "buy", 67000, 0.8, 0.0) is False

    def test_exceeds_leverage(self):
        # equity=10000, notional=0.75*67000=50250, leverage=5.025 > 5.0
        assert self.risk.validate_order("BTC", "buy", 67000, 0.75, 0.0) is False

    def test_sell_reduces_position(self):
        # current long 0.5, sell 0.3 → net 0.2, should pass
        assert self.risk.validate_order("BTC", "sell", 67000, 0.3, 0.5) is True

    def test_no_limits_set_always_passes(self):
        assert self.risk.validate_order("ETH", "buy", 3000, 10.0, 0.0) is True

    def test_calculate_notional(self):
        assert self.risk.calculate_notional(67000, 0.1) == pytest.approx(6700.0)

    def test_calculate_leverage(self):
        notional = self.risk.calculate_notional(67000, 0.1)
        lev = self.risk.calculate_leverage(notional)
        assert lev == pytest.approx(0.67)

    def test_leverage_zero_equity(self):
        self.risk.set_account_equity(0)
        assert self.risk.calculate_leverage(10000) == 0.0

    def test_set_account_equity(self):
        self.risk.set_account_equity(5000.0)
        assert self.risk.account_equity == 5000.0
      
