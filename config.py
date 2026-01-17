# config.py
# Global configuration for GRSM

class Config:
    """
    Central configuration class for GRSM.
    """

    # ----------------- Risk Limits -----------------
    MAX_DRAWDOWN_PCT = 0.25
    MAX_DAILY_LOSS_PCT = 0.10
    MAX_LEVERAGE = 5.0
    MAX_POSITION_PCT = 0.20
    MAX_CORRELATED_EXPOSURE_PCT = 0.50

    # ----------------- Execution -----------------
    DEFAULT_STARTING_BALANCE = 100000.0
    MAX_BATCH_SIZE = 5

    # ----------------- Health & Monitoring -----------------
    HEALTH_CHECK_INTERVAL_SEC = 1.0

    # ----------------- Logging & Persistence -----------------
    SNAPSHOT_DIR = "snapshots"
    EVENT_LOG_FILE = "event_log.json"

    # ----------------- Strategy Defaults -----------------
    DEFAULT_STRATEGY_LIST = []

    # ----------------- Misc -----------------
    VERBOSE = True
