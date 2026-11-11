"""Custom monochrome grey dialogs for keyboard shortcuts and confirmations."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from slate.themes import ThemePalette


class ShortcutsDialog(QDialog):
    """Displays keyboard shortcuts inside a sleek monochrome grey card."""

    def __init__(self, palette: ThemePalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)
        self.setFixedWidth(410)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        card = QFrame(self)
        card.setObjectName("DialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(12)

        heading = QLabel("Keyboard Shortcuts", card)
        heading.setStyleSheet(
            f"color: {palette.text_primary}; font-size: 16px; font-weight: 700;"
        )
        card_layout.addWidget(heading)

        shortcuts = [
            ("New Note", "Cmd + N"),
            ("Search Notes", "Cmd + F"),
            ("Pin / Unpin Note", "Cmd + Shift + P"),
            ("Toggle Charcoal / Ash", "Cmd + Shift + T"),
            ("Write / Split / Preview", "Cmd + 1 / 2 / 3"),
            ("Zen Focus Mode", "Cmd + \\"),
            ("Export as Markdown", "Cmd + E"),
            ("Move to Trash", "Cmd + Backspace"),
        ]

        for action_label, keys in shortcuts:
            row = QHBoxLayout()
            row.setSpacing(10)
            name_lbl = QLabel(action_label, card)
            name_lbl.setStyleSheet(f"color: {palette.text_secondary}; font-size: 13px;")

            key_lbl = QLabel(keys, card)
            key_lbl.setStyleSheet(
                f"background-color: {palette.bg_pill}; color: {palette.text_primary}; "
                f"border: 1px solid {palette.border_subtle}; border-radius: 6px; "
                f"padding: 3px 8px; font-family: 'SF Mono', 'Menlo', monospace; font-size: 11px;"
            )
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row.addWidget(name_lbl, 1)
            row.addWidget(key_lbl)
            card_layout.addLayout(row)

        close_row = QHBoxLayout()
        close_row.addStretch(1)
        close_btn = QPushButton("Done", card)
        close_btn.setObjectName("DialogPrimaryBtn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        card_layout.addSpacing(4)
        card_layout.addLayout(close_row)

        root.addWidget(card)


class ConfirmDialog(QDialog):
    """Monochrome confirmation modal for irreversible actions."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_label: str,
        palette: ThemePalette,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(380)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        card = QFrame(self)
        card.setObjectName("DialogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        title_lbl = QLabel(title, card)
        title_lbl.setStyleSheet(
            f"color: {palette.text_primary}; font-size: 15px; font-weight: 700;"
        )

        msg_lbl = QLabel(message, card)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color: {palette.text_secondary}; font-size: 13px;")

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        cancel_btn = QPushButton("Cancel", card)
        cancel_btn.setObjectName("DialogSecondaryBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton(confirm_label, card)
        confirm_btn.setObjectName("DeleteForeverButton")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(msg_lbl)
        card_layout.addSpacing(6)
        card_layout.addLayout(btn_row)

        root.addWidget(card)
