"""
AegisTrade - Logger
"""
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

def get_logger(name: str):
    return logger.bind(module=name)
backend/utils/i18n.py:
"""
AegisTrade - i18n
"""
_LANG = "en"
_STRINGS = {
    "en": {
        "bot_started": "Bot started",
        "bot_stopped": "Bot stopped",
        "dry_run_mode": "DRY RUN mode",
        "live_mode": "LIVE mode",
        "no_signal": "No signal",
        "mode_switched": "Mode switched to {mode}",
        "admin_started": "Admin server started on {host}:{port}",
    },
    "bg": {
        "bot_started": "Ботът стартира",
        "bot_stopped": "Ботът спря",
        "dry_run_mode": "ТЕСТ режим",
        "live_mode": "ЖИВО",
        "no_signal": "Няма сигнал",
        "mode_switched": "Режим: {mode}",
        "admin_started": "Админ сървър на {host}:{port}",
    }
}

def set_language(lang: str) -> None:
    global _LANG
    _LANG = lang

def t(key: str, **kwargs) -> str:
    s = _STRINGS.get(_LANG, _STRINGS["en"]).get(key, key)
    return s.format(**kwargs) if kwargs else s
backend/utils/ux_effects.py:
"""
AegisTrade - UX Effects
"""
import queue

UX_EVENT_QUEUE = queue.Queue()

class UXEvent:
    def __init__(self, event_type: str, name: str, **payload):
        self.event_type = event_type
        self.name = name
        self.payload = payload
