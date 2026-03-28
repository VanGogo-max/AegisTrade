class Config:
    """
    Централна конфигурация на бота
    """

    # ---------------- GENERAL ----------------

    SYMBOL = "ETH"
    DEFAULT_DEX = "gmx"

    LOOP_INTERVAL = 5  # секунди

    DRY_RUN = True  # 🔥 True = без реални сделки

    # ---------------- TRADING ----------------

    TRADE_SIZE = 0.01

    USE_MULTI_DEX = True
    SPLIT_ORDERS = False

    # ---------------- RISK ----------------

    MAX_DRAWDOWN_PERCENT = 20
    STOP_LOSS_PERCENT = 10
    TAKE_PROFIT_PERCENT = 20
    MAX_LEVERAGE = 5

    # ---------------- STRATEGY ----------------

    PRICE_CHANGE_THRESHOLD = 1  # %

    # ---------------- NETWORK ----------------

    RPC_URL = "https://arb1.arbitrum.io/rpc"

    # ---------------- WALLET ----------------

    PRIVATE_KEY = "YOUR_PRIVATE_KEY"

    # ---------------- LOGGING ----------------

    LOG_LEVEL = "INFO"
