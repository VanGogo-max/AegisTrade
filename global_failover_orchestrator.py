# global_failover_orchestrator.py
"""
Responsibility:
- Central orchestrator for failover across all exchanges
- Coordinates per-exchange FailoverManager
- Decides when to disable, reroute or halt execution globally
"""

from typing import Dict

from exchange_health_monitor import ExchangeHealthMonitor


class GlobalFailoverOrchestrator:
    def __init__(self, health_monitor: ExchangeHealthMonitor):
        self.health_monitor = health_monitor
        self._exchange_failovers: Dict[str, object] = {}

    def register_failover_manager(self, exchange: str, manager: object):
        self._exchange_failovers[exchange] = manager

    def evaluate(self):
        """
        Evaluate all exchanges and trigger local failovers if needed.
        """
        for exchange, manager in self._exchange_failovers.items():
            if not self.health_monitor.is_healthy(exchange):
                manager.activate_failover(reason="Global health monitor detected outage")

    def emergency_halt_all(self, reason: str):
        """
        Hard stop all trading on all exchanges.
        """
        for manager in self._exchange_failovers.values():
            manager.emergency_shutdown(reason=reason)
