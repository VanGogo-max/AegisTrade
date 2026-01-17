# state_persistence.py
# State Persistence and Snapshot for GRSM
# Supports fail-safe recovery and event log replay

import threading
import json
import os
from datetime import datetime

class StatePersistence:
    """
    Handles saving and loading snapshots and event logs.
    """

    def __init__(self, snapshot_dir="snapshots", event_log_file="event_log.json"):
        self.snapshot_dir = snapshot_dir
        self.event_log_file = event_log_file
        self._lock = threading.RLock()
        os.makedirs(self.snapshot_dir, exist_ok=True)
        if not os.path.exists(self.event_log_file):
            with open(self.event_log_file, "w") as f:
                json.dump([], f)

    # ----------------- Snapshot -----------------
    def save_snapshot(self, snapshot: dict):
        with self._lock:
            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
            file_path = f"{self.snapshot_dir}/snapshot_{timestamp}.json"
            with open(file_path, "w") as f:
                json.dump(snapshot, f, indent=4)
            return file_path

    def load_latest_snapshot(self):
        with self._lock:
            files = sorted(os.listdir(self.snapshot_dir), reverse=True)
            for fname in files:
                if fname.startswith("snapshot_") and fname.endswith(".json"):
                    with open(os.path.join(self.snapshot_dir, fname), "r") as f:
                        return json.load(f)
            return None

    # ----------------- Event Log -----------------
    def append_event(self, event: dict):
        with self._lock:
            with open(self.event_log_file, "r+") as f:
                events = json.load(f)
                events.append(event)
                f.seek(0)
                json.dump(events, f, indent=4)

    def load_event_log(self):
        with self._lock:
            with open(self.event_log_file, "r") as f:
                return json.load(f)
