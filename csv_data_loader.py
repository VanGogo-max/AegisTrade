"""
csv_data_loader.py

Loads historical OHLCV data from CSV files.
"""

import csv
from typing import List, Dict, Any


class CSVDataLoader:
    """
    Loads and validates OHLCV market data from a CSV file.
    """

    REQUIRED_COLUMNS = {
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def load(self) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []

        with open(self.file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise ValueError("CSV file has no header.")

            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(f"CSV file missing columns: {missing}")

            for row in reader:
                bar = {
                    "timestamp": int(row["timestamp"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }
                data.append(bar)

        return data
