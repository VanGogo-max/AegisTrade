"""
AegisTrade — Admin Panel
"""
from __future__ import annotations
import asyncio
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from backend.config.config import ADMIN_HOST, ADMIN_PORT, ADMIN_TOKEN
from backend.analytics.pnl_engine import PnLEngine
from backend.referral.referral_system import ReferralSystem
from backend.utils.logger import get_logger
from backend.utils.i18n import t, set_language

log = get_logger(__name__)

_pnl_engine = PnLEngine()
_bot_loop = None
_referral: ReferralSystem | None = None


def _json(data: Any) -> bytes:
    return json.dumps(data, default=str).encode()


def _cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
    handler.send_header("Content-Type", "application/json")


class AegisHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.debug("Admin: " + format, *args)

    def _auth(self) -> bool:
        token = self.headers.get("Authorization", "").replace("Bearer ", "")
        return token == ADMIN_TOKEN

    def _send(self, code: int, data: Any) -> None:
        body = _json(data)
        self.send_response(code)
        _cors(self)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self):
        self.send_response(204)
        _cors(self)
        self.end_headers()

    def do_GET(self):
        if not self._auth():
            self._send(401, {"error": "Unauthorized"})
            return
        path = urlparse(self.path).path
        state = _bot_loop.state if _bot_loop else None

        if path == "/status":
            from backend.bot import trading_loop as tl
            self._send(200, {
                "running": tl.is_running(),
                "dry_run": tl.is_dry_run(),
                "regime": state.current_regime if state else "unknown",
                "locked": state.system_locked if state else False,
                "halted": state.trading_halted if state else False,
                "uptime": time.time(),
            })

        elif path == "/metrics":
            if state:
                report = _pnl_engine.full_report(state.trades, 50.0)
                self._send(200, {
                    **report,
                    "balance": round(state.balance, 2),
                    "equity": round(state.equity, 2),
                    "daily_pnl": round(state.daily_pnl, 2),
                    "weekly_pnl": round(state.weekly_pnl, 2),
                    "total_pnl": round(state.total_pnl, 2),
                })
            else:
                self._send(503, {"error": "Bot not initialised"})

        elif path == "/positions":
            if state:
                self._send(200, {"positions": list(state.positions.values())})
            else:
                self._send(503, {"error": "Bot not initialised"})

        elif path == "/pnl":
            if state:
                self._send(200, {
                    "summary": _pnl_engine.full_report(state.trades, 50.0),
                    "by_symbol": _pnl_engine.by_symbol(state.trades),
                    "by_strategy": _pnl_engine.by_strategy(state.trades),
                    "history": state.trades[-50:],
                })
            else:
                self._send(503, {"error": "Bot not initialised"})

        elif path == "/risk":
            if _bot_loop:
                self._send(200, _bot_loop.risk.snapshot())
            else:
                self._send(503, {"error": "Bot not initialised"})

        elif path == "/referral":
            if _referral:
