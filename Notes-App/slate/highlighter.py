"""Subtle monochrome grey Markdown syntax highlighter for the editor."""

from __future__ import annotations

import re

from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument

from slate.themes import ThemePalette


class MarkdownHighlighter(QSyntaxHighlighter):
    """Applies restrained grey-scale Markdown formatting to QTextDocument blocks."""

    def __init__(self, document: QTextDocument, palette: ThemePalette) -> None:
        super().__init__(document)
        self._palette = palette
        self._build_formats()

    def set_palette(self, palette: ThemePalette) -> None:
        """Update palette colors and re-highlight the entire document."""
        self._palette = palette
        self._build_formats()
        self.rehighlight()

    def _build_formats(self) -> None:
        p = self._palette

        self._h1_fmt = QTextCharFormat()
        self._h1_fmt.setForeground(QColor(p.text_primary))
        self._h1_fmt.setFontWeight(QFont.Weight.Bold)
        self._h1_fmt.setFontPointSize(20)

        self._h2_fmt = QTextCharFormat()
        self._h2_fmt.setForeground(QColor(p.text_primary))
        self._h2_fmt.setFontWeight(QFont.Weight.Bold)
        self._h2_fmt.setFontPointSize(17)

        self._h3_fmt = QTextCharFormat()
        self._h3_fmt.setForeground(QColor(p.text_secondary))
        self._h3_fmt.setFontWeight(QFont.Weight.Bold)
        self._h3_fmt.setFontPointSize(15)

        self._syntax_muted_fmt = QTextCharFormat()
        self._syntax_muted_fmt.setForeground(QColor(p.text_muted))

        self._bold_fmt = QTextCharFormat()
        self._bold_fmt.setForeground(QColor(p.text_primary))
        self._bold_fmt.setFontWeight(QFont.Weight.Bold)

        self._italic_fmt = QTextCharFormat()
        self._italic_fmt.setForeground(QColor(p.text_secondary))
        self._italic_fmt.setFontItalic(True)

        self._code_fmt = QTextCharFormat()
        self._code_fmt.setForeground(QColor(p.text_primary))
        self._code_fmt.setBackground(QColor(p.bg_code))
        self._code_fmt.setFontFamilies(["SF Mono", "Menlo", "Consolas", "monospace"])

        self._quote_fmt = QTextCharFormat()
        self._quote_fmt.setForeground(QColor(p.text_secondary))
        self._quote_fmt.setFontItalic(True)

        self._checklist_fmt = QTextCharFormat()
        self._checklist_fmt.setForeground(QColor(p.accent))
        self._checklist_fmt.setFontWeight(QFont.Weight.DemiBold)

        self._rules: list[tuple[re.Pattern[str], QTextCharFormat]] = [
            (re.compile(r"\*\*[^*\n]+\*\*"), self._bold_fmt),
            (re.compile(r"__[^_\n]+__"), self._bold_fmt),
            (re.compile(r"(?<!\*)\*(?!\*)[^*\n]+(?<!\*)\*(?!\*)"), self._italic_fmt),
            (re.compile(r"`[^`\n]+`"), self._code_fmt),
            (re.compile(r"^\s*[-*+]\s+\[[ xX]\]"), self._checklist_fmt),
            (re.compile(r"^\s*(?:[-*+]|\d+\.)\s+"), self._syntax_muted_fmt),
        ]

    def highlightBlock(self, text: str) -> None:
        """Highlight headings, fenced code blocks, quotes, and inline Markdown."""
        prev_state = self.previousBlockState()
        in_code_block = prev_state == 1

        if text.lstrip().startswith("```"):
            self.setFormat(0, len(text), self._code_fmt)
            self.setCurrentBlockState(0 if in_code_block else 1)
            return

        if in_code_block:
            self.setFormat(0, len(text), self._code_fmt)
            self.setCurrentBlockState(1)
            return

        self.setCurrentBlockState(0)

        if text.startswith("### "):
            self.setFormat(0, len(text), self._h3_fmt)
            self.setFormat(0, 4, self._syntax_muted_fmt)
            return
        if text.startswith("## "):
            self.setFormat(0, len(text), self._h2_fmt)
            self.setFormat(0, 3, self._syntax_muted_fmt)
            return
        if text.startswith("# "):
            self.setFormat(0, len(text), self._h1_fmt)
            self.setFormat(0, 2, self._syntax_muted_fmt)
            return
        if text.lstrip().startswith(">"):
            self.setFormat(0, len(text), self._quote_fmt)
            return

        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
