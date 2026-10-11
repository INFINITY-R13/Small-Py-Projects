"""
Calculation History Management.
Stores previous calculations and allows recalling expressions or results.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from typing import List, Optional


@dataclass
class HistoryEntry:
    expression: str
    result: str
    timestamp: str


class HistoryManager:
    """Manages history entries with optional local JSON persistence."""

    def __init__(self, storage_path: Optional[str] = None, max_entries: int = 50):
        self.storage_path = storage_path
        self.max_entries = max_entries
        self.entries: List[HistoryEntry] = []
        if self.storage_path and os.path.exists(self.storage_path):
            self.load()

    def add(self, expression: str, result: str) -> HistoryEntry:
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = HistoryEntry(expression=expression, result=result, timestamp=timestamp)
        self.entries.insert(0, entry)  # Most recent first
        if len(self.entries) > self.max_entries:
            self.entries.pop()
        if self.storage_path:
            self.save()
        return entry

    def clear(self) -> None:
        self.entries.clear()
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                os.remove(self.storage_path)
            except OSError:
                pass

    def get_all(self) -> List[HistoryEntry]:
        return list(self.entries)

    def save(self) -> None:
        if not self.storage_path:
            return
        try:
            data = [asdict(e) for e in self.entries]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def load(self) -> None:
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = [HistoryEntry(**item) for item in data]
        except (OSError, json.JSONDecodeError, TypeError):
            self.entries = []
