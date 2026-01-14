# system_bootstrap.py
"""
Responsibility:
- Bootstraps the entire trading system
- Wires all core components together
- Registers exchanges, routers, health monitors and failover orchestrator
- Performs startup validation
"""

from exchange_router import ExchangeRouter
from exchange_registry import ExchangeRegistry
from exchange_health_monitor import ExchangeHealthMonitor
from global_failover_orchestrator import GlobalFailoverOrchestrator
from runtime_guard import RuntimeGuard


class SystemBootstrap:
    def __init__(self):
        self.registry = ExchangeRegistry()
        self.health_monitor = ExchangeHealthMonitor()
        self.failover_orchestrator = GlobalFailoverOrchestrator(self.health_monitor)
        self.router = None

    def initialize(self):
        """
        Initialize and validate full system graph.
        """
        RuntimeGuard.assert_ready("SystemBootstrap")

        adapters = self.registry.load_all_adapters()
        self.router = ExchangeRouter(adapters)

        for name, adapter in adapters.items():
            if hasattr(adapter, "failover_manager"):
                self.failover_orchestrator.register_failover_manager(
                    name, adapter.failover_manager
                )

        self.health_monitor.start_monitoring(list(adapters.keys()))

        return {
            "router": self.router,
            "health_monitor": self.health_monitor,
            "failover_orchestrator": self.failover_orchestrator,
        }

    def shutdown(self, reason: str):
        """
        Graceful global shutdown.
        """
        self.failover_orchestrator.emergency_halt_all(reason=reason)
