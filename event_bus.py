"""
event_bus.py

Central synchronous Event Bus for decoupled communication
between core trading logic and infrastructure layers.

Design goals:
- No business logic
- No external dependencies
- Deterministic behavior
- Safe failure isolation
"""

from typing import Callable, Dict, List, Type
from threading import RLock
import logging


class Event:
    """Base class for all events."""
    pass


EventHandler = Callable[[Event], None]


class EventBus:
    """
    Enterprise-grade in-process event bus.

    Characteristics:
    - Thread-safe
    - Fan-out delivery
    - No handler coupling
    - Failure isolation per handler
    """

    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[EventHandler]] = {}
        self._lock = RLock()
        self._logger = logging.getLogger("event_bus")

    def subscribe(self, event_type: Type[Event], handler: EventHandler) -> None:
        """
        Register handler for specific event type.
        """
        if not issubclass(event_type, Event):
            raise TypeError("event_type must inherit from Event")

        with self._lock:
            self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        """
        Publish event to all subscribed handlers.
        """
        event_type = type(event)

        with self._lock:
            handlers = list(self._subscribers.get(event_type, []))

        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                self._logger.exception(
                    "Event handler failure",
                    extra={
                        "event_type": event_type.__name__,
                        "handler": getattr(handler, "__name__", repr(handler)),
                        "error": str(exc),
                    },
                )


# Global singleton (explicit, controlled usage)
event_bus = EventBus()
