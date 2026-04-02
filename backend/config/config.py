import os


class Config:

    # ---------------- TRADING ----------------
    SYMBOL = os.getenv("SYMBOL", "BTC")
    DEFAULT_DEX = os.getenv("DEFAULT_DEX", "hyperliquid")
    TRADE_SIZE = float(os.getenv("TRADE_SIZE", "100"))
    LOOP_INTERVAL = float(os.getenv("LOOP_INTERVAL", "10"))
    SPLIT_ORDERS = os.getenv("SPLIT_ORDERS", "false").lower() == "true"

    # ---------------- MODE ----------------
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

    # ---------------- RISK ----------------
    MAX_LEVERAGE = float(os.getenv("MAX_LEVERAGE", "10"))
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))
    MAX_DAILY_DRAWDOWN = float(os.getenv("MAX_DAILY_DRAWDOWN", "0.05"))

    # ---------------- STATE ----------------
    STATE_FILE = os.getenv("STATE_FILE", "backend/state/state.json")
