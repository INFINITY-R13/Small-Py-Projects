"""
Storage manager handling JSON persistence, default sample data,
and overall statistical aggregation for habits.
"""

from datetime import date, timedelta
import json
import os
from typing import Any, Dict, List, Optional
from app.models import Habit


DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "habits.json"
)


def generate_default_habits() -> List[Habit]:
    """Generates a curated set of aesthetic starter habits with realistic logs."""
    today = date.today()

    def d(days_ago: int) -> str:
        return (today - timedelta(days=days_ago)).isoformat()

    habits = [
        Habit(
            name="Morning Hydration (750ml)",
            emoji="💧",
            category="Health",
            routine="Morning",
            frequency="Every Day",
            created_at=d(14),
            history={
                d(0): True,
                d(1): True,
                d(2): True,
                d(3): True,
                d(4): True,
                d(5): False,
                d(6): True,
                d(7): True,
            }
        ),
        Habit(
            name="Mindful Meditation & Breathwork",
            emoji="🧘",
            category="Mindfulness",
            routine="Morning",
            frequency="Every Day",
            created_at=d(20),
            history={
                d(0): True,
                d(1): True,
                d(2): True,
                d(3): False,
                d(4): True,
                d(5): True,
                d(6): True,
                d(7): True,
            }
        ),
        Habit(
            name="30 Min Daily Movement / Jog",
            emoji="🏃",
            category="Fitness",
            routine="Morning",
            frequency="Every Day",
            created_at=d(30),
            history={
                d(0): False,
                d(1): True,
                d(2): True,
                d(3): True,
                d(4): True,
                d(5): True,
                d(6): False,
                d(7): True,
            }
        ),
        Habit(
            name="Read 20 Pages of a Book",
            emoji="📚",
            category="Learning",
            routine="Afternoon",
            frequency="Every Day",
            created_at=d(25),
            history={
                d(0): True,
                d(1): True,
                d(2): False,
                d(3): True,
                d(4): True,
                d(5): True,
                d(6): True,
                d(7): False,
            }
        ),
        Habit(
            name="Matcha or Herbal Infusion",
            emoji="🍵",
            category="Wellness",
            routine="Afternoon",
            frequency="Weekdays (Mon-Fri)",
            created_at=d(10),
            history={
                d(0): False,
                d(1): True,
                d(2): True,
                d(3): True,
                d(4): False,
                d(5): True,
                d(6): True,
            }
        ),
        Habit(
            name="Evening Reflection Journal",
            emoji="✍️",
            category="Mindfulness",
            routine="Evening",
            frequency="Every Day",
            created_at=d(18),
            history={
                d(0): False,
                d(1): True,
                d(2): True,
                d(3): True,
                d(4): True,
                d(5): True,
                d(6): True,
                d(7): True,
            }
        ),
        Habit(
            name="Screen-Free 30m Before Bed",
            emoji="💤",
            category="Self Care",
            routine="Evening",
            frequency="Every Day",
            created_at=d(12),
            history={
                d(0): False,
                d(1): True,
                d(2): True,
                d(3): True,
                d(4): True,
                d(5): False,
                d(6): True,
            }
        ),
    ]
    return habits


class HabitStore:
    """Manages loading, updating, and saving habits to disk."""

    def __init__(self, file_path: str = DEFAULT_DATA_PATH):
        self.file_path = file_path
        self._ensure_directory()
        self.habits: List[Habit] = self.load()

    def _ensure_directory(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load(self) -> List[Habit]:
        """Loads habits from JSON file or generates defaults if file does not exist."""
        if not os.path.exists(self.file_path):
            habits = generate_default_habits()
            self.save(habits)
            return habits

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list) or len(data) == 0:
                    habits = generate_default_habits()
                    self.save(habits)
                    return habits
                return [Habit.from_dict(item) for item in data]
        except Exception:
            habits = generate_default_habits()
            self.save(habits)
            return habits

    def save(self, habits: Optional[List[Habit]] = None) -> None:
        """Serializes habits list into JSON format."""
        if habits is not None:
            self.habits = habits

        self._ensure_directory()
        raw_data = [habit.to_dict() for habit in self.habits]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)

    def add_habit(self, habit: Habit) -> None:
        """Adds a new habit and persists to disk."""
        self.habits.insert(0, habit)
        self.save()

    def update_habit(self, habit: Habit) -> None:
        """Updates an existing habit by ID."""
        for idx, h in enumerate(self.habits):
            if h.id == habit.id:
                self.habits[idx] = habit
                break
        self.save()

    def delete_habit(self, habit_id: str) -> None:
        """Removes a habit by ID."""
        self.habits = [h for h in self.habits if h.id != habit_id]
        self.save()

    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """Finds a habit by ID."""
        for h in self.habits:
            if h.id == habit_id:
                return h
        return None

    def reset_defaults(self) -> None:
        """Restores default aesthetic starter habits."""
        self.habits = generate_default_habits()
        self.save()

    def get_stats_for_date(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Calculates daily completion stats for the given date."""
        if target_date is None:
            target_date = date.today().isoformat()

        total = len(self.habits)
        completed = sum(1 for h in self.habits if h.is_completed(target_date))
        percentage = (completed / total * 100.0) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "percentage": percentage,
            "target_date": target_date,
        }

    def get_overall_stats(self) -> Dict[str, Any]:
        """Calculates all-time aggregate statistics across all habits."""
        total_completions = sum(h.total_completed for h in self.habits)
        best_streak = max((h.calculate_streaks()[1] for h in self.habits), default=0)
        current_max_streak = max((h.calculate_streaks()[0] for h in self.habits), default=0)

        # 7-day daily completion counts
        today = date.today()
        week_summary = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            iso = d.isoformat()
            done = sum(1 for h in self.habits if h.is_completed(iso))
            total = len(self.habits)
            rate = (done / total * 100) if total > 0 else 0
            week_summary.append({
                "date": d,
                "iso": iso,
                "day_name": d.strftime("%a"),
                "completed": done,
                "total": total,
                "rate": rate,
            })

        return {
            "total_habits": len(self.habits),
            "total_completions": total_completions,
            "current_max_streak": current_max_streak,
            "best_streak": best_streak,
            "week_summary": week_summary,
        }
