"""Crisp, theme-tinted SVG icons rendered at Retina resolution."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


_ICONS: dict[str, str] = {
    "slate_logo": (
        '<rect x="4" y="3" width="16" height="18" rx="3" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="8" y1="16" x2="12.5" y2="16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
    ),
    "plus": (
        '<line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
    ),
    "notes": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" '
        'stroke="currentColor" stroke-width="1.75" fill="none" stroke-linejoin="round"/>'
        '<polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linejoin="round"/>'
        '<line x1="8" y1="13" x2="16" y2="13" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
        '<line x1="8" y1="17" x2="13" y2="17" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
    ),
    "pin": (
        '<path d="M12 17v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z" '
        'stroke="currentColor" stroke-width="1.75" fill="none" stroke-linejoin="round"/>'
    ),
    "pin_filled": (
        '<path d="M12 17v5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>'
        '<path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z" '
        'stroke="currentColor" stroke-width="1.6" fill="currentColor" stroke-linejoin="round"/>'
    ),
    "trash": (
        '<polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round"/>'
        '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linejoin="round"/>'
        '<path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
        '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" stroke="currentColor" stroke-width="1.75" fill="none"/>'
    ),
    "tag": (
        '<line x1="9" y1="4" x2="7" y2="20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="17" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="4" y1="9" x2="20" y2="9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="3" y1="15" x2="19" y2="15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
    ),
    "close": (
        '<line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>'
        '<line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>'
    ),
    "moon": (
        '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" '
        'stroke="currentColor" stroke-width="1.75" fill="none" stroke-linejoin="round"/>'
    ),
    "sun": (
        '<circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.75" fill="none"/>'
        '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
    ),
    "focus": (
        '<polyline points="15 3 21 3 21 9" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<polyline points="9 21 3 21 3 15" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="21" y1="3" x2="14" y2="10" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
        '<line x1="3" y1="21" x2="10" y2="14" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
    ),
    "export": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round"/>'
        '<polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>'
    ),
    "sort": (
        '<line x1="4" y1="7" x2="20" y2="7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="7" y1="12" x2="17" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<line x1="10" y1="17" x2="14" y2="17" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
    ),
    "help": (
        '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.75" fill="none"/>'
        '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="currentColor" stroke-width="1.75" fill="none" stroke-linecap="round"/>'
        '<circle cx="12" cy="17" r="0.8" fill="currentColor"/>'
    ),
}


def render_svg_pixmap(name: str, color: str, size: int = 16, dpr: float = 2.0) -> QPixmap:
    """Render a named SVG icon into a crisp high-DPI QPixmap."""
    body = _ICONS.get(name, "")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        f'{body.replace("currentColor", color)}'
        f"</svg>"
    )
    pixel_size = int(size * dpr)
    pixmap = QPixmap(QSize(pixel_size, pixel_size))
    pixmap.fill(Qt.GlobalColor.transparent)

    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()

    pixmap.setDevicePixelRatio(dpr)
    return pixmap


def svg_icon(name: str, color: str, size: int = 16) -> QIcon:
    """Create a QIcon from an SVG icon name and hex color."""
    return QIcon(render_svg_pixmap(name, color, size=size))
