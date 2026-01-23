from enum import Enum

class ExchangeName(str, Enum):
    BINANCE = "binance"
    HYPERLIQUID = "hyperliquid"
    DYDX = "dydx"
    GMX = "gmx"
    APEX = "apex"
    KWENTA = "kwenta"
    VERTEX = "vertex"
    KCEX = "kcex"


# Кои борси реално се стартират от app.py
ACTIVE_EXCHANGES = {
    ExchangeName.BINANCE: True,
    ExchangeName.HYPERLIQUID: True,
    ExchangeName.DYDX: True,
    ExchangeName.GMX: True,
    ExchangeName.APEX: True,
    ExchangeName.KWENTA: True,
    ExchangeName.VERTEX: True,
    ExchangeName.KCEX: False,   # ← изрично изключена
}
