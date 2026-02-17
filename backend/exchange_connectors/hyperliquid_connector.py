import asyncio
import aiohttp
import websockets
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from .base_dex_connector import (
    BaseDexConnector,
    NormalizedOrder,
    NormalizedPosition,
)

logger = logging.getLogger(__name__)


# =========================
# CONFIG
# =========================

@dataclass
class HyperliquidConfig:
    wallet_address: str
    private_key: str
    rest_url: str = "_
