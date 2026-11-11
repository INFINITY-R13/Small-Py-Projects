"""Unit and offscreen UI smoke tests for Slate Notes."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from slate.app import MainWindow
from slate.models import Note, normalize_tags
from slate.storage import NoteStore


class NoteModelTests(unittest.TestCase):
    """Verify Note text utilities, tags normalization, and query matching."""

    def test_tags_normalization_deduplicates_and_cleans(self) -> None:
        tags = normalize_tags(["#Design", "design", "  My Tag ", "", "#"])
        self.assertEqual(tags, ["design", "my-tag"])

    def test_excerpt_strips_markdown_markers(self) -> None:
        note = Note(
            title="Specs",
            content="# Header\n\n- [ ] **First** `task` item\n> Quote line",
        )
        excerpt = note.excerpt()
        self.assertNotIn("#", excerpt)
        self.assertNotIn("**", excerpt)
        self.assertIn("Header", excerpt)
        self.assertIn("First task item", excerpt)

    def test_matches_query_supports_text_and_hashtags(self) -> None:
        note = Note(
            title="Grey Theme Spec",
            content="Matte charcoal surfaces and typography.",
            tags=["design", "ui"],
        )
        self.assertTrue(note.matches_query("charcoal"))
        self.assertTrue(note.matches_query("#design grey"))
        self.assertFalse(note.matches_query("#backend"))
        self.assertFalse(note.matches_query("charcoal missingword"))

    def test_markdown_export_includes_title_tags_and_body(self) -> None:
        note = Note(title="Draft", content="Hello world.", tags=["ideas", "drafts"])
        doc = note.to_markdown_document()
        self.assertIn("# Draft", doc)
        self.assertIn("*#ideas #drafts*", doc)
        self.assertTrue(doc.endswith("Hello world.\n"))


class NoteStoreTests(unittest.TestCase):
    """Verify JSON persistence, trash lifecycle, filtering, and settings."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._tmp.name)
        self.store = NoteStore(self.data_dir)
        self.store.load()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_first_launch_seeds_welcome_notes_once(self) -> None:
        counts = self.store.counts_by_view()
        self.assertGreaterEqual(counts["all"], 4)
        self.assertEqual(counts["pinned"], 1)
        self.assertEqual(counts["trash"], 0)

    def test_create_pin_trash_restore_and_delete(self) -> None:
        created = self.store.create_note(
            title="Test Note",
            content="Body content here",
            tags=["testing"],
        )
        self.assertIsNotNone(self.store.get(created.id))

        self.store.toggle_pin(created.id)
        self.assertTrue(self.store.get(created.id).pinned)

        # Trashing also unpins the note
        self.store.move_to_trash(created.id)
        trashed = self.store.get(created.id)
        self.assertTrue(trashed.trashed)
        self.assertFalse(trashed.pinned)

        # Reload from disk to verify persistence
        reloaded = NoteStore(self.data_dir)
        reloaded.load()
        self.assertTrue(reloaded.get(created.id).trashed)

        reloaded.restore_from_trash(created.id)
        self.assertFalse(reloaded.get(created.id).trashed)

        reloaded.move_to_trash(created.id)
        removed = reloaded.empty_trash()
        self.assertEqual(removed, 1)
        self.assertIsNone(reloaded.get(created.id))

    def test_filter_notes_by_view_tag_and_sort(self) -> None:
        a = self.store.create_note(title="Alpha", tags=["focus"])
        z = self.store.create_note(title="Zeta", tags=["focus"], pinned=True)

        results = self.store.filter_notes(view="all", tag="focus", sort_by="title")
        self.assertEqual([n.id for n in results], [z.id, a.id])  # pinned first


class MainWindowSmokeTests(unittest.TestCase):
    """Offscreen Qt smoke tests for MainWindow interactions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_window_theme_modes_and_note_editing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = NoteStore(Path(tmp))
            window = MainWindow(store=store)

            self.assertEqual(window.store.settings.theme, "charcoal")
            window.toggle_theme()
            self.assertEqual(window.store.settings.theme, "ash")
            self.assertFalse(window._dirty)
            self.assertEqual(window._editor._status_label.text(), "● Saved")

            window.create_new_note()
            window._editor._title_input.setText("Offscreen Verification")
            window._editor._editor.setPlainText("# Heading\n\n- [x] Tested cleanly")
            window.flush_pending_save()

            window._set_editor_mode("split")
            self.assertEqual(window.store.settings.editor_mode, "split")
            window._set_editor_mode("preview")
            self.assertIn("Heading", window._editor._preview.toPlainText())

            window.toggle_zen_mode()
            self.assertTrue(window.store.settings.zen_mode)
            window.toggle_zen_mode()
            self.assertFalse(window.store.settings.zen_mode)

            # Verify note saved on disk
            reloaded = NoteStore(Path(tmp))
            reloaded.load()
            titles = [n.title for n in reloaded.all_notes()]
            self.assertIn("Offscreen Verification", titles)
            self.assertEqual(reloaded.settings.theme, "ash")

            window.close()


if __name__ == "__main__":
    unittest.main()
