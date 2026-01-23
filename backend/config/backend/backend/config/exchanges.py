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


# Само реално работещите към момента
ACTIVE_EXCHANGES = {
    ExchangeName.BINANCE: True,
    ExchangeName.HYPERLIQUID: True,
    ExchangeName.DYDX: True,
    ExchangeName.GMX: True,

    # Архитектурно подготвени, но без автоматизирано трейдване още
    ExchangeName.APEX: False,
    ExchangeName.KWENTA: False,
    ExchangeName.VERTEX: False,

    # Няма публичен API за търговия → напълно изключена
    ExchangeName.KCEX: False,
}
