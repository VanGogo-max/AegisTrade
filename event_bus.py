# core/risk/event_bus.py

import threading
import time
from queue import Queue

class EventBus:
    def __init__(self):
        self.queue = Queue()

    def emit(self, event):
        """Добавя event в queue"""
        self.queue.put(event)

    def get_next(self, timeout=0.01):
        """Връща следващия event или None"""
        try:
            return self.queue.get(timeout=timeout)
        except:
            return None

    def start_processing(self, handler):
        """
        Стартира отделен thread за обработка на events.
        handler: callable(event)
        """
        def loop():
            while True:
                event = self.get_next()
                if event:
                    handler(event)
                else:
                    time.sleep(0.001)
        t = threading.Thread(target=loop, daemon=True)
        t.start()
