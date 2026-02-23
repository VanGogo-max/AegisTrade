"""
System Monitor

Responsibilities:
- Health checks for all backend services
- Track latency and execution delays
- Uptime metrics
- Alerting on failures or anomalies
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Callable


class ServiceStatus:
    def __init__(self, name: str):
        self.name = name
        self.last_heartbeat: float = 0.0
        self.latency: float = 0.0
        self.healthy: bool = True
        self.error: Optional[str] = None

    def heartbeat(self, latency: float = 0.0):
        self.last_heartbeat = time.time()
        self.latency = latency
        self.healthy = True
        self.error = None

    def mark_unhealthy(self, error: str):
        self.healthy = False
        self.error = error


class SystemMonitor:

    def __init__(self, check_interval: float = 5.0):
        self.services: Dict[str, ServiceStatus] = {}
        self.check_interval = check_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False

        # Optional callback on alert
        self.alert_callback: Optional[Callable[[ServiceStatus], None]] = None

    # ---------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------

    async def start(self):
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self._running = False
        if self._monitor_task:
            await self._monitor_task

    # ---------------------------------------------------
    # Service management
    # ---------------------------------------------------

    def register_service(self, name: str):
        if name not in self.services:
            self.services[name] = ServiceStatus(name)

    def heartbeat(self, name: str, latency: float = 0.0):
        if name in self.services:
            self.services[name].heartbeat(latency)
        else:
            self.register_service(name)
            self.services[name].heartbeat(latency)

    # ---------------------------------------------------
    # Monitoring loop
    # ---------------------------------------------------

    async def _monitor_loop(self):
        while self._running:
            self._check_services()
            await asyncio.sleep(self.check_interval)

    def _check_services(self):
        now = time.time()
        for service in self.services.values():
            # mark unhealthy if no heartbeat in last 2x interval
            if now - service.last_heartbeat > self.check_interval * 2:
                service.mark_unhealthy("No heartbeat")
                if self.alert_callback:
                    self.alert_callback(service)

    # ---------------------------------------------------
    # Metrics
    # ---------------------------------------------------

    def get_status(self) -> Dict[str, Dict]:
        return {
            name: {
                "healthy": svc.healthy,
                "latency": svc.latency,
                "last_heartbeat": svc.last_heartbeat,
                "error": svc.error,
            }
            for name, svc in self.services.items()
        }
