# exchange_capabilities.py
"""
exchange_capabilities.py — FINAL

Declarative capability registry for supported exchanges.

Purpose:
- Single source of truth for WHAT an exchange supports
- Used by router, strategy validator, execution engine
- Prevents invalid order construction before adapter level

Design rules:
- NO execution logic
- NO network calls
- NO assumptions beyond documented capabilities
- Pure data definitions only

Sources (official docs):
- GMX v2: https://docs.gmx.io
- dYdX v4: https://docs.dydx.exchange
- Hyperliquid: https://docs.hyperliquid.xyz
- Kwenta: https://docs.kwenta.io
- Vertex: https://docs.vertexprotocol.com
- Apex: https://docs.apex.exchange
- KCEX: https://www.kcex.com/help
"""

from dataclasses import dataclass
from typing import Set, Dict


@dataclass(frozen=True)
class ExchangeCapabilities:
    exchange: str

    # Market / execution model
    execution_model: str          # onchain | offchain | hybrid
    orderbook: bool               # true if orderbook-based
    perpetuals: bool
    spot: bool

    # Order types
    order_types: Set[str]         # market, limit, stop, tp, sl
    reduce_only: bool
    post_only: bool
    partial_fills: bool

    # Margin / leverage
    max_leverage: int
    isolated_margin: bool
    cross_margin: bool

    # Latency class
    latency_class: str            # low | medium | high


EXCHANGE_CAPABILITIES: Dict[str, ExchangeCapabilities] = {

    # =====================
    # GMX v2
    # =====================
    "gmx_v2": ExchangeCapabilities(
        exchange="gmx_v2",
        execution_model="onchain",
        orderbook=False,
        perpetuals=True,
        spot=False,
        order_types={"market", "stop", "tp", "sl"},
        reduce_only=True,
        post_only=False,
        partial_fills=False,
        max_leverage=100,
        isolated_margin=True,
        cross_margin=False,
        latency_class="high",
    ),

    # =====================
    # dYdX v4
    # =====================
    "dydx_v4": ExchangeCapabilities(
        exchange="dydx_v4",
        execution_model="hybrid",
        orderbook=True,
        perpetuals=True,
        spot=False,
        order_types={"market", "limit", "stop"},
        reduce_only=True,
        post_only=True,
        partial_fills=True,
        max_leverage=20,
        isolated_margin=False,
        cross_margin=True,
        latency_class="low",
    ),

    # =====================
    # Hyperliquid
    # =====================
    "hyperliquid": ExchangeCapabilities(
        exchange="hyperliquid",
        execution_model="offchain",
        orderbook=True,
        perpetuals=True,
        spot=False,
        order_types={"market", "limit"},
        reduce_only=True,
        post_only=True,
        partial_fills=True,
        max_leverage=50,
        isolated_margin=False,
        cross_margin=True,
        latency_class="low",
    ),

    # =====================
    # Kwenta
    # =====================
    "kwenta": ExchangeCapabilities(
        exchange="kwenta",
        execution_model="onchain",
        orderbook=False,
        perpetuals=True,
        spot=False,
        order_types={"market"},
        reduce_only=True,
        post_only=False,
        partial_fills=False,
        max_leverage=25,
        isolated_margin=True,
        cross_margin=False,
        latency_class="high",
    ),

    # =====================
    # Vertex Protocol
    # =====================
    "vertex": ExchangeCapabilities(
        exchange="vertex",
        execution_model="hybrid",
        orderbook=True,
        perpetuals=True,
        spot=True,
        order_types={"market", "limit"},
        reduce_only=True,
        post_only=True,
        partial_fills=True,
        max_leverage=10,
        isolated_margin=False,
        cross_margin=True,
        latency_class="medium",
    ),

    # =====================
    # Apex Protocol
    # =====================
    "apex": ExchangeCapabilities(
        exchange="apex",
        execution_model="offchain",
        orderbook=True,
        perpetuals=True,
        spot=False,
        order_types={"market", "limit"},
        reduce_only=True,
        post_only=True,
        partial_fills=True,
        max_leverage=20,
        isolated_margin=False,
        cross_margin=True,
        latency_class="low",
    ),

    # =====================
    # KCEX
    # =====================
    "kcex": ExchangeCapabilities(
        exchange="kcex",
        execution_model="offchain",
        orderbook=True,
        perpetuals=True,
        spot=True,
        order_types={"market", "limit"},
        reduce_only=True,
        post_only=True,
        partial_fills=True,
        max_leverage=100,
        isolated_margin=True,
        cross_margin=True,
        latency_class="low",
    ),
}


def get_exchange_capabilities(exchange: str) -> ExchangeCapabilities:
    """
    Fetch capabilities for a given exchange identifier.
    """
    key = exchange.lower()
    if key not in EXCHANGE_CAPABILITIES:
        raise KeyError(f"Unknown exchange capabilities: {exchange}")
    return EXCHANGE_CAPABILITIES[key]
