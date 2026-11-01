"""
Data models representing habits, streaks, and completion logs.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid


@dataclass
class Habit:
    name: str
    emoji: str = "✨"
    category: str = "Wellness"
    routine: str = "Anytime"  # Morning, Afternoon, Evening, Anytime
    frequency: str = "Every Day"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: date.today().isoformat())
    history: Dict[str, bool] = field(default_factory=dict)

    def is_completed(self, target_date: Optional[str] = None) -> bool:
        """Check if habit was marked completed on a given date (defaults to today)."""
        if target_date is None:
            target_date = date.today().isoformat()
        return bool(self.history.get(target_date, False))

    def set_completed(self, target_date: str, completed: bool) -> None:
        """Set completion status for a specific date."""
        if completed:
            self.history[target_date] = True
        else:
            self.history.pop(target_date, None)

    def toggle(self, target_date: Optional[str] = None) -> bool:
        """Toggle completion for the given date. Returns new completion status."""
        if target_date is None:
            target_date = date.today().isoformat()
        current = self.is_completed(target_date)
        new_state = not current
        self.set_completed(target_date, new_state)
        return new_state

    def calculate_streaks(self, ref_date: Optional[date] = None) -> Tuple[int, int]:
        """
        Calculate (current_streak, best_streak) in days.
        Current streak counts consecutive completed days up to today
        (or yesterday if today isn't logged yet).
        """
        if ref_date is None:
            ref_date = date.today()

        completed_dates = {
            date.fromisoformat(d_str)
            for d_str, done in self.history.items()
            if done
        }

        if not completed_dates:
            return 0, 0

        # Calculate current streak
        current_streak = 0
        pointer = ref_date
        if pointer in completed_dates:
            current_streak += 1
            pointer -= timedelta(days=1)
        elif (pointer - timedelta(days=1)) in completed_dates:
            # Active streak still intact from yesterday, today pending
            pointer -= timedelta(days=1)
        else:
            pointer = None

        if pointer is not None:
            while pointer in completed_dates:
                current_streak += 1
                pointer -= timedelta(days=1)

        # Calculate best all-time streak
        sorted_dates = sorted(completed_dates)
        best_streak = 0
        current_run = 0
        prev_date: Optional[date] = None

        for d in sorted_dates:
            if prev_date is None or d == prev_date + timedelta(days=1):
                current_run += 1
            else:
                current_run = 1
            prev_date = d
            if current_run > best_streak:
                best_streak = current_run

        best_streak = max(best_streak, current_streak)
        return current_streak, best_streak

    @property
    def total_completed(self) -> int:
        """Total number of times completed."""
        return sum(1 for completed in self.history.values() if completed)

    def get_recent_days(self, num_days: int = 7, end_date: Optional[date] = None) -> List[Tuple[date, bool]]:
        """
        Returns list of (date_obj, is_completed) ordered from oldest to newest
        for the given number of days ending at end_date (defaults to today).
        """
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(days=num_days - 1)
        results = []
        for i in range(num_days):
            d = start_date + timedelta(days=i)
            iso = d.isoformat()
            results.append((d, self.is_completed(iso)))
        return results

    def get_completion_rate(self, days: int = 30) -> float:
        """Percentage of completed days in the past N days since habit creation."""
        today_date = date.today()
        created = date.fromisoformat(self.created_at)
        start_date = max(today_date - timedelta(days=days - 1), created)
        total_possible = (today_date - start_date).days + 1
        if total_possible <= 0:
            return 0.0

        completed_count = 0
        for i in range(total_possible):
            d = start_date + timedelta(days=i)
            if self.is_completed(d.isoformat()):
                completed_count += 1

        return (completed_count / total_possible) * 100.0

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "category": self.category,
            "routine": self.routine,
            "frequency": self.frequency,
            "created_at": self.created_at,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Habit"),
            emoji=data.get("emoji", "✨"),
            category=data.get("category", "Wellness"),
            routine=data.get("routine", "Anytime"),
            frequency=data.get("frequency", "Every Day"),
            created_at=data.get("created_at", date.today().isoformat()),
            history=data.get("history", {}),
        )
