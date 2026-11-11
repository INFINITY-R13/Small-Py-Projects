"""Data models and note text helpers for Slate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any
import uuid


_MD_PREFIX_RE = re.compile(r"^\s{0,3}(?:#{1,6}\s+|>\s+|[-*+]\s+\[[ xX]\]\s+|[-*+]\s+|\d+\.\s+)")
_MD_INLINE_RE = re.compile(r"(\*\*|__|\*|_|~~|`{1,3})")


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def normalize_tag(raw_tag: str) -> str:
    """Normalize a tag by removing leading hashes, whitespace, and lowering case."""
    cleaned = raw_tag.strip().lstrip("#").strip().lower()
    return re.sub(r"\s+", "-", cleaned)


def normalize_tags(tags: list[str]) -> list[str]:
    """Return deduplicated, normalized tags preserving original insertion order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in tags:
        tag = normalize_tag(item)
        if tag and tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result


def parse_iso_datetime(value: str) -> datetime:
    """Parse an ISO-8601 timestamp safely, defaulting to UTC now on invalid input."""
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return datetime.now(timezone.utc)


@dataclass
class Note:
    """Represents a single markdown-capable note."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    content: str = ""
    tags: list[str] = field(default_factory=list)
    pinned: bool = False
    trashed: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        self.tags = normalize_tags(self.tags)

    @property
    def display_title(self) -> str:
        """Return the note title or a clean placeholder for untitled notes."""
        stripped = self.title.strip()
        return stripped if stripped else "Untitled Note"

    @property
    def word_count(self) -> int:
        """Count words across the note body."""
        words = self.content.split()
        return len(words)

    @property
    def char_count(self) -> int:
        """Count characters in the note body."""
        return len(self.content)

    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time in whole minutes (minimum 1 min if non-empty)."""
        if self.word_count == 0:
            return 0
        return max(1, round(self.word_count / 200))

    def excerpt(self, max_len: int = 96) -> str:
        """Build a clean, markdown-stripped preview line for note cards."""
        lines: list[str] = []
        for raw_line in self.content.splitlines():
            line = _MD_PREFIX_RE.sub("", raw_line).strip()
            line = _MD_INLINE_RE.sub("", line).strip()
            if line and not set(line) <= {"-", "_", "*", "`"}:
                lines.append(line)
            if len(" ".join(lines)) >= max_len:
                break

        summary = " ".join(lines).strip()
        if not summary:
            return "No additional text"
        if len(summary) <= max_len:
            return summary
        return summary[: max_len - 1].rstrip() + "…"

    def relative_updated_label(self, now: datetime | None = None) -> str:
        """Format `updated_at` as a concise, human-friendly local time label."""
        current = now or datetime.now(timezone.utc).astimezone()
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc).astimezone()

        updated_local = parse_iso_datetime(self.updated_at).astimezone(current.tzinfo)
        delta_seconds = max(0, int((current - updated_local).total_seconds()))

        if delta_seconds < 60:
            return "Just now"
        if delta_seconds < 3600:
            return f"{delta_seconds // 60}m ago"
        if updated_local.date() == current.date():
            return updated_local.strftime("%H:%M")
        if (current.date() - updated_local.date()).days == 1:
            return "Yesterday"
        if updated_local.year == current.year:
            return updated_local.strftime("%b %d")
        return updated_local.strftime("%b %d, %Y")

    def detailed_updated_label(self) -> str:
        """Format `updated_at` with day and time for the editor header."""
        local_dt = parse_iso_datetime(self.updated_at).astimezone()
        now_local = datetime.now(timezone.utc).astimezone()
        if local_dt.date() == now_local.date():
            return f"Today, {local_dt.strftime('%H:%M')}"
        if (now_local.date() - local_dt.date()).days == 1:
            return f"Yesterday, {local_dt.strftime('%H:%M')}"
        return local_dt.strftime("%b %d, %Y · %H:%M")

    def matches_query(self, query: str) -> bool:
        """Return True if all whitespace-separated search terms match title, body, or tags."""
        terms = [t.strip().lower() for t in query.split() if t.strip()]
        if not terms:
            return True

        haystack_title = self.title.lower()
        haystack_body = self.content.lower()
        tag_set = {t.lower() for t in self.tags}

        for term in terms:
            if term.startswith("#") and len(term) > 1:
                needle = term[1:]
                if not any(needle in tag for tag in tag_set):
                    return False
            else:
                if (
                    term not in haystack_title
                    and term not in haystack_body
                    and not any(term in tag for tag in tag_set)
                ):
                    return False
        return True

    def touch(self) -> None:
        """Update `updated_at` to the current UTC timestamp."""
        self.updated_at = utc_now_iso()

    def to_markdown_document(self) -> str:
        """Render the note as a portable Markdown file string."""
        parts: list[str] = [f"# {self.display_title}"]
        if self.tags:
            tag_line = " ".join(f"#{tag}" for tag in self.tags)
            parts.append(f"*{tag_line}*")
        if self.content.strip():
            parts.append(self.content.rstrip())
        return "\n\n".join(parts) + "\n"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the note into a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": list(self.tags),
            "pinned": bool(self.pinned),
            "trashed": bool(self.trashed),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Note:
        """Deserialize a Note instance from a dictionary."""
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex[:12]),
            title=str(data.get("title") or ""),
            content=str(data.get("content") or ""),
            tags=list(data.get("tags") or []),
            pinned=bool(data.get("pinned", False)),
            trashed=bool(data.get("trashed", False)),
            created_at=str(data.get("created_at") or utc_now_iso()),
            updated_at=str(data.get("updated_at") or utc_now_iso()),
        )
