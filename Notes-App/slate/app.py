"""Main application window and orchestration for Slate."""

from __future__ import annotations

from pathlib import Path
import re
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QSplitter,
)

from slate.icons import svg_icon
from slate.models import Note
from slate.storage import NoteStore
from slate.themes import ThemePalette, build_stylesheet, get_palette
from slate.widgets.dialogs import ConfirmDialog, ShortcutsDialog
from slate.widgets.editor_pane import EditorPane
from slate.widgets.note_list import NoteListPane
from slate.widgets.sidebar import SidebarPane


def _safe_filename(title: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", title.strip()).strip("-.")
    return cleaned.lower() or "untitled-note"


class MainWindow(QMainWindow):
    """Three-pane grey-themed Notes window orchestrating sidebar, list, and editor."""

    def __init__(self, store: NoteStore | None = None) -> None:
        super().__init__()
        self.store = store or NoteStore()
        self.store.load()

        self._palette: ThemePalette = get_palette(self.store.settings.theme)
        self._current_view: str = "all"
        self._current_tag: str | None = None
        self._search_query: str = ""
        self._active_note_id: str | None = self.store.settings.selected_note_id
        self._dirty: bool = False

        self.setWindowTitle("Slate — Notes")
        self.setMinimumSize(900, 600)
        self.resize(1200, 760)
        self.setWindowIcon(svg_icon("slate_logo", self._palette.text_primary, size=32))

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(350)
        self._save_timer.timeout.connect(self.flush_pending_save)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setHandleWidth(1)
        self.setCentralWidget(self._splitter)

        self._sidebar = SidebarPane(self._palette, self._splitter)
        self._note_list = NoteListPane(self._palette, self._splitter)
        self._editor = EditorPane(self._palette, self._splitter)

        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(self._note_list)
        self._splitter.addWidget(self._editor)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 0)
        self._splitter.setStretchFactor(2, 1)
        self._splitter.setSizes([195, 305, 700])

        self._connect_signals()
        self._register_shortcuts()
        self.apply_theme(self.store.settings.theme, persist=False)
        self._editor.set_mode(self.store.settings.editor_mode)
        self._apply_zen_mode(self.store.settings.zen_mode, persist=False)
        self.refresh_ui()

    def _connect_signals(self) -> None:
        # Sidebar signals
        self._sidebar.new_note_requested.connect(self.create_new_note)
        self._sidebar.view_selected.connect(self._on_view_selected)
        self._sidebar.tag_selected.connect(self._on_tag_selected)
        self._sidebar.theme_toggle_requested.connect(self.toggle_theme)
        self._sidebar.help_requested.connect(self.show_shortcuts)

        # Note list signals
        self._note_list.note_selected.connect(self._on_note_selected)
        self._note_list.search_changed.connect(self._on_search_changed)
        self._note_list.sort_toggled.connect(self._on_sort_toggled)
        self._note_list.empty_trash_requested.connect(self._on_empty_trash)

        # Editor signals
        self._editor.note_edited.connect(self._on_note_edited)
        self._editor.tags_edited.connect(self._on_tags_edited)
        self._editor.pin_toggled.connect(self._on_pin_toggled)
        self._editor.trash_requested.connect(self._on_trash_note)
        self._editor.restore_requested.connect(self._on_restore_note)
        self._editor.delete_forever_requested.connect(self._on_delete_forever)
        self._editor.export_requested.connect(self.export_current_note)
        self._editor.mode_changed.connect(self._on_mode_changed)
        self._editor.zen_toggled.connect(self.toggle_zen_mode)
        self._editor.create_note_requested.connect(self.create_new_note)

    def _register_shortcuts(self) -> None:
        bindings = [
            ("Ctrl+N", self.create_new_note),
            ("Ctrl+F", self._focus_search),
            ("Ctrl+Shift+P", self._on_pin_toggled),
            ("Ctrl+Shift+T", self.toggle_theme),
            ("Ctrl+1", lambda: self._set_editor_mode("write")),
            ("Ctrl+2", lambda: self._set_editor_mode("split")),
            ("Ctrl+3", lambda: self._set_editor_mode("preview")),
            ("Ctrl+\\", self.toggle_zen_mode),
            ("Ctrl+E", self.export_current_note),
            ("Ctrl+Backspace", self._on_trash_note),
        ]
        self._shortcuts: list[QShortcut] = []
        for seq, handler in bindings:
            shortcut = QShortcut(QKeySequence(seq), self)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)

    def apply_theme(self, theme_name: str, persist: bool = True) -> None:
        """Apply Charcoal (dark grey) or Ash (light grey) styling globally."""
        palette = get_palette(theme_name)
        self._palette = palette
        self.setStyleSheet(build_stylesheet(palette))
        self._sidebar.apply_palette(palette)
        self._note_list.apply_palette(palette)
        self._editor.apply_palette(palette)
        self.setWindowIcon(svg_icon("slate_logo", palette.text_primary, size=32))

        if persist:
            self.store.settings.theme = palette.name
            self.store.save_settings()

    def toggle_theme(self) -> None:
        """Switch between Charcoal Slate and Ash Grey themes."""
        next_theme = "ash" if self._palette.name == "charcoal" else "charcoal"
        self.apply_theme(next_theme, persist=True)

    def toggle_zen_mode(self) -> None:
        """Toggle distraction-free Zen mode hiding sidebars."""
        self._apply_zen_mode(not self.store.settings.zen_mode, persist=True)

    def _apply_zen_mode(self, enabled: bool, persist: bool = True) -> None:
        self._sidebar.setVisible(not enabled)
        self._note_list.setVisible(not enabled)
        self._editor.set_zen_mode(enabled)
        if persist:
            self.store.settings.zen_mode = enabled
            self.store.save_settings()

    def _focus_search(self) -> None:
        if self.store.settings.zen_mode:
            self._apply_zen_mode(False, persist=True)
        self._note_list.focus_search()

    def _set_editor_mode(self, mode: str) -> None:
        self._editor.set_mode(mode)
        self._on_mode_changed(mode)

    def _on_mode_changed(self, mode: str) -> None:
        self.store.settings.editor_mode = mode
        self.store.save_settings()

    def _on_view_selected(self, view: str) -> None:
        self.flush_pending_save()
        self._current_view = view
        self._current_tag = None
        self.refresh_ui()

    def _on_tag_selected(self, tag: str | None) -> None:
        self.flush_pending_save()
        self._current_tag = tag
        if tag is not None:
            self._current_view = "all"
        self.refresh_ui()

    def _on_search_changed(self, query: str) -> None:
        self.flush_pending_save()
        self._search_query = query
        self.refresh_ui(refresh_sidebar=False)

    def _on_sort_toggled(self) -> None:
        self.store.settings.sort_by = (
            "title" if self.store.settings.sort_by == "updated" else "updated"
        )
        self.store.save_settings()
        self.refresh_ui(refresh_sidebar=False)

    def _on_note_selected(self, note_id: str) -> None:
        if note_id == self._active_note_id:
            return
        self.flush_pending_save()
        self._active_note_id = note_id
        self.store.settings.selected_note_id = note_id
        self.store.save_settings()
        self._editor.load_note(self.store.get(note_id))

    def _on_note_edited(self, title: str, content: str) -> None:
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None or note.trashed:
            return
        note.title = title
        note.content = content
        self._dirty = True
        self._save_timer.start()

    def _on_tags_edited(self, tags: list[str]) -> None:
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None or note.trashed:
            return
        note.tags = list(tags)
        self.store.upsert_note(note, touch=True)
        self._editor.set_saving_state(saved=True)
        self.refresh_ui()

    def flush_pending_save(self) -> None:
        """Persist any pending debounced edits immediately."""
        if self._save_timer.isActive():
            self._save_timer.stop()
        if not self._dirty or self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is not None and not note.trashed:
            self.store.upsert_note(note, touch=True)
            self._editor.set_saving_state(saved=True)
            self.refresh_ui(reload_editor=False)
        self._dirty = False

    def create_new_note(self) -> None:
        """Create a blank note (inheriting active tag filter if set) and focus title."""
        self.flush_pending_save()
        if self._current_view == "trash":
            self._current_view = "all"
        initial_tags = [self._current_tag] if self._current_tag else []
        pinned = self._current_view == "pinned"
        note = self.store.create_note(title="", content="", tags=initial_tags, pinned=pinned)
        self._active_note_id = note.id
        self.store.settings.selected_note_id = note.id
        self.store.save_settings()
        self.refresh_ui()
        if self._editor.mode == "preview":
            self._set_editor_mode("write")
        self._editor.focus_title()

    def _on_pin_toggled(self) -> None:
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None or note.trashed:
            return
        self.flush_pending_save()
        self.store.toggle_pin(note.id)
        self.refresh_ui()

    def _on_trash_note(self) -> None:
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None or note.trashed:
            return
        self.flush_pending_save()
        self.store.move_to_trash(note.id)
        self._active_note_id = None
        self.refresh_ui()

    def _on_restore_note(self) -> None:
        if self._active_note_id is None:
            return
        note = self.store.restore_from_trash(self._active_note_id)
        if note is not None:
            self._current_view = "all"
            self._current_tag = None
            self.refresh_ui()

    def _on_delete_forever(self) -> None:
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None:
            return
        dialog = ConfirmDialog(
            "Delete Note Forever",
            f"Permanently delete “{note.display_title}”? This cannot be undone.",
            "Delete Forever",
            self._palette,
            self,
        )
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec():
            self.store.delete_permanently(note.id)
            self._active_note_id = None
            self.refresh_ui()

    def _on_empty_trash(self) -> None:
        counts = self.store.counts_by_view()
        if counts.get("trash", 0) == 0:
            return
        dialog = ConfirmDialog(
            "Empty Trash",
            f"Permanently delete {counts['trash']} trashed note(s)? This cannot be undone.",
            "Empty Trash",
            self._palette,
            self,
        )
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec():
            self.store.empty_trash()
            self._active_note_id = None
            self.refresh_ui()

    def export_current_note(self) -> None:
        """Save the currently open note as a `.md` or `.txt` file."""
        self.flush_pending_save()
        if self._active_note_id is None:
            return
        note = self.store.get(self._active_note_id)
        if note is None:
            return
        suggested = f"{_safe_filename(note.display_title)}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Note",
            str(Path.home() / suggested),
            "Markdown Files (*.md);;Text Files (*.txt)",
        )
        if file_path:
            Path(file_path).write_text(note.to_markdown_document(), encoding="utf-8")

    def show_shortcuts(self) -> None:
        """Open the keyboard shortcuts modal."""
        dialog = ShortcutsDialog(self._palette, self)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def refresh_ui(
        self,
        refresh_sidebar: bool = True,
        reload_editor: bool = True,
    ) -> None:
        """Synchronize sidebar counts, filtered note list, and active editor pane."""
        if refresh_sidebar:
            self._sidebar.update_counts(
                self.store.counts_by_view(),
                self.store.all_tags_with_counts(),
            )
            self._sidebar.set_selection(self._current_view, self._current_tag)

        notes = self.store.filter_notes(
            view=self._current_view,
            tag=self._current_tag,
            query=self._search_query,
            sort_by=self.store.settings.sort_by,
        )

        visible_ids = {n.id for n in notes}
        if self._active_note_id not in visible_ids:
            self._active_note_id = notes[0].id if notes else None
            self.store.settings.selected_note_id = self._active_note_id
            self.store.save_settings()
            reload_editor = True

        if self._current_tag:
            header_title = f"#{self._current_tag}"
        elif self._current_view == "pinned":
            header_title = "Pinned"
        elif self._current_view == "trash":
            header_title = "Trash"
        else:
            header_title = "All Notes"

        if self._search_query.strip():
            empty_msg = "No notes match your search."
        elif self._current_view == "trash":
            empty_msg = "Trash is empty."
        elif self._current_view == "pinned":
            empty_msg = "Pin important notes to keep them here."
        else:
            empty_msg = "No notes yet.\nClick New Note to start writing."

        self._note_list.set_header(
            header_title,
            len(notes),
            is_trash=(self._current_view == "trash"),
            sort_by=self.store.settings.sort_by,
        )
        self._note_list.set_notes(notes, self._active_note_id, empty_message=empty_msg)

        if reload_editor:
            active_note = self.store.get(self._active_note_id) if self._active_note_id else None
            self._editor.load_note(active_note)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.flush_pending_save()
        self.store.save_settings()
        super().closeEvent(event)


def run() -> int:
    """Launch the Slate Notes desktop application."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Slate")
    app.setOrganizationName("SlateNotes")

    window = MainWindow()
    window.show()
    return app.exec()
