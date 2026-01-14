# main.py
"""
Entry point of the automated multi-exchange trading platform.

Responsibilities:
- Initialize full system via SystemBootstrap
- Start core services (health monitor, failover, routing)
- Keep process alive
- Handle global shutdown signals
"""

import signal
import sys
import time

from system_bootstrap import SystemBootstrap


def main():
    print("=== Starting Trading Platform ===")

    bootstrap = SystemBootstrap()
    components = bootstrap.initialize()

    router = components["router"]
    health_monitor = components["health_monitor"]
    failover = components["failover_orchestrator"]

    print("System initialized successfully.")
    print("Connected exchanges:", router.supported_exchanges())

    def shutdown_handler(signum, frame):
        print(f"Shutdown signal received: {signum}")
        bootstrap.shutdown(reason=f"Signal {signum}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print("System running. Waiting for trade intents...")

    # Main loop (orchestration layer stays idle until intents arrive)
    while True:
        time.sleep(5)
        health_monitor.tick()
        failover.tick()


if __name__ == "__main__":
    main()
