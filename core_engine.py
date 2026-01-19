# core_engine.py
"""
Core Engine

Роля:
- Управлява lifecycle на системата
- Оркестрира потока:
  Strategy -> Filter Stack -> Risk Engine -> Order Executor -> Trade Logger
- Няма борсова логика (DEX-агностичен)
- Поддържа plug-and-play за нови стратегии и борси
"""

from typing import Dict, Any, List
from loguru import logger


class CoreEngine:
    def __init__(
        self,
        strategies: List[Any],
        filters: List[Any],
        risk_engine: Any,
        executors: Dict[str, Any],  # например {"GMX": gmx_executor}
    ):
        self.strategies = strategies
        self.filters = filters
        self.risk_engine = risk_engine
        self.executors = executors

    # ----------------------------
    # Main loop (single tick)
    # ----------------------------
    def run_once(self, market_data: Dict[str, Any]):
        logger.info("🔁 CoreEngine tick started")

        for strategy in self.strategies:
            signals = strategy.generate_signals(market_data)

            for signal in signals:
                if not self._pass_filters(signal):
                    continue

                trade_intent = self.risk_engine.evaluate(signal)
                if not trade_intent:
                    continue

                exchange = trade_intent["exchange"]
                executor = self.executors.get(exchange)

                if not executor:
                    logger.error(f"No executor registered for {exchange}")
                    continue

                if trade_intent["action"] == "OPEN":
                    result = executor.execute_open(trade_intent)
                elif trade_intent["action"] == "CLOSE":
                    result = executor.execute_close(trade_intent)
                else:
                    logger.error(f"Unknown action: {trade_intent['action']}")
                    continue

                logger.info(f"✅ Executed: {result}")

    # ----------------------------
    # Filters
    # ----------------------------
    def _pass_filters(self, signal: Dict[str, Any]) -> bool:
        for f in self.filters:
            if not f.allow(signal):
                logger.debug(f"❌ Filter blocked signal: {signal}")
                return False
        return True
