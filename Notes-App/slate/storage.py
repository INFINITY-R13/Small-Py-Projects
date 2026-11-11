"""Local JSON storage and note querying for Slate."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from slate.models import Note, normalize_tag


DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class AppSettings:
    """Persisted user interface preferences."""

    theme: str = "charcoal"  # "charcoal" (dark grey) | "ash" (light grey)
    editor_mode: str = "write"  # "write" | "split" | "preview"
    sort_by: str = "updated"  # "updated" | "title"
    selected_note_id: str | None = None
    zen_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize settings into a dictionary."""
        return {
            "theme": self.theme if self.theme in {"charcoal", "ash"} else "charcoal",
            "editor_mode": (
                self.editor_mode
                if self.editor_mode in {"write", "split", "preview"}
                else "write"
            ),
            "sort_by": self.sort_by if self.sort_by in {"updated", "title"} else "updated",
            "selected_note_id": self.selected_note_id,
            "zen_mode": bool(self.zen_mode),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        """Deserialize settings safely with defaults."""
        theme = data.get("theme", "charcoal")
        mode = data.get("editor_mode", "write")
        sort_by = data.get("sort_by", "updated")
        return cls(
            theme=theme if theme in {"charcoal", "ash"} else "charcoal",
            editor_mode=mode if mode in {"write", "split", "preview"} else "write",
            sort_by=sort_by if sort_by in {"updated", "title"} else "updated",
            selected_note_id=data.get("selected_note_id"),
            zen_mode=bool(data.get("zen_mode", False)),
        )


def _atomic_write_json(path: Path, payload: Any) -> None:
    """Atomically write JSON payload to `path` via a sibling temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def _create_seed_notes() -> list[Note]:
    """Create initial sample notes shown on first launch."""
    now = datetime.now(timezone.utc)

    return [
        Note(
            id="welcome-slate",
            title="Welcome to Slate",
            tags=["welcome", "guide"],
            pinned=True,
            created_at=(now - timedelta(hours=3)).isoformat(),
            updated_at=(now - timedelta(minutes=2)).isoformat(),
            content=(
                "A calm, monochrome workspace designed for clear thinking.\n\n"
                "## Highlights\n"
                "- **Charcoal & Ash Modes** — Switch effortlessly between matte dark grey and soft dove grey.\n"
                "- **Markdown Native** — Write in clean plain text, split view, or rendered preview.\n"
                "- **Focus Mode** — Collapse the sidebars with `Cmd+\\` for distraction-free writing.\n"
                "- **Local-First** — Every note is autosaved cleanly to disk as JSON.\n\n"
                "> \"Simplicity is about subtracting the obvious and adding the meaningful.\"\n\n"
                "### Quick Checklist\n"
                "- [x] Open Slate and explore the grey aesthetic\n"
                "- [ ] Try **Split** or **Preview** mode in the top toolbar\n"
                "- [ ] Toggle **Charcoal / Ash** theme in the bottom-left corner\n"
                "- [ ] Create your first note with `Cmd+N`\n"
            ),
        ),
        Note(
            id="monochrome-palette",
            title="Monochrome Design Notes",
            tags=["design", "aesthetic"],
            pinned=False,
            created_at=(now - timedelta(days=1, hours=2)).isoformat(),
            updated_at=(now - timedelta(hours=1)).isoformat(),
            content=(
                "Good grey interfaces avoid pure black and pure white. Instead, they step gently "
                "between slate surfaces so hierarchy reads naturally.\n\n"
                "### Surface Hierarchy\n"
                "| Layer | Charcoal Hex | Ash Hex |\n"
                "| --- | --- | --- |\n"
                "| Navigation Rail | `#161719` | `#E4E6EA` |\n"
                "| Note Index | `#1B1D20` | `#ECEEF1` |\n"
                "| Editorial Canvas | `#202226` | `#F3F4F6` |\n"
                "| Elevated Card | `#26292E` | `#E2E4E9` |\n\n"
                "```python\n"
                "# Quiet typography + generous margins = effortless focus\n"
                "def clarity(noise: int) -> str:\n"
                "    return 'calm' if noise == 0 else 'refactor'\n"
                "```\n"
            ),
        ),
        Note(
            id="weekly-reading",
            title="Reading & Thought Log",
            tags=["journal", "ideas"],
            pinned=False,
            created_at=(now - timedelta(days=2)).isoformat(),
            updated_at=(now - timedelta(hours=6)).isoformat(),
            content=(
                "Collecting small observations before they vanish:\n\n"
                "1. Keep tools quiet so thoughts stay loud.\n"
                "2. Write short paragraphs; leave room around ideas.\n"
                "3. Review pinned notes every Sunday evening.\n\n"
                "- [ ] Sketch clean architecture for next Python CLI utility\n"
                "- [ ] Summarize chapters 3–4 on visual hierarchy\n"
            ),
        ),
        Note(
            id="shortcut-cheatsheet",
            title="Keyboard Shortcuts",
            tags=["guide"],
            pinned=False,
            created_at=(now - timedelta(days=4)).isoformat(),
            updated_at=(now - timedelta(days=1)).isoformat(),
            content=(
                "Move around Slate without touching the mouse:\n\n"
                "- `Cmd+N` — Create a new note\n"
                "- `Cmd+F` — Jump to search\n"
                "- `Cmd+Shift+P` — Pin or unpin current note\n"
                "- `Cmd+Shift+T` — Toggle Charcoal / Ash theme\n"
                "- `Cmd+1` / `Cmd+2` / `Cmd+3` — Write / Split / Preview mode\n"
                "- `Cmd+\\` — Toggle Zen Focus mode\n"
                "- `Cmd+E` — Export note as Markdown\n"
                "- `Cmd+Backspace` — Move note to Trash\n"
            ),
        ),
    ]


class NoteStore:
    """Manages loading, saving, querying, and organizing notes on disk."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
        self.notes_path = self.data_dir / "notes.json"
        self.settings_path = self.data_dir / "settings.json"
        self._notes: dict[str, Note] = {}
        self.settings: AppSettings = AppSettings()

    def load(self) -> None:
        """Load notes and settings from disk, seeding initial notes on first run."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.settings_path.exists():
            try:
                raw_settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(raw_settings, dict):
                    self.settings = AppSettings.from_dict(raw_settings)
            except (OSError, json.JSONDecodeError):
                self.settings = AppSettings()

        if not self.notes_path.exists():
            seed = _create_seed_notes()
            self._notes = {note.id: note for note in seed}
            self.save_notes()
            return

        try:
            raw_notes = json.loads(self.notes_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw_notes = []

        self._notes = {}
        if isinstance(raw_notes, list):
            for entry in raw_notes:
                if isinstance(entry, dict):
                    note = Note.from_dict(entry)
                    self._notes[note.id] = note

    def save_notes(self) -> None:
        """Persist all notes atomically to JSON."""
        payload = [note.to_dict() for note in self._notes.values()]
        _atomic_write_json(self.notes_path, payload)

    def save_settings(self) -> None:
        """Persist current UI settings atomically to JSON."""
        _atomic_write_json(self.settings_path, self.settings.to_dict())

    def get(self, note_id: str) -> Note | None:
        """Return a note by ID if present."""
        return self._notes.get(note_id)

    def all_notes(self) -> list[Note]:
        """Return all notes including trashed ones."""
        return list(self._notes.values())

    def create_note(
        self,
        title: str = "",
        content: str = "",
        tags: list[str] | None = None,
        pinned: bool = False,
    ) -> Note:
        """Create, store, and persist a new note."""
        note = Note(
            title=title,
            content=content,
            tags=list(tags or []),
            pinned=pinned,
        )
        self._notes[note.id] = note
        self.save_notes()
        return note

    def upsert_note(self, note: Note, touch: bool = True) -> Note:
        """Save changes to an existing or new note."""
        if touch:
            note.touch()
        self._notes[note.id] = note
        self.save_notes()
        return note

    def toggle_pin(self, note_id: str) -> Note | None:
        """Toggle pinned status for an active note."""
        note = self._notes.get(note_id)
        if note is None:
            return None
        note.pinned = not note.pinned
        self.save_notes()
        return note

    def move_to_trash(self, note_id: str) -> Note | None:
        """Soft-delete a note into Trash and unpin it."""
        note = self._notes.get(note_id)
        if note is None:
            return None
        note.trashed = True
        note.pinned = False
        note.touch()
        self.save_notes()
        return note

    def restore_from_trash(self, note_id: str) -> Note | None:
        """Restore a trashed note back to All Notes."""
        note = self._notes.get(note_id)
        if note is None:
            return None
        note.trashed = False
        note.touch()
        self.save_notes()
        return note

    def delete_permanently(self, note_id: str) -> bool:
        """Remove a note permanently from storage."""
        if note_id not in self._notes:
            return False
        del self._notes[note_id]
        self.save_notes()
        return True

    def empty_trash(self) -> int:
        """Delete all trashed notes permanently, returning removed count."""
        trash_ids = [nid for nid, note in self._notes.items() if note.trashed]
        if not trash_ids:
            return 0
        for nid in trash_ids:
            del self._notes[nid]
        self.save_notes()
        return len(trash_ids)

    def counts_by_view(self) -> dict[str, int]:
        """Return note counts for sidebar smart views."""
        active = [n for n in self._notes.values() if not n.trashed]
        pinned = [n for n in active if n.pinned]
        trashed = [n for n in self._notes.values() if n.trashed]
        return {
            "all": len(active),
            "pinned": len(pinned),
            "trash": len(trashed),
        }

    def all_tags_with_counts(self) -> list[tuple[str, int]]:
        """Return sorted `(tag, count)` pairs across all non-trashed notes."""
        counter: Counter[str] = Counter()
        for note in self._notes.values():
            if not note.trashed:
                counter.update(note.tags)
        return sorted(counter.items(), key=lambda item: (-item[1], item[0]))

    def filter_notes(
        self,
        view: str = "all",
        tag: str | None = None,
        query: str = "",
        sort_by: str = "updated",
    ) -> list[Note]:
        """Filter and sort notes for the middle note list pane."""
        normalized_tag = normalize_tag(tag) if tag else None

        filtered: list[Note] = []
        for note in self._notes.values():
            if view == "trash":
                if not note.trashed:
                    continue
            else:
                if note.trashed:
                    continue
                if view == "pinned" and not note.pinned:
                    continue

            if normalized_tag and normalized_tag not in note.tags:
                continue

            if query and not note.matches_query(query):
                continue

            filtered.append(note)

        if sort_by == "title":
            filtered.sort(
                key=lambda n: (
                    0 if (n.pinned and view != "trash") else 1,
                    n.display_title.lower(),
                    n.updated_at,
                )
            )
        else:
            filtered.sort(
                key=lambda n: (
                    1 if (n.pinned and view != "trash") else 0,
                    n.updated_at,
                ),
                reverse=True,
            )

        return filtered
