"""
AegisTrade — i18n
"""
from __future__ import annotations
from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "bot_started": "Bot started",
        "bot_stopped": "Bot stopped",
        "dry_run_mode": "Running in DRY-RUN (simulation) mode",
        "live_mode": "Running in LIVE mode — real trades enabled",
        "signal_buy": "BUY signal on {symbol} @ {price}",
        "signal_sell": "SELL signal on {symbol} @ {price}",
        "no_signal": "No signal — holding",
        "order_placed": "Order placed: {side} {qty} {symbol} @ {price}",
        "order_simulated": "[SIM] Order: {side} {qty} {symbol} @ {price}",
        "position_closed": "Position closed: {symbol} PnL={pnl:.2f}",
        "risk_daily_limit": "Daily loss limit reached ({pct:.1%}) — reducing exposure",
        "risk_daily_stop": "Daily loss {pct:.1%} exceeds hard stop — trading halted",
        "risk_weekly_lock": "Weekly loss {pct:.1%} — system LOCKED",
        "risk_ok": "Risk checks passed",
        "insufficient_balance": "Insufficient balance for trade",
        "regime_bull": "Market regime: BULL",
        "regime_bear": "Market regime: BEAR",
        "regime_neutral": "Market regime: NEUTRAL",
        "regime_crash": "Market regime: CRASH",
        "regime_euphoria": "Market regime: EUPHORIA",
        "price_feed_ok": "Price feed OK: {symbol} @ {price}",
        "price_feed_fallback": "Primary feed failed — using fallback",
        "price_feed_error": "Price feed unavailable for {symbol}",
        "admin_started": "Admin panel started on {host}:{port}",
        "mode_switched": "Mode switched to {mode}",
    },
    "bg": {
        "bot_started": "Ботът стартира",
        "bot_stopped": "Ботът спря",
        "dry_run_mode": "Работи в DRY-RUN (симулация) режим",
        "live_mode": "Работи в LIVE режим — реални сделки активирани",
        "signal_buy": "BUY сигнал за {symbol} @ {price}",
        "signal_sell": "SELL сигнал за {symbol} @ {price}",
        "no_signal": "Няма сигнал — изчакване",
        "order_placed": "Поръчка изпратена: {side} {qty} {symbol} @ {price}",
        "order_simulated": "[СИМ] Поръчка: {side} {qty} {symbol} @ {price}",
        "position_closed": "Позиция затворена: {symbol} PnL={pnl:.2f}",
        "risk_daily_limit": "Дневен лимит загуба достигнат ({pct:.1%})",
        "risk_daily_stop": "Дневна загуба {pct:.1%} — търговията е спряна",
        "risk_weekly_lock": "Седмична загуба {pct:.1%} — системата е ЗАКЛЮЧЕНА",
        "risk_ok": "Рисковите проверки преминаха",
        "insufficient_balance": "Недостатъчен баланс за сделка",
        "regime_bull": "Пазарен режим: БИЧИ",
        "regime_bear": "Пазарен режим: МЕЧИ",
        "regime_neutral": "Пазарен режим: НЕУТРАЛЕН",
        "regime_crash": "Пазарен режим: СРИВ",
        "regime_euphoria": "Пазарен режим: ЕУФОРИЯ",
        "price_feed_ok": "Ценови поток OK: {symbol} @ {price}",
        "price_feed_fallback": "Основният поток не работи — използва се резервен",
        "price_feed_error": "Ценовият поток е недостъпен за {symbol}",
        "admin_started": "Администраторски панел стартира на {host}:{port}",
        "mode_switched": "Режимът е сменен на {mode}",
    },
}

_CURRENT_LANG: str = "en"


def set_language(lang: str) -> None:
    global _CURRENT_LANG
    if lang in TRANSLATIONS:
        _CURRENT_LANG = lang


def t(key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(_CURRENT_LANG, TRANSLATIONS["en"])
    template = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
