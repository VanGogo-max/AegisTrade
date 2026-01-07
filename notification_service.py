"""
notification_service.py

Enterprise Notification Service

Responsibilities:
- Subscribe to event bus
- Classify notification events
- Route notifications to admin / user channels
- Prepare hooks for sounds and animations (future UI layer)

No business logic. No UI code.
"""

import logging
from typing import Any, Dict, Callable, Optional

from event_bus import event_bus, Event


class NotificationLevel:
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @classmethod
    def is_valid(cls, level: str) -> bool:
        return level in (cls.INFO, cls.WARNING, cls.CRITICAL)


class NotificationEvent(Event):
    """
    Event representing a system notification.
    """

    def __init__(
        self,
        level: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        admin_only: bool = False,
    ) -> None:
        if not NotificationLevel.is_valid(level):
            raise ValueError(f"Invalid notification level: {level}")

        self.level = level
        self.message = message
        self.payload = payload or {}
        self.admin_only = admin_only


class NotificationService:
    """
    Central notification dispatcher.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger("notification_service")
        self._handlers: Dict[str, Callable[[NotificationEvent], None]] = {}

    # STEP A — Registration validation
    def register_handler(
        self,
        level: str,
        handler: Callable[[NotificationEvent], None],
    ) -> None:
        if not NotificationLevel.is_valid(level):
            raise ValueError(f"Invalid notification level: {level}")
        if not callable(handler):
            raise TypeError("Handler must be callable")

        self._handlers[level] = handler

    # STEP B — Routing & isolation
    def _dispatch(self, event: NotificationEvent) -> None:
        handler = self._handlers.get(event.level)
        if handler:
            handler(event)
        else:
            self._logger.info(
                "Notification",
                extra={
                    "level": event.level,
                    "message": event.message,
                    "payload": event.payload,
                    "admin_only": event.admin_only,
                },
            )

    # STEP C — Fault containment
    def handle_event(self, event: Event) -> None:
        if not isinstance(event, NotificationEvent):
            return

        try:
            self._dispatch(event)
        except Exception as exc:
            self._logger.exception(
                "Notification dispatch failure",
                extra={"error": str(exc)},
            )


_service = NotificationService()


def init_notification_service() -> None:
    """
    Initializes notification service and subscribes to event bus.
    Must be called once at application startup.
    """
    event_bus.subscribe(NotificationEvent, _service.handle_event)
