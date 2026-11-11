"""Middle pane: search capsule, view header, and custom-painted grey note cards."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QModelIndex, QObject, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel

from slate.icons import render_svg_pixmap, svg_icon
from slate.models import Note
from slate.themes import ThemePalette


NOTE_ROLE = Qt.ItemDataRole.UserRole + 1


class NoteCardDelegate(QStyledItemDelegate):
    """Paints each note list entry as a rounded, high-DPI monochrome card."""

    def __init__(self, palette: ThemePalette, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._palette = palette

    def set_palette(self, palette: ThemePalette) -> None:
        """Update palette colors used when painting cards."""
        self._palette = palette

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        note: Note | None = index.data(NOTE_ROLE)
        has_tags = bool(note and note.tags)
        return QSize(option.rect.width(), 98 if has_tags else 80)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        note: Note | None = index.data(NOTE_ROLE)
        if note is None:
            return

        p = self._palette
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        is_hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        card_rect = option.rect.adjusted(2, 3, -2, -3)

        # Card background & border
        if is_selected:
            painter.setBrush(QColor(p.bg_card_selected))
            painter.setPen(QPen(QColor(p.border_strong), 1.0))
        elif is_hovered:
            painter.setBrush(QColor(p.bg_surface_hover))
            painter.setPen(QPen(QColor(p.border_subtle), 1.0))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRoundedRect(card_rect, 10.0, 10.0)

        # Subtle monochrome active bar on selected card
        if is_selected:
            bar_rect = QRect(card_rect.left() + 5, card_rect.top() + 16, 3, card_rect.height() - 32)
            painter.setBrush(QColor(p.accent))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(bar_rect, 1.5, 1.5)

        content_rect = card_rect.adjusted(16, 10, -12, -10)

        # Top row: timestamp + pin indicator on right, title on left
        meta_font = QFont("SF Pro Text", 11)
        meta_font.setWeight(QFont.Weight.Medium)
        meta_metrics = QFontMetrics(meta_font)
        time_text = note.relative_updated_label()
        time_width = meta_metrics.horizontalAdvance(time_text)

        pin_space = 18 if note.pinned else 0
        right_reserved = time_width + pin_space + 8

        title_rect = QRect(
            content_rect.left(),
            content_rect.top(),
            max(40, content_rect.width() - right_reserved),
            20,
        )
        title_font = QFont("SF Pro Text", 13)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_metrics = QFontMetrics(title_font)
        elided_title = title_metrics.elidedText(
            note.display_title, Qt.TextElideMode.ElideRight, title_rect.width()
        )

        painter.setFont(title_font)
        painter.setPen(QColor(p.text_primary if note.title.strip() else p.text_secondary))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_title)

        # Draw pin icon + timestamp
        if note.pinned:
            pin_pm = render_svg_pixmap("pin_filled", p.pin_color, size=12)
            pin_x = content_rect.right() - time_width - 16
            pin_y = content_rect.top() + 4
            painter.drawPixmap(pin_x, pin_y, pin_pm)

        time_rect = QRect(content_rect.right() - time_width, content_rect.top(), time_width, 20)
        painter.setFont(meta_font)
        painter.setPen(QColor(p.text_muted))
        painter.drawText(time_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, time_text)

        # Middle row: clean excerpt
        excerpt_font = QFont("SF Pro Text", 12)
        excerpt_top = content_rect.top() + 24
        excerpt_height = 32 if not note.tags else 22
        excerpt_rect = QRect(content_rect.left(), excerpt_top, content_rect.width(), excerpt_height)

        excerpt_metrics = QFontMetrics(excerpt_font)
        excerpt_text = excerpt_metrics.elidedText(
            note.excerpt(110), Qt.TextElideMode.ElideRight, excerpt_rect.width()
        )
        painter.setFont(excerpt_font)
        painter.setPen(QColor(p.text_secondary))
        painter.drawText(excerpt_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, excerpt_text)

        # Bottom row: tag chips
        if note.tags:
            tag_font = QFont("SF Pro Text", 10)
            tag_font.setWeight(QFont.Weight.Medium)
            tag_metrics = QFontMetrics(tag_font)
            painter.setFont(tag_font)

            x_cursor = content_rect.left()
            y_chip = content_rect.bottom() - 18
            max_x = content_rect.right()

            visible_tags = note.tags[:3]
            overflow = len(note.tags) - len(visible_tags)
            labels = [f"#{t}" for t in visible_tags]
            if overflow > 0:
                labels.append(f"+{overflow}")

            for label in labels:
                pill_w = tag_metrics.horizontalAdvance(label) + 12
                if x_cursor + pill_w > max_x:
                    break
                pill_rect = QRect(x_cursor, y_chip, pill_w, 18)
                painter.setBrush(QColor(p.bg_pill))
                painter.setPen(QPen(QColor(p.border_subtle), 1.0))
                painter.drawRoundedRect(pill_rect, 9.0, 9.0)
                painter.setPen(QColor(p.text_secondary))
                painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, label)
                x_cursor += pill_w + 5

        # Subtle bottom hairline between unselected cards
        if not is_selected and not is_hovered:
            painter.setPen(QPen(QColor(p.border_subtle), 1.0))
            line_y = option.rect.bottom()
            painter.drawLine(card_rect.left() + 12, line_y, card_rect.right() - 12, line_y)

        painter.restore()


class NoteListPane(QFrame):
    """Middle column holding search bar, filter header, and note cards list."""

    note_selected = Signal(str)
    search_changed = Signal(str)
    sort_toggled = Signal()
    empty_trash_requested = Signal()

    def __init__(self, palette: ThemePalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("NoteListPane")
        self.setMinimumWidth(240)
        self.setMaximumWidth(360)

        self._palette = palette
        self._suppress_selection = False

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 14, 12, 10)
        root.setSpacing(10)

        # Capsule Search Input
        self._search_frame = QFrame(self)
        self._search_frame.setObjectName("SearchFrame")
        self._search_frame.setProperty("focused", "false")
        search_layout = QHBoxLayout(self._search_frame)
        search_layout.setContentsMargins(10, 2, 6, 2)
        search_layout.setSpacing(6)

        self._search_icon = QLabel(self._search_frame)
        self._search_icon.setFixedSize(14, 14)

        self._search_input = QLineEdit(self._search_frame)
        self._search_input.setObjectName("SearchInput")
        self._search_input.setPlaceholderText("Search notes or #tags...")
        self._search_input.installEventFilter(self)
        self._search_input.textChanged.connect(self._on_search_text_changed)

        self._clear_btn = QToolButton(self._search_frame)
        self._clear_btn.setObjectName("ClearSearchButton")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setFixedSize(20, 20)
        self._clear_btn.setIconSize(QSize(12, 12))
        self._clear_btn.setVisible(False)
        self._clear_btn.setToolTip("Clear search")
        self._clear_btn.clicked.connect(self._search_input.clear)

        search_layout.addWidget(self._search_icon)
        search_layout.addWidget(self._search_input, 1)
        search_layout.addWidget(self._clear_btn)
        root.addWidget(self._search_frame)

        # Header strip: view label + sort/trash actions
        header_row = QHBoxLayout()
        header_row.setContentsMargins(4, 0, 2, 0)
        header_row.setSpacing(6)

        self._header_label = QLabel("All Notes", self)
        self._header_label.setObjectName("PaneHeaderTitle")

        self._sort_btn = QPushButton(" Updated", self)
        self._sort_btn.setObjectName("SortButton")
        self._sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sort_btn.setIconSize(QSize(12, 12))
        self._sort_btn.setToolTip("Toggle sort order (Updated / Title)")
        self._sort_btn.clicked.connect(self.sort_toggled.emit)

        self._empty_trash_btn = QPushButton("Empty Trash", self)
        self._empty_trash_btn.setObjectName("EmptyTrashButton")
        self._empty_trash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._empty_trash_btn.setVisible(False)
        self._empty_trash_btn.clicked.connect(self.empty_trash_requested.emit)

        header_row.addWidget(self._header_label, 1)
        header_row.addWidget(self._empty_trash_btn)
        header_row.addWidget(self._sort_btn)
        root.addLayout(header_row)

        # Notes List View
        self._model = QStandardItemModel(self)
        self._delegate = NoteCardDelegate(palette, self)

        self._list_view = QListView(self)
        self._list_view.setObjectName("NotesListView")
        self._list_view.setModel(self._model)
        self._list_view.setItemDelegate(self._delegate)
        self._list_view.setMouseTracking(True)
        self._list_view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self._list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self._list_view.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self._empty_label = QLabel("No notes yet", self)
        self._empty_label.setObjectName("ListEmptyStateLabel")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.setVisible(False)
        self._empty_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root.addWidget(self._list_view, 1)
        root.addWidget(self._empty_label, 1)

        self.apply_palette(palette)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._search_input:
            if event.type() == QEvent.Type.FocusIn:
                self._search_frame.setProperty("focused", "true")
                self._search_frame.style().unpolish(self._search_frame)
                self._search_frame.style().polish(self._search_frame)
            elif event.type() == QEvent.Type.FocusOut:
                self._search_frame.setProperty("focused", "false")
                self._search_frame.style().unpolish(self._search_frame)
                self._search_frame.style().polish(self._search_frame)
        return super().eventFilter(watched, event)

    def _on_search_text_changed(self, text: str) -> None:
        self._clear_btn.setVisible(bool(text))
        self.search_changed.emit(text)

    def _on_selection_changed(self) -> None:
        if self._suppress_selection:
            return
        indexes = self._list_view.selectedIndexes()
        if not indexes:
            return
        note: Note | None = indexes[0].data(NOTE_ROLE)
        if note is not None:
            self.note_selected.emit(note.id)

    def focus_search(self) -> None:
        """Focus and select the search input field."""
        self._search_input.setFocus()
        self._search_input.selectAll()

    def set_header(self, title: str, count: int, is_trash: bool, sort_by: str) -> None:
        """Update the list header text, sort button label, and Empty Trash visibility."""
        self._header_label.setText(f"{title}  ·  {count}")
        self._sort_btn.setText(" Updated" if sort_by == "updated" else " Title")
        self._sort_btn.setVisible(not is_trash)
        self._empty_trash_btn.setVisible(is_trash and count > 0)

    def set_notes(
        self,
        notes: list[Note],
        selected_note_id: str | None,
        empty_message: str = "No notes found",
    ) -> None:
        """Populate the list view with filtered notes and keep selection synced."""
        self._suppress_selection = True
        try:
            self._model.clear()
            selected_row = -1
            for row, note in enumerate(notes):
                item = QStandardItem()
                item.setData(note, NOTE_ROLE)
                item.setEditable(False)
                self._model.appendRow(item)
                if note.id == selected_note_id:
                    selected_row = row

            has_items = len(notes) > 0
            self._list_view.setVisible(has_items)
            self._empty_label.setVisible(not has_items)
            self._empty_label.setText(empty_message)

            if selected_row >= 0:
                idx = self._model.index(selected_row, 0)
                self._list_view.setCurrentIndex(idx)
        finally:
            self._suppress_selection = False

    def apply_palette(self, palette: ThemePalette) -> None:
        """Retint search icons, sort icon, and note card delegate."""
        self._palette = palette
        self._search_icon.setPixmap(render_svg_pixmap("search", palette.text_muted, size=14))
        self._clear_btn.setIcon(svg_icon("close", palette.text_muted, size=12))
        self._sort_btn.setIcon(svg_icon("sort", palette.text_muted, size=12))
        self._delegate.set_palette(palette)
        self._list_view.viewport().update()
