# notification_service.py
# Central Notification & Alerting Service for GRSM
# Thread-safe, supports multiple channels (console, file, webhook placeholder)

import threading
import time

class NotificationService:
    """
    Sends alerts and notifications for critical events:
    - Risk halt
    - Health check failures
    - Execution errors
    - System startup / shutdown
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._subscribers = []  # callbacks or external hooks

    # ----------------- Subscription -----------------

    def subscribe(self, callback):
        """
        Register external notification handler (e.g. Telegram, Email, Webhook).
        """
        with self._lock:
            self._subscribers.append(callback)

    # ----------------- Core API -----------------

    def notify(self, level: str, message: str, context: dict = None):
        """
        level: INFO | WARNING | ERROR | CRITICAL
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        payload = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "context": context or {}
        }

        with self._lock:
            # Console output (default)
            print(f"[{payload['timestamp']}] [{level}] {message} | {payload['context']}")

            # External hooks
            for callback in self._subscribers:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"[NotificationService] Callback error: {e}")

    # ----------------- Convenience Wrappers -----------------

    def info(self, message: str, context: dict = None):
        self.notify("INFO", message, context)

    def warning(self, message: str, context: dict = None):
        self.notify("WARNING", message, context)

    def error(self, message: str, context: dict = None):
        self.notify("ERROR", message, context)

    def critical(self, message: str, context: dict = None):
        self.notify("CRITICAL", message, context)
