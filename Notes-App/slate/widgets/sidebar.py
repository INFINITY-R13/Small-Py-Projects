"""Left navigation rail widget: smart views, tag filter list, and theme controls."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from slate.icons import render_svg_pixmap, svg_icon
from slate.themes import ThemePalette


class NavRowButton(QPushButton):
    """Sidebar navigation item with left icon, text label, and right-aligned count badge."""

    def __init__(self, icon_name: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.icon_name = icon_name
        self._active = False
        self.setProperty("navItem", "true")
        self.setProperty("active", "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(15, 15)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._text_label = QLabel(label, self)
        self._text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._count_label = QLabel("", self)
        self._count_label.setProperty("countBadge", "true")
        self._count_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label, 1)
        layout.addWidget(self._count_label)

    def set_count(self, count: int) -> None:
        """Update the right-aligned count badge."""
        self._count_label.setText(str(count) if count > 0 else "")

    def set_active(self, active: bool) -> None:
        """Toggle active highlight state and refresh styling."""
        self._active = active
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def apply_palette(self, palette: ThemePalette) -> None:
        """Retint icon and label colors to match the active grey palette."""
        icon_color = palette.text_primary if self._active else palette.text_secondary
        self._icon_label.setPixmap(render_svg_pixmap(self.icon_name, icon_color, size=15))
        text_color = palette.text_primary if self._active else palette.text_secondary
        weight = "600" if self._active else "500"
        self._text_label.setStyleSheet(
            f"color: {text_color}; font-size: 13px; font-weight: {weight}; background: transparent;"
        )


class SidebarPane(QFrame):
    """Left navigation rail containing views, dynamic tag filters, and theme toggle."""

    new_note_requested = Signal()
    view_selected = Signal(str)
    tag_selected = Signal(object)  # str | None
    theme_toggle_requested = Signal()
    help_requested = Signal()

    def __init__(self, palette: ThemePalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SidebarPane")
        self.setMinimumWidth(185)
        self.setMaximumWidth(250)

        self._palette = palette
        self._current_view = "all"
        self._current_tag: str | None = None
        self._tag_buttons: dict[str, NavRowButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 16, 12, 14)
        root.setSpacing(12)

        # Brand mark header
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(4, 0, 4, 2)
        brand_row.setSpacing(8)
        self._brand_icon = QLabel(self)
        self._brand_icon.setFixedSize(18, 18)
        brand_title = QLabel("SLATE", self)
        brand_title.setObjectName("BrandTitle")
        brand_row.addWidget(self._brand_icon)
        brand_row.addWidget(brand_title)
        brand_row.addStretch(1)
        root.addLayout(brand_row)

        # Primary CTA button
        self._new_btn = QPushButton(" New Note", self)
        self._new_btn.setObjectName("NewNoteButton")
        self._new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_btn.setIconSize(QSize(14, 14))
        self._new_btn.setToolTip("Create a new note (Cmd+N)")
        self._new_btn.clicked.connect(self.new_note_requested.emit)
        root.addWidget(self._new_btn)

        # Smart views
        views_layout = QVBoxLayout()
        views_layout.setContentsMargins(0, 4, 0, 0)
        views_layout.setSpacing(2)

        self._view_buttons: dict[str, NavRowButton] = {
            "all": NavRowButton("notes", "All Notes", self),
            "pinned": NavRowButton("pin", "Pinned", self),
            "trash": NavRowButton("trash", "Trash", self),
        }
        for view_key, btn in self._view_buttons.items():
            btn.clicked.connect(lambda _checked=False, k=view_key: self._on_view_clicked(k))
            views_layout.addWidget(btn)

        root.addLayout(views_layout)

        # Tags header
        tags_header = QLabel("TAGS", self)
        tags_header.setObjectName("SidebarSectionLabel")
        root.addWidget(tags_header)

        # Scrollable tags list
        self._tags_scroll = QScrollArea(self)
        self._tags_scroll.setObjectName("TagsScroll")
        self._tags_scroll.setWidgetResizable(True)
        self._tags_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._tags_container = QWidget(self._tags_scroll)
        self._tags_container.setObjectName("TagsContainer")
        self._tags_layout = QVBoxLayout(self._tags_container)
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(2)
        self._tags_layout.addStretch(1)

        self._empty_tags_label = QLabel("No tags yet", self._tags_container)
        self._empty_tags_label.setStyleSheet("font-size: 12px; padding: 4px 10px;")
        self._tags_layout.insertWidget(0, self._empty_tags_label)

        self._tags_scroll.setWidget(self._tags_container)
        root.addWidget(self._tags_scroll, 1)

        # Bottom utility dock
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 4, 0, 0)
        bottom_row.setSpacing(6)

        self._theme_btn = QPushButton(self)
        self._theme_btn.setObjectName("ThemeToggleButton")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.setIconSize(QSize(14, 14))
        self._theme_btn.clicked.connect(self.theme_toggle_requested.emit)

        self._help_btn = QPushButton(self)
        self._help_btn.setObjectName("HelpButton")
        self._help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._help_btn.setFixedWidth(34)
        self._help_btn.setIconSize(QSize(14, 14))
        self._help_btn.setToolTip("Keyboard shortcuts")
        self._help_btn.clicked.connect(self.help_requested.emit)

        bottom_row.addWidget(self._theme_btn, 1)
        bottom_row.addWidget(self._help_btn)
        root.addLayout(bottom_row)

        self.apply_palette(palette)
        self.set_selection(self._current_view, self._current_tag)

    def _on_view_clicked(self, view_key: str) -> None:
        self._current_view = view_key
        self._current_tag = None
        self._refresh_active_states()
        self.view_selected.emit(view_key)
        self.tag_selected.emit(None)

    def _on_tag_clicked(self, tag: str) -> None:
        if self._current_tag == tag and self._current_view == "all":
            self._current_tag = None
        else:
            self._current_view = "all"
            self._current_tag = tag
        self._refresh_active_states()
        self.view_selected.emit(self._current_view)
        self.tag_selected.emit(self._current_tag)

    def set_selection(self, view: str, tag: str | None) -> None:
        """Programmatically synchronize active sidebar selection."""
        self._current_view = view
        self._current_tag = tag
        self._refresh_active_states()

    def _refresh_active_states(self) -> None:
        for key, btn in self._view_buttons.items():
            is_active = self._current_tag is None and self._current_view == key
            btn.set_active(is_active)
            btn.apply_palette(self._palette)

        for tag_name, btn in self._tag_buttons.items():
            is_active = self._current_tag == tag_name
            btn.set_active(is_active)
            btn.apply_palette(self._palette)

    def update_counts(self, counts: dict[str, int], tags: list[tuple[str, int]]) -> None:
        """Refresh smart view counts and rebuild the dynamic tag filter list."""
        for key, btn in self._view_buttons.items():
            btn.set_count(counts.get(key, 0))

        # Rebuild tag buttons cleanly
        for btn in self._tag_buttons.values():
            self._tags_layout.removeWidget(btn)
            btn.deleteLater()
        self._tag_buttons.clear()

        self._empty_tags_label.setVisible(len(tags) == 0)

        for index, (tag_name, count) in enumerate(tags):
            btn = NavRowButton("tag", tag_name, self._tags_container)
            btn.set_count(count)
            btn.clicked.connect(lambda _checked=False, t=tag_name: self._on_tag_clicked(t))
            self._tags_layout.insertWidget(index, btn)
            self._tag_buttons[tag_name] = btn

        self._refresh_active_states()

    def apply_palette(self, palette: ThemePalette) -> None:
        """Apply monochrome grey icons and surface contrast for the active palette."""
        self._palette = palette
        self._brand_icon.setPixmap(render_svg_pixmap("slate_logo", palette.text_primary, size=18))
        self._new_btn.setIcon(svg_icon("plus", palette.accent_text, size=14))
        self._empty_tags_label.setStyleSheet(
            f"color: {palette.text_muted}; font-size: 12px; padding: 4px 10px; background: transparent;"
        )

        if palette.is_dark:
            self._theme_btn.setIcon(svg_icon("moon", palette.text_secondary, size=14))
            self._theme_btn.setText(" Charcoal")
            self._theme_btn.setToolTip("Switch to Ash (Light Grey) — Cmd+Shift+T")
        else:
            self._theme_btn.setIcon(svg_icon("sun", palette.text_secondary, size=14))
            self._theme_btn.setText(" Ash Grey")
            self._theme_btn.setToolTip("Switch to Charcoal (Dark Grey) — Cmd+Shift+T")

        self._help_btn.setIcon(svg_icon("help", palette.text_secondary, size=14))
        self._refresh_active_states()
