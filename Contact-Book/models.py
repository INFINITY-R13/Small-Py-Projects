"""
Contact Book Data Models and Calculations.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Tuple, Dict, Any
import hashlib


# Palette of soothing modern pastel colors for contact avatar backgrounds
AVATAR_COLORS = [
    ("#E0E7FF", "#4338CA"),  # Indigo
    ("#EDE9FE", "#6D28D9"),  # Purple
    ("#FCE7F3", "#BE185D"),  # Pink
    ("#FEE2E2", "#B91C1C"),  # Red
    ("#FEF3C7", "#B45309"),  # Amber
    ("#ECFDF5", "#047857"),  # Emerald
    ("#E0F2FE", "#0369A1"),  # Sky
    ("#F1F5F9", "#334155"),  # Slate
    ("#CCFBF1", "#0F766E"),  # Teal
]


@dataclass
class Contact:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    birth_date: str = ""  # Format: YYYY-MM-DD
    instagram: str = ""   # e.g. "alex_dev" (without or with @)
    category: str = "General"  # General, Friends, Family, Work, VIP
    is_favorite: bool = False
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    @property
    def clean_instagram(self) -> str:
        """Return the Instagram handle cleaned of @ or URL prefixes."""
        handle = self.instagram.strip()
        if not handle:
            return ""
        if "instagram.com/" in handle:
            handle = handle.split("instagram.com/")[-1]
        handle = handle.lstrip("@").strip().rstrip("/")
        return handle

    @property
    def instagram_url(self) -> str:
        """Return direct URL to the Instagram profile."""
        handle = self.clean_instagram
        if not handle:
            return ""
        return f"https://www.instagram.com/{handle}/"

    @property
    def initials(self) -> str:
        """Compute 1 or 2 letter initials for the avatar badge."""
        parts = self.name.strip().split()
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def avatar_theme(self) -> Tuple[str, str]:
        """Deterministic (background_hex, text_hex) based on contact name."""
        if not self.name.strip():
            return ("#E2E8F0", "#475569")
        h = int(hashlib.md5(self.name.strip().lower().encode("utf-8")).hexdigest(), 16)
        return AVATAR_COLORS[h % len(AVATAR_COLORS)]

    def get_birthday_details(self) -> Dict[str, Any]:
        """
        Calculate current age, days until next birthday, next age, and human summary.
        """
        if not self.birth_date or not self.birth_date.strip():
            return {
                "has_birthday": False,
                "current_age": None,
                "days_until": None,
                "next_age": None,
                "is_today": False,
                "is_soon": False,
                "summary": "No birth date provided",
                "badge": ""
            }

        try:
            b_date = datetime.strptime(self.birth_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            return {
                "has_birthday": False,
                "current_age": None,
                "days_until": None,
                "next_age": None,
                "is_today": False,
                "is_soon": False,
                "summary": f"Invalid date: {self.birth_date}",
                "badge": ""
            }

        today = date.today()
        # Current age
        current_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))

        # Next birthday occurrence
        try:
            this_year_birthday = b_date.replace(year=today.year)
        except ValueError:
            # Handle Feb 29 on non-leap years
            this_year_birthday = b_date.replace(year=today.year, day=28)

        if this_year_birthday < today:
            try:
                next_birthday = b_date.replace(year=today.year + 1)
            except ValueError:
                next_birthday = b_date.replace(year=today.year + 1, day=28)
            next_age = current_age + 1
        elif this_year_birthday == today:
            next_birthday = today
            next_age = current_age
        else:
            next_birthday = this_year_birthday
            next_age = current_age + 1

        days_until = (next_birthday - today).days
        is_today = (days_until == 0)
        is_soon = (0 <= days_until <= 30)

        month_name = b_date.strftime("%B %d, %Y")

        if is_today:
            summary = f"🎉 Today! Turning {current_age} years old"
            badge = "🎂 Birthday Today!"
        elif days_until == 1:
            summary = f"🎈 Tomorrow! Turning {next_age} years old"
            badge = "🎈 Tomorrow"
        elif is_soon:
            summary = f"In {days_until} days (turning {next_age})"
            badge = f"🎂 in {days_until}d"
        else:
            summary = f"{month_name} (Age {current_age})"
            badge = f"{b_date.strftime('%b %d')}"

        return {
            "has_birthday": True,
            "birth_date_obj": b_date,
            "formatted_date": month_name,
            "current_age": current_age,
            "next_age": next_age,
            "days_until": days_until,
            "is_today": is_today,
            "is_soon": is_soon,
            "summary": summary,
            "badge": badge
        }
