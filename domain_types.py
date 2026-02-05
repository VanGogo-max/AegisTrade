# domain_types.py
from typing import TypedDict, Dict, Any


# ============================================================
# Trade / Order data
# ============================================================

class TradeData(TypedDict):
    pair: str
    expected_price: float
    expected_size: float
    current_price: float
    pool_address: str
    to: str
    data: bytes
    value: int


# ============================================================
# MEV / Sandwich risk analysis
# ============================================================

class MEVRisk(TypedDict):
    block_trade: bool
    risk_score: float
    details: Dict[str, Any]


# ============================================================
# Mempool risk analysis
# ============================================================

class MempoolRisk(TypedDict):
    frontrun_detected: bool
    emergency_boost: bool
    pending_txs_count: int


# ============================================================
# Liquidity / OI / Funding risk analysis
# ============================================================

class LiquidityRisk(TypedDict):
    overall_risk: bool
    liquidity: float
    open_interest: float
    funding_rate: float
    details: Dict[str, Any]


# ============================================================
# Gas optimizer result
# ============================================================

class GasFees(TypedDict):
    maxFeePerGas: int
    maxPriorityFeePerGas: int
