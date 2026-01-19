# trade_logger.py
# Модул за логване на всички търговски операции (Core + Shadow/Research)

import os
import sqlite3
from datetime import datetime
from loguru import logger
from threading import Lock

# ----------------------------
# Configuration
# ----------------------------
DB_PATH = os.getenv("DB_PATH", "data/trading.db")
LOCK = Lock()  # За thread-safe операции

# ----------------------------
# Database Initialization
# ----------------------------
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            strategy TEXT,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            exit_price REAL,
            size REAL,
            pnl REAL,
            chain TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"✅ Trade Logger DB initialized at {DB_PATH}")

# ----------------------------
# Trade Logging
# ----------------------------
def log_trade(
    strategy: str,
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    size: float,
    pnl: float,
    chain: str,
    notes: str = ""
):
    timestamp = datetime.utcnow().isoformat()
    with LOCK:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades (
                timestamp, strategy, symbol, side, entry_price, exit_price, size, pnl, chain, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, strategy, symbol, side, entry_price, exit_price, size, pnl, chain, notes))
        conn.commit()
        conn.close()
    logger.info(f"📈 Trade logged | {strategy} | {symbol} | {side} | PnL: {pnl}")

# ----------------------------
# Utility: Fetch Trades
# ----------------------------
def fetch_trades(limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ----------------------------
# Initialize DB on import
# ----------------------------
init_db()
