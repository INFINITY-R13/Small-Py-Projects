"""Right editorial canvas: toolbar, title, tag chips, formatting bar, editor, and Markdown preview."""

from __future__ import annotations

import re

import markdown
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QTextCursor, QTextOption
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTextBrowser,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from slate.highlighter import MarkdownHighlighter
from slate.icons import render_svg_pixmap, svg_icon
from slate.models import Note, normalize_tag
from slate.themes import ThemePalette, build_markdown_css


_CHECKBOX_UNCHECKED_RE = re.compile(r"^(\s*[-*+]\s+)\[ \]\s+", re.MULTILINE)
_CHECKBOX_CHECKED_RE = re.compile(r"^(\s*[-*+]\s+)\[[xX]\]\s+", re.MULTILINE)


class TagChip(QFrame):
    """Compact monochrome pill chip representing a single note tag."""

    removed = Signal(str)

    def __init__(self, tag: str, read_only: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.tag = tag
        self.setObjectName("TagChip")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 2, 6, 2)
        layout.setSpacing(4)

        label = QLabel(f"#{tag}", self)
        label.setObjectName("TagChipLabel")
        layout.addWidget(label)

        if not read_only:
            remove_btn = QToolButton(self)
            remove_btn.setObjectName("TagChipRemove")
            remove_btn.setText("×")
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setToolTip(f"Remove #{tag}")
            remove_btn.clicked.connect(lambda: self.removed.emit(self.tag))
            layout.addWidget(remove_btn)


class EditorPane(QFrame):
    """Editorial workspace for viewing, writing, tagging, and previewing a note."""

    note_edited = Signal(str, str)  # title, content
    tags_edited = Signal(list)  # list[str]
    pin_toggled = Signal()
    trash_requested = Signal()
    restore_requested = Signal()
    delete_forever_requested = Signal()
    export_requested = Signal()
    mode_changed = Signal(str)  # write | split | preview
    zen_toggled = Signal()
    create_note_requested = Signal()

    def __init__(self, palette: ThemePalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("EditorPane")

        self._palette = palette
        self._current_note: Note | None = None
        self._mode = "write"
        self._zen_mode = False
        self._loading = False
        self._tag_widgets: list[QWidget] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget(self)
        root.addWidget(self._stack)

        # Page 0: Empty Canvas State
        self._stack.addWidget(self._build_empty_page())

        # Page 1: Active Note Canvas
        self._stack.addWidget(self._build_editor_page())

        self.apply_palette(palette)
        self.set_mode("write")
        self.load_note(None)

    def _build_empty_page(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        self._empty_logo = QLabel(page)
        self._empty_logo.setFixedSize(40, 40)
        self._empty_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Quiet Space Ready", page)
        title.setObjectName("EmptyCanvasTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Select a note from the list or start a fresh thought.", page)
        subtitle.setObjectName("EmptyCanvasSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        create_btn = QPushButton("Create Note", page)
        create_btn.setObjectName("EmptyCreateButton")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.create_note_requested.emit)

        layout.addWidget(self._empty_logo, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(4)
        layout.addWidget(create_btn, 0, Qt.AlignmentFlag.AlignCenter)
        return page

    def _build_editor_page(self) -> QWidget:
        page = QWidget(self)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Top Toolbar
        toolbar = QFrame(page)
        toolbar.setObjectName("EditorToolbar")
        toolbar.setFixedHeight(48)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 18, 0)
        tb_layout.setSpacing(10)

        self._status_label = QLabel("Saved", toolbar)
        self._status_label.setObjectName("StatusDotLabel")

        self._meta_label = QLabel("", toolbar)
        self._meta_label.setObjectName("StatusMetaLabel")

        tb_layout.addWidget(self._status_label)
        tb_layout.addWidget(self._meta_label)
        tb_layout.addStretch(1)

        # Segmented Mode Control
        seg_frame = QFrame(toolbar)
        seg_frame.setObjectName("SegmentedControl")
        seg_layout = QHBoxLayout(seg_frame)
        seg_layout.setContentsMargins(2, 2, 2, 2)
        seg_layout.setSpacing(2)

        self._mode_buttons: dict[str, QPushButton] = {}
        for mode_key, label in [("write", "Write"), ("split", "Split"), ("preview", "Preview")]:
            btn = QPushButton(label, seg_frame)
            btn.setProperty("segmentButton", "true")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _c=False, m=mode_key: self._on_mode_clicked(m))
            seg_layout.addWidget(btn)
            self._mode_buttons[mode_key] = btn

        tb_layout.addWidget(seg_frame)
        tb_layout.addSpacing(4)

        # Icon action buttons
        self._pin_btn = self._make_icon_btn(toolbar, "Pin note (Cmd+Shift+P)", self.pin_toggled.emit)
        self._zen_btn = self._make_icon_btn(toolbar, "Zen focus mode (Cmd+\\)", self.zen_toggled.emit)
        self._export_btn = self._make_icon_btn(toolbar, "Export Markdown (Cmd+E)", self.export_requested.emit)
        self._trash_btn = self._make_icon_btn(
            toolbar, "Move to Trash (Cmd+Backspace)", self.trash_requested.emit, danger=True
        )

        for btn in (self._pin_btn, self._zen_btn, self._export_btn, self._trash_btn):
            tb_layout.addWidget(btn)

        page_layout.addWidget(toolbar)

        # Editorial Column Wrapper (padding adjusts dynamically in Zen mode)
        self._canvas_wrap = QWidget(page)
        self._canvas_layout = QVBoxLayout(self._canvas_wrap)
        self._canvas_layout.setContentsMargins(40, 22, 40, 20)
        self._canvas_layout.setSpacing(10)

        # Trash Notice Banner
        self._trash_banner = QFrame(self._canvas_wrap)
        self._trash_banner.setObjectName("TrashBanner")
        banner_layout = QHBoxLayout(self._trash_banner)
        banner_layout.setContentsMargins(14, 9, 12, 9)
        banner_layout.setSpacing(8)

        banner_msg = QLabel("This note is in Trash. Restore it to edit.", self._trash_banner)
        banner_msg.setObjectName("TrashBannerLabel")
        restore_btn = QPushButton("Restore", self._trash_banner)
        restore_btn.setObjectName("RestoreButton")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self.restore_requested.emit)

        delete_btn = QPushButton("Delete Forever", self._trash_banner)
        delete_btn.setObjectName("DeleteForeverButton")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_forever_requested.emit)

        banner_layout.addWidget(banner_msg, 1)
        banner_layout.addWidget(restore_btn)
        banner_layout.addWidget(delete_btn)
        self._trash_banner.setVisible(False)
        self._canvas_layout.addWidget(self._trash_banner)

        # Title input
        self._title_input = QLineEdit(self._canvas_wrap)
        self._title_input.setObjectName("NoteTitleInput")
        self._title_input.setPlaceholderText("Untitled Note")
        self._title_input.textChanged.connect(self._on_content_changed)
        self._canvas_layout.addWidget(self._title_input)

        # Tag Chips + Add Tag row
        self._tags_row = QHBoxLayout()
        self._tags_row.setContentsMargins(0, 0, 0, 2)
        self._tags_row.setSpacing(6)

        self._add_tag_input = QLineEdit(self._canvas_wrap)
        self._add_tag_input.setObjectName("AddTagInput")
        self._add_tag_input.setPlaceholderText("+ tag")
        self._add_tag_input.setFixedWidth(92)
        self._add_tag_input.returnPressed.connect(self._commit_new_tag)
        self._add_tag_input.textChanged.connect(self._on_tag_typing)

        self._tags_row.addWidget(self._add_tag_input)
        self._tags_row.addStretch(1)
        self._canvas_layout.addLayout(self._tags_row)

        # Subtle Formatting Mini-Bar
        self._format_bar = QFrame(self._canvas_wrap)
        self._format_bar.setObjectName("FormatBar")
        fmt_layout = QHBoxLayout(self._format_bar)
        fmt_layout.setContentsMargins(0, 2, 0, 2)
        fmt_layout.setSpacing(4)

        format_actions = [
            ("H1", "Heading 1", lambda: self._prefix_line("# ")),
            ("H2", "Heading 2", lambda: self._prefix_line("## ")),
            ("B", "Bold", lambda: self._wrap_selection("**", "**", "bold")),
            ("I", "Italic", lambda: self._wrap_selection("*", "*", "italic")),
            ("` `", "Inline code", lambda: self._wrap_selection("`", "`", "code")),
            ("[ ]", "Checklist item", lambda: self._prefix_line("- [ ] ")),
            (">", "Blockquote", lambda: self._prefix_line("> ")),
            ("—", "Horizontal rule", lambda: self._insert_block("\n---\n")),
        ]
        for label, tip, handler in format_actions:
            btn = QPushButton(label, self._format_bar)
            btn.setProperty("formatBtn", "true")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tip)
            btn.clicked.connect(handler)
            fmt_layout.addWidget(btn)
        fmt_layout.addStretch(1)
        self._canvas_layout.addWidget(self._format_bar)

        # Hairline divider
        divider = QFrame(self._canvas_wrap)
        divider.setObjectName("CanvasDivider")
        self._canvas_layout.addWidget(divider)

        # Split Editor / Preview Area
        self._body_splitter = QSplitter(Qt.Orientation.Horizontal, self._canvas_wrap)
        self._body_splitter.setHandleWidth(1)

        self._editor = QPlainTextEdit(self._body_splitter)
        self._editor.setObjectName("NoteBodyEditor")
        self._editor.setPlaceholderText("Start writing in plain text or Markdown...")
        self._editor.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self._editor.setTabStopDistance(28.0)
        self._editor.viewport().setContentsMargins(0, 6, 0, 20)
        self._editor.textChanged.connect(self._on_content_changed)

        self._highlighter = MarkdownHighlighter(self._editor.document(), self._palette)

        self._preview = QTextBrowser(self._body_splitter)
        self._preview.setObjectName("MarkdownPreview")
        self._preview.setOpenExternalLinks(True)

        self._body_splitter.addWidget(self._editor)
        self._body_splitter.addWidget(self._preview)
        self._body_splitter.setSizes([500, 500])

        self._canvas_layout.addWidget(self._body_splitter, 1)
        page_layout.addWidget(self._canvas_wrap, 1)
        return page

    def _make_icon_btn(
        self,
        parent: QWidget,
        tooltip: str,
        callback,
        danger: bool = False,
    ) -> QToolButton:
        btn = QToolButton(parent)
        btn.setProperty("iconAction", "true")
        btn.setProperty("active", "false")
        btn.setProperty("danger", "true" if danger else "false")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(30, 30)
        btn.setIconSize(QSize(15, 15))
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        return btn

    def load_note(self, note: Note | None) -> None:
        """Load a note into the editorial canvas or show the empty state."""
        self._loading = True
        try:
            self._current_note = note
            if note is None:
                self._stack.setCurrentIndex(0)
                return

            self._stack.setCurrentIndex(1)
            self._title_input.setText(note.title)
            self._editor.setPlainText(note.content)

            is_trashed = note.trashed
            self._trash_banner.setVisible(is_trashed)
            self._title_input.setReadOnly(is_trashed)
            self._editor.setReadOnly(is_trashed)
            self._add_tag_input.setVisible(not is_trashed)
            self._format_bar.setVisible((not is_trashed) and self._mode != "preview")
            self._pin_btn.setVisible(not is_trashed)
            self._trash_btn.setVisible(not is_trashed)

            self._rebuild_tag_chips(note.tags, read_only=is_trashed)
            self._update_pin_visual(note.pinned)
            self._update_meta_labels(note, saved=True)
            self._refresh_preview()
        finally:
            self._loading = False

    def focus_title(self) -> None:
        """Place keyboard focus on the note title field."""
        if self._current_note is not None and not self._current_note.trashed:
            self._title_input.setFocus()
            self._title_input.selectAll()

    def set_saving_state(self, saved: bool) -> None:
        """Update toolbar saved indicator and metadata."""
        if self._current_note is not None:
            self._update_meta_labels(self._current_note, saved=saved)

    @property
    def mode(self) -> str:
        """Return the active editor mode ('write', 'split', or 'preview')."""
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Switch between 'write', 'split', and 'preview' viewing modes."""
        if mode not in {"write", "split", "preview"}:
            mode = "write"
        self._mode = mode

        for key, btn in self._mode_buttons.items():
            btn.setProperty("active", "true" if key == mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self._editor.setVisible(mode in {"write", "split"})
        self._preview.setVisible(mode in {"split", "preview"})
        if mode == "split":
            self._editor.viewport().setContentsMargins(0, 6, 16, 20)
            self._preview.viewport().setContentsMargins(18, 6, 4, 20)
        else:
            self._editor.viewport().setContentsMargins(0, 6, 0, 20)
            self._preview.viewport().setContentsMargins(0, 6, 0, 20)
        if self._current_note is not None:
            self._format_bar.setVisible((not self._current_note.trashed) and mode != "preview")
        if mode in {"split", "preview"}:
            self._refresh_preview()

    def set_zen_mode(self, enabled: bool) -> None:
        """Toggle expanded margins for distraction-free focus mode."""
        self._zen_mode = enabled
        self._zen_btn.setProperty("active", "true" if enabled else "false")
        self._zen_btn.style().unpolish(self._zen_btn)
        self._zen_btn.style().polish(self._zen_btn)

        if enabled:
            self._canvas_layout.setContentsMargins(120, 28, 120, 24)
        else:
            self._canvas_layout.setContentsMargins(40, 22, 40, 20)

    def _on_mode_clicked(self, mode: str) -> None:
        self.set_mode(mode)
        self.mode_changed.emit(mode)

    def _on_content_changed(self) -> None:
        if self._loading or self._current_note is None:
            return
        title = self._title_input.text()
        content = self._editor.toPlainText()
        self._current_note.title = title
        self._current_note.content = content
        self._update_meta_labels(self._current_note, saved=False)
        if self._mode in {"split", "preview"}:
            self._refresh_preview()
        self.note_edited.emit(title, content)

    def _on_tag_typing(self, text: str) -> None:
        if "," in text:
            self._commit_new_tag()

    def _commit_new_tag(self) -> None:
        if self._current_note is None or self._current_note.trashed:
            return
        raw = self._add_tag_input.text().replace(",", " ")
        self._add_tag_input.clear()

        updated = list(self._current_note.tags)
        changed = False
        for token in raw.split():
            tag = normalize_tag(token)
            if tag and tag not in updated:
                updated.append(tag)
                changed = True

        if changed:
            self._current_note.tags = updated
            self._rebuild_tag_chips(updated, read_only=False)
            self.tags_edited.emit(updated)

    def _remove_tag(self, tag: str) -> None:
        if self._current_note is None or self._current_note.trashed:
            return
        updated = [t for t in self._current_note.tags if t != tag]
        self._current_note.tags = updated
        self._rebuild_tag_chips(updated, read_only=False)
        self.tags_edited.emit(updated)

    def _rebuild_tag_chips(self, tags: list[str], read_only: bool) -> None:
        for widget in self._tag_widgets:
            self._tags_row.removeWidget(widget)
            widget.deleteLater()
        self._tag_widgets.clear()

        for index, tag in enumerate(tags):
            chip = TagChip(tag, read_only=read_only, parent=self._canvas_wrap)
            chip.removed.connect(self._remove_tag)
            self._tags_row.insertWidget(index, chip)
            self._tag_widgets.append(chip)

    def _update_meta_labels(self, note: Note, saved: bool) -> None:
        dot = "● Saved" if saved else "○ Editing…"
        self._status_label.setText(dot)
        words = note.word_count
        word_unit = "word" if words == 1 else "words"
        if words > 0:
            meta = f"  ·  {note.detailed_updated_label()}  ·  {words} {word_unit} · {note.reading_time_minutes} min read"
        else:
            meta = f"  ·  {note.detailed_updated_label()}"
        self._meta_label.setText(meta)

    def _update_pin_visual(self, pinned: bool) -> None:
        icon_name = "pin_filled" if pinned else "pin"
        color = self._palette.pin_color if pinned else self._palette.text_secondary
        self._pin_btn.setIcon(svg_icon(icon_name, color, size=15))
        self._pin_btn.setProperty("active", "true" if pinned else "false")
        self._pin_btn.style().unpolish(self._pin_btn)
        self._pin_btn.style().polish(self._pin_btn)
        self._pin_btn.setToolTip("Unpin note (Cmd+Shift+P)" if pinned else "Pin note (Cmd+Shift+P)")

    def _refresh_preview(self) -> None:
        if self._current_note is None:
            self._preview.setHtml("")
            return

        source = self._editor.toPlainText()
        # Render markdown checklists neatly as visual checkbox characters
        source = _CHECKBOX_UNCHECKED_RE.sub(r"\1☐ ", source)
        source = _CHECKBOX_CHECKED_RE.sub(r"\1☑ ", source)

        rendered_body = markdown.markdown(
            source,
            extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
        )
        if not rendered_body.strip():
            rendered_body = (
                f'<p style="color: {self._palette.text_muted};">Nothing to preview yet.</p>'
            )

        css = build_markdown_css(self._palette)
        doc_html = f"<!DOCTYPE html><html><head><style>{css}</style></head><body>{rendered_body}</body></html>"
        self._preview.setHtml(doc_html)

    def _wrap_selection(self, prefix: str, suffix: str, placeholder: str) -> None:
        if self._editor.isReadOnly():
            return
        cursor = self._editor.textCursor()
        selected = cursor.selectedText()
        if selected:
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            start = cursor.position()
            cursor.insertText(f"{prefix}{placeholder}{suffix}")
            cursor.setPosition(start + len(prefix))
            cursor.setPosition(start + len(prefix) + len(placeholder), QTextCursor.MoveMode.KeepAnchor)
            self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    def _prefix_line(self, prefix: str) -> None:
        if self._editor.isReadOnly():
            return
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText(prefix)
        self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    def _insert_block(self, text: str) -> None:
        if self._editor.isReadOnly():
            return
        cursor = self._editor.textCursor()
        cursor.insertText(text)
        self._editor.setFocus()

    def apply_palette(self, palette: ThemePalette) -> None:
        """Update icons, syntax highlighter, and Markdown preview CSS for active palette."""
        self._palette = palette
        self._empty_logo.setPixmap(render_svg_pixmap("slate_logo", palette.text_muted, size=36))
        self._zen_btn.setIcon(svg_icon("focus", palette.text_secondary, size=15))
        self._export_btn.setIcon(svg_icon("export", palette.text_secondary, size=15))
        self._trash_btn.setIcon(svg_icon("trash", palette.text_secondary, size=15))

        was_loading = self._loading
        self._loading = True
        try:
            self._highlighter.set_palette(palette)
        finally:
            self._loading = was_loading

        pinned = bool(self._current_note and self._current_note.pinned)
        self._update_pin_visual(pinned)
        self._refresh_preview()
