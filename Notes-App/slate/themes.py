"""Monochrome grey design tokens, Qt stylesheets (QSS), and Markdown preview CSS."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    """Color and surface tokens for a monochrome grey theme."""

    name: str
    label: str
    is_dark: bool

    # Surface hierarchy
    bg_sidebar: str
    bg_list: str
    bg_editor: str
    bg_surface: str
    bg_surface_hover: str
    bg_card_selected: str
    bg_pill: str
    bg_pill_active: str
    bg_code: str

    # Borders & dividers
    border_subtle: str
    border_strong: str
    border_focus: str

    # Typography
    text_primary: str
    text_secondary: str
    text_muted: str

    # Interactive monochrome accents
    accent: str
    accent_hover: str
    accent_text: str
    selection_bg: str
    selection_text: str

    # Semantic muted tones (harmonized with grey)
    pin_color: str
    danger: str
    danger_bg: str
    scrollbar_thumb: str
    scrollbar_thumb_hover: str


CHARCOAL_PALETTE = ThemePalette(
    name="charcoal",
    label="Charcoal",
    is_dark=True,
    bg_sidebar="#161719",
    bg_list="#1B1D20",
    bg_editor="#202226",
    bg_surface="#26292E",
    bg_surface_hover="#2C3036",
    bg_card_selected="#2D3138",
    bg_pill="#2B2E34",
    bg_pill_active="#3C4048",
    bg_code="#181A1D",
    border_subtle="#2A2D33",
    border_strong="#373B43",
    border_focus="#626874",
    text_primary="#E6E8EC",
    text_secondary="#A2A8B3",
    text_muted="#6E7480",
    accent="#D0D4DC",
    accent_hover="#E3E6EC",
    accent_text="#161719",
    selection_bg="#3E444E",
    selection_text="#F0F2F5",
    pin_color="#C2C7D0",
    danger="#C59B9B",
    danger_bg="#352A2C",
    scrollbar_thumb="#353941",
    scrollbar_thumb_hover="#4B505B",
)

ASH_PALETTE = ThemePalette(
    name="ash",
    label="Ash",
    is_dark=False,
    bg_sidebar="#E4E6EA",
    bg_list="#ECEEF1",
    bg_editor="#F4F5F7",
    bg_surface="#E7E9ED",
    bg_surface_hover="#DFE2E7",
    bg_card_selected="#DCDFE6",
    bg_pill="#E1E3E8",
    bg_pill_active="#CFD4DC",
    bg_code="#E8EAEE",
    border_subtle="#D6D9E0",
    border_strong="#C3C7D0",
    border_focus="#7F8694",
    text_primary="#212429",
    text_secondary="#585E69",
    text_muted="#878D99",
    accent="#373B43",
    accent_hover="#25282E",
    accent_text="#F4F5F7",
    selection_bg="#CED3DC",
    selection_text="#1A1C20",
    pin_color="#494E58",
    danger="#8F5E5E",
    danger_bg="#EADEDE",
    scrollbar_thumb="#C8CCD4",
    scrollbar_thumb_hover="#A6ACB7",
)

PALETTES: dict[str, ThemePalette] = {
    "charcoal": CHARCOAL_PALETTE,
    "ash": ASH_PALETTE,
}


def get_palette(name: str) -> ThemePalette:
    """Return the requested monochrome grey palette, defaulting to Charcoal."""
    return PALETTES.get(name, CHARCOAL_PALETTE)


def build_stylesheet(p: ThemePalette) -> str:
    """Generate the complete Qt stylesheet (QSS) for the active grey palette."""
    return f"""
    QMainWindow, QDialog {{
        background-color: {p.bg_editor};
        color: {p.text_primary};
        font-family: "SF Pro Text", "Helvetica Neue", "Segoe UI", sans-serif;
    }}

    QWidget {{
        color: {p.text_primary};
        outline: none;
    }}

    QTooltip, QToolTip {{
        background-color: {p.bg_surface};
        color: {p.text_primary};
        border: 1px solid {p.border_strong};
        border-radius: 6px;
        padding: 5px 9px;
        font-size: 11px;
    }}

    /* Splitter hairline dividers */
    QSplitter::handle {{
        background-color: {p.border_subtle};
    }}
    QSplitter::handle:hover {{
        background-color: {p.border_focus};
    }}

    /* Minimal slim scrollbars */
    QScrollBar:vertical {{
        background: transparent;
        width: 7px;
        margin: 4px 2px 4px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.scrollbar_thumb};
        border-radius: 3px;
        min-height: 28px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p.scrollbar_thumb_hover};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 7px;
        margin: 0px 4px 2px 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p.scrollbar_thumb};
        border-radius: 3px;
        min-width: 28px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {p.scrollbar_thumb_hover};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
        width: 0px;
    }}

    /* Left Sidebar Rail */
    #SidebarPane {{
        background-color: {p.bg_sidebar};
    }}
    #BrandTitle {{
        color: {p.text_primary};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2.4px;
    }}
    #SidebarSectionLabel {{
        color: {p.text_muted};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.3px;
        padding: 4px 10px;
    }}
    QPushButton#NewNoteButton {{
        background-color: {p.accent};
        color: {p.accent_text};
        border: none;
        border-radius: 9px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
    }}
    QPushButton#NewNoteButton:hover {{
        background-color: {p.accent_hover};
    }}

    QPushButton[navItem="true"] {{
        background-color: transparent;
        color: {p.text_secondary};
        border: none;
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 13px;
        font-weight: 500;
        text-align: left;
    }}
    QPushButton[navItem="true"]:hover {{
        background-color: {p.bg_surface};
        color: {p.text_primary};
    }}
    QPushButton[navItem="true"][active="true"] {{
        background-color: {p.bg_card_selected};
        color: {p.text_primary};
        font-weight: 600;
    }}

    QLabel[countBadge="true"] {{
        color: {p.text_muted};
        font-size: 11px;
        font-weight: 600;
        background: transparent;
    }}

    QScrollArea#TagsScroll {{
        background: transparent;
        border: none;
    }}
    QWidget#TagsContainer {{
        background: transparent;
    }}

    QPushButton#ThemeToggleButton, QPushButton#HelpButton {{
        background-color: {p.bg_pill};
        color: {p.text_secondary};
        border: 1px solid {p.border_subtle};
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton#ThemeToggleButton:hover, QPushButton#HelpButton:hover {{
        background-color: {p.bg_pill_active};
        color: {p.text_primary};
        border-color: {p.border_strong};
    }}

    /* Middle Note List Pane */
    #NoteListPane {{
        background-color: {p.bg_list};
    }}
    #SearchFrame {{
        background-color: {p.bg_surface};
        border: 1px solid {p.border_subtle};
        border-radius: 10px;
    }}
    #SearchFrame[focused="true"] {{
        border-color: {p.border_focus};
    }}
    QLineEdit#SearchInput {{
        background: transparent;
        border: none;
        color: {p.text_primary};
        font-size: 13px;
        padding: 6px 2px;
        selection-background-color: {p.selection_bg};
        selection-color: {p.selection_text};
    }}
    QToolButton#ClearSearchButton {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 3px;
    }}
    QToolButton#ClearSearchButton:hover {{
        background-color: {p.bg_pill_active};
    }}

    #PaneHeaderTitle {{
        color: {p.text_secondary};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.4px;
    }}
    QPushButton#SortButton, QPushButton#EmptyTrashButton {{
        background-color: transparent;
        color: {p.text_muted};
        border: none;
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 11px;
        font-weight: 500;
    }}
    QPushButton#SortButton:hover {{
        background-color: {p.bg_surface};
        color: {p.text_primary};
    }}
    QPushButton#EmptyTrashButton:hover {{
        background-color: {p.danger_bg};
        color: {p.danger};
    }}

    QListView#NotesListView {{
        background-color: {p.bg_list};
        border: none;
        padding: 4px 8px;
    }}

    #ListEmptyStateLabel {{
        color: {p.text_muted};
        font-size: 13px;
    }}

    /* Right Editorial Canvas Pane */
    #EditorPane {{
        background-color: {p.bg_editor};
    }}
    #EditorToolbar {{
        background-color: {p.bg_editor};
        border-bottom: 1px solid {p.border_subtle};
    }}
    #StatusMetaLabel {{
        color: {p.text_muted};
        font-size: 12px;
    }}
    #StatusDotLabel {{
        color: {p.text_secondary};
        font-size: 11px;
        font-weight: 500;
    }}

    /* Segmented mode pill (Write | Split | Preview) */
    #SegmentedControl {{
        background-color: {p.bg_pill};
        border: 1px solid {p.border_subtle};
        border-radius: 8px;
        padding: 2px;
    }}
    QPushButton[segmentButton="true"] {{
        background-color: transparent;
        color: {p.text_secondary};
        border: none;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 600;
    }}
    QPushButton[segmentButton="true"]:hover {{
        color: {p.text_primary};
    }}
    QPushButton[segmentButton="true"][active="true"] {{
        background-color: {p.bg_pill_active};
        color: {p.text_primary};
    }}

    /* Toolbar icon actions */
    QToolButton[iconAction="true"] {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 7px;
        padding: 5px;
    }}
    QToolButton[iconAction="true"]:hover {{
        background-color: {p.bg_surface};
        border-color: {p.border_subtle};
    }}
    QToolButton[iconAction="true"][active="true"] {{
        background-color: {p.bg_pill_active};
        border-color: {p.border_strong};
    }}
    QToolButton[iconAction="true"][danger="true"]:hover {{
        background-color: {p.danger_bg};
        border-color: {p.danger};
    }}

    /* Trash banner */
    #TrashBanner {{
        background-color: {p.bg_surface};
        border: 1px solid {p.border_subtle};
        border-radius: 9px;
    }}
    #TrashBannerLabel {{
        color: {p.text_secondary};
        font-size: 12px;
    }}
    QPushButton#RestoreButton {{
        background-color: {p.bg_pill_active};
        color: {p.text_primary};
        border: none;
        border-radius: 6px;
        padding: 5px 11px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#RestoreButton:hover {{
        background-color: {p.accent};
        color: {p.accent_text};
    }}
    QPushButton#DeleteForeverButton {{
        background-color: {p.danger_bg};
        color: {p.danger};
        border: none;
        border-radius: 6px;
        padding: 5px 11px;
        font-size: 12px;
        font-weight: 600;
    }}

    /* Note Title & Tags */
    QLineEdit#NoteTitleInput {{
        background: transparent;
        border: none;
        color: {p.text_primary};
        font-family: "SF Pro Display", "Helvetica Neue", "Segoe UI", sans-serif;
        font-size: 26px;
        font-weight: 700;
        padding: 4px 0px;
        selection-background-color: {p.selection_bg};
        selection-color: {p.selection_text};
    }}

    QFrame#TagChip {{
        background-color: {p.bg_pill};
        border: 1px solid {p.border_subtle};
        border-radius: 11px;
    }}
    QLabel#TagChipLabel {{
        color: {p.text_secondary};
        font-size: 11px;
        font-weight: 500;
    }}
    QToolButton#TagChipRemove {{
        background: transparent;
        border: none;
        color: {p.text_muted};
        font-size: 12px;
        padding: 0px 2px;
    }}
    QToolButton#TagChipRemove:hover {{
        color: {p.text_primary};
    }}

    QLineEdit#AddTagInput {{
        background-color: transparent;
        border: 1px dashed {p.border_subtle};
        border-radius: 11px;
        color: {p.text_secondary};
        font-size: 11px;
        padding: 2px 9px;
    }}
    QLineEdit#AddTagInput:focus {{
        border-style: solid;
        border-color: {p.border_focus};
        background-color: {p.bg_surface};
        color: {p.text_primary};
    }}

    #CanvasDivider {{
        background-color: {p.border_subtle};
        max-height: 1px;
        min-height: 1px;
    }}

    /* Subtle formatting strip */
    #FormatBar {{
        background-color: transparent;
    }}
    QPushButton[formatBtn="true"] {{
        background-color: transparent;
        color: {p.text_muted};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
        font-family: "SF Mono", "Menlo", "Consolas", monospace;
    }}
    QPushButton[formatBtn="true"]:hover {{
        background-color: {p.bg_surface};
        border-color: {p.border_subtle};
        color: {p.text_primary};
    }}

    /* Markdown Text Editor */
    QPlainTextEdit#NoteBodyEditor {{
        background-color: {p.bg_editor};
        border: none;
        color: {p.text_primary};
        font-family: "SF Pro Text", "Helvetica Neue", "Segoe UI", sans-serif;
        font-size: 15px;
        selection-background-color: {p.selection_bg};
        selection-color: {p.selection_text};
    }}

    /* Rendered Markdown Preview */
    QTextBrowser#MarkdownPreview {{
        background-color: {p.bg_editor};
        border: none;
        color: {p.text_primary};
        selection-background-color: {p.selection_bg};
        selection-color: {p.selection_text};
    }}

    /* Empty canvas placeholder */
    #EmptyCanvasTitle {{
        color: {p.text_secondary};
        font-size: 18px;
        font-weight: 600;
    }}
    #EmptyCanvasSubtitle {{
        color: {p.text_muted};
        font-size: 13px;
    }}
    QPushButton#EmptyCreateButton {{
        background-color: {p.bg_pill};
        color: {p.text_primary};
        border: 1px solid {p.border_strong};
        border-radius: 9px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton#EmptyCreateButton:hover {{
        background-color: {p.bg_pill_active};
    }}

    /* Dialogs */
    QFrame#DialogCard {{
        background-color: {p.bg_list};
        border: 1px solid {p.border_strong};
        border-radius: 12px;
    }}
    QPushButton#DialogPrimaryBtn {{
        background-color: {p.accent};
        color: {p.accent_text};
        border: none;
        border-radius: 8px;
        padding: 7px 16px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#DialogPrimaryBtn:hover {{
        background-color: {p.accent_hover};
    }}
    QPushButton#DialogSecondaryBtn {{
        background-color: {p.bg_pill};
        color: {p.text_primary};
        border: 1px solid {p.border_subtle};
        border-radius: 8px;
        padding: 7px 16px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton#DialogSecondaryBtn:hover {{
        background-color: {p.bg_pill_active};
    }}
    """


def build_markdown_css(p: ThemePalette) -> str:
    """Return CSS for rendering Markdown cleanly inside QTextBrowser."""
    return f"""
    body {{
        background-color: {p.bg_editor};
        color: {p.text_primary};
        font-family: "SF Pro Text", "Helvetica Neue", sans-serif;
        font-size: 15px;
        line-height: 1.65;
        margin: 0;
        padding: 0;
    }}
    h1, h2, h3, h4 {{
        color: {p.text_primary};
        font-family: "SF Pro Display", "Helvetica Neue", sans-serif;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 8px;
    }}
    h1 {{ font-size: 22px; border-bottom: 1px solid {p.border_subtle}; padding-bottom: 6px; }}
    h2 {{ font-size: 18px; }}
    h3 {{ font-size: 15px; color: {p.text_secondary}; }}
    p {{
        margin-top: 0;
        margin-bottom: 12px;
    }}
    a {{
        color: {p.text_primary};
        text-decoration: underline;
    }}
    strong {{
        color: {p.text_primary};
        font-weight: 700;
    }}
    em {{
        color: {p.text_secondary};
    }}
    blockquote {{
        margin: 14px 0;
        padding: 8px 14px;
        background-color: {p.bg_surface};
        border-left: 3px solid {p.border_focus};
        color: {p.text_secondary};
    }}
    code {{
        background-color: {p.bg_code};
        color: {p.text_primary};
        font-family: "SF Mono", "Menlo", "Consolas", monospace;
        font-size: 13px;
        padding: 2px 5px;
    }}
    pre {{
        background-color: {p.bg_code};
        border: 1px solid {p.border_subtle};
        padding: 12px 14px;
        font-family: "SF Mono", "Menlo", "Consolas", monospace;
        font-size: 13px;
        line-height: 1.5;
        margin: 12px 0;
    }}
    ul, ol {{
        margin: 8px 0 12px 20px;
        padding-left: 4px;
    }}
    li {{
        margin-bottom: 5px;
    }}
    hr {{
        border: none;
        border-top: 1px solid {p.border_subtle};
        margin: 18px 0;
    }}
    table {{
        border-collapse: collapse;
        margin: 14px 0;
        width: 100%;
    }}
    th, td {{
        border: 1px solid {p.border_subtle};
        padding: 7px 11px;
        text-align: left;
    }}
    th {{
        background-color: {p.bg_surface};
        color: {p.text_primary};
        font-weight: 600;
    }}
    td {{
        color: {p.text_secondary};
    }}
    """
