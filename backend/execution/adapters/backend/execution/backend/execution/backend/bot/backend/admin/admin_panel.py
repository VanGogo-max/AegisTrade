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
                self._send(200, {
                    "codes": _referral.list_codes(),
                    "tiers": _referral.subscription_tiers()
                })
            else:
                self._send(503, {"error": "Referral not initialised"})

        elif path == "/ux_events":
            from backend.utils.ux_effects import UX_EVENT_QUEUE
            events = []
            while not UX_EVENT_QUEUE.empty():
                try:
                    ev = UX_EVENT_QUEUE.get_nowait()
                    events.append({
                        "type": ev.event_type,
                        "name": ev.name,
                        **ev.payload
                    })
                except Exception:
                    break
            self._send(200, {"events": events})

        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if not self._auth():
            self._send(401, {"error": "Unauthorized"})
            return
        path = urlparse(self.path).path
        body = self._body()

        if path == "/start":
            from backend.bot import trading_loop as tl
            if tl.is_running():
                self._send(200, {"status": "already_running"})
                return
            asyncio.create_task(tl.get_loop().run())
            self._send(200, {"status": "started"})

        elif path == "/stop":
            from backend.bot import trading_loop as tl
            tl.set_running(False)
            self._send(200, {"status": "stopped"})

        elif path == "/mode":
            dry = body.get("dry_run", True)
            from backend.bot import trading_loop as tl
            tl.set_mode(bool(dry))
            mode = "DRY_RUN" if dry else "LIVE"
            log.info(t("mode_switched", mode=mode))
            self._send(200, {"mode": mode})

        elif path == "/settings":
            lang = body.get("lang")
            if lang:
                set_language(lang)
            symbol = body.get("symbol")
            if symbol:
                from backend.bot import trading_loop as tl
                tl.set_symbol(symbol)
            self._send(200, {"status": "updated"})

        elif path == "/referral/generate":
            if not _referral:
                self._send(503, {"error": "Referral not initialised"})
                return
            owner = body.get("owner", "admin")
            tier = body.get("tier", "basic")
            code = _referral.generate_code(owner, tier)
            loop = asyncio.new_event_loop()
            data = loop.run_until_complete(
                _referral.register_code(code, owner, tier)
            )
            loop.close()
            self._send(200, {
                "code": code,
                "link": _referral.get_link(code),
                **data
            })

        elif path == "/risk/unlock":
            if _bot_loop:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(_bot_loop.state.set_locked(False))
                loop.run_until_complete(_bot_loop.state.set_halted(False))
                loop.close()
                self._send(200, {"status": "unlocked"})
            else:
                self._send(503, {"error": "Bot not initialised"})

        else:
            self._send(404, {"error": "Not found"})


def create_admin_server(
    bot_loop_obj, referral_obj: ReferralSystem
) -> HTTPServer:
    global _bot_loop, _referral
    _bot_loop = bot_loop_obj
    _referral = referral_obj
    server = HTTPServer((ADMIN_HOST, ADMIN_PORT), AegisHandler)
    log.info(t("admin_started", host=ADMIN_HOST, port=ADMIN_PORT))
    return server


async def run_admin_server(
    bot_loop_obj, referral_obj: ReferralSystem
) -> None:
    server = create_admin_server(bot_loop_obj, referral_obj)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, server.serve_forever)
