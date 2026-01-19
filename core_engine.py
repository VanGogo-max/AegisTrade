# core_engine.py

"""
Core Engine

Role:
- Orchestrates full trading lifecycle
- Connects:
    strategies
    filter_stack
    risk_engine
    execution_engine
    trade_logger
- Runs in:
    real trading
    paper trading
    shadow mode
"""

from typing import List
from loguru import logger


class CoreEngine:
    def __init__(
        self,
        strategies: List,
        filter_stack,
        risk_engine,
        execution_engine,
        trade_logger,
        shadow_engine=None,
    ):
        self.strategies = strategies
        self.filter_stack = filter_stack
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self.trade_logger = trade_logger
        self.shadow_engine = shadow_engine

    def run_cycle(self, market_data: dict):
        for strategy in self.strategies:
            try:
                signal = strategy.generate_signal(market_data)
                if not signal:
                    continue

                logger.info(f"Signal from {strategy.name}: {signal}")

                filtered = self.filter_stack.apply(signal, market_data)
                if not filtered:
                    logger.info("Signal rejected by filters")
                    continue

                risk_checked = self.risk_engine.evaluate(filtered)
                if not risk_checked:
                    logger.info("Signal rejected by risk engine")
                    continue

                result = self.execution_engine.execute(risk_checked)

                self.trade_logger.log(result)

                if self.shadow_engine:
                    self.shadow_engine.record(signal, result)

            except Exception as e:
                logger.exception(f"CoreEngine error in {strategy.name}: {e}")
