# event_bus.py
# Asynchronous EventBus for GRSM
# Thread-safe, supports publish/subscribe

import threading
from collections import defaultdict
from queue import Queue

class EventBus:
    """
    Simple thread-safe event bus for GRSM.
    Supports subscription, publishing, and event queue processing.
    """

    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.RLock()
        self._queue = Queue()
        self._worker_thread = threading.Thread(target=self._process_events)
        self._worker_thread.daemon = True
        self._worker_thread.start()

    # ----------------- Subscription -----------------
    def subscribe(self, event_type: str, callback):
        with self._lock:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    # ----------------- Publishing -----------------
    def publish(self, event_type: str, data):
        self._queue.put((event_type, data))

    # ----------------- Internal Processing -----------------
    def _process_events(self):
        while True:
            event_type, data = self._queue.get()
            with self._lock:
                for callback in self._subscribers.get(event_type, []):
                    try:
                        callback(data)
                    except Exception as e:
                        print(f"[EventBus] Error in callback for {event_type}: {e}")
            self._queue.task_done()
