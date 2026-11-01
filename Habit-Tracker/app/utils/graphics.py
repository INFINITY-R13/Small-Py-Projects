"""
High-resolution, anti-aliased graphics generator for CustomTkinter UI.
Renders Apple-style progress rings, completion checkmarks, week dots,
and bar indicators using Pillow supersampling.
"""

import math
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import customtkinter as ctk


def create_circular_progress_image(
    percentage: float,
    size: int = 120,
    stroke_width: int = 10,
    bg_color: str = "#FCE5ED",
    progress_color: str = "#FF5288",
    scale: int = 3
) -> ctk.CTkImage:
    """
    Renders an Apple Fitness-style circular progress ring with supersampling.
    """
    pct = max(0.0, min(100.0, percentage))
    w, h = size * scale, size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = (stroke_width / 2.0 + 2) * scale
    box = [pad, pad, w - pad, h - pad]
    scaled_stroke = int(stroke_width * scale)

    # Draw full background track
    draw.ellipse(box, outline=bg_color, width=scaled_stroke)

    # Draw active progress arc
    if pct > 0:
        sweep = (pct / 100.0) * 360.0
        start_angle = -90.0
        end_angle = start_angle + sweep

        # PIL arc angles go clockwise when start < end with 0 at 3 o'clock
        draw.arc(box, start=start_angle, end=end_angle, fill=progress_color, width=scaled_stroke)

        # Smooth rounded end cap at start
        radius = (w - 2 * pad) / 2.0
        center_x, center_y = w / 2.0, h / 2.0
        cap_r = scaled_stroke / 2.0

        # Start cap (at -90 deg / top)
        start_rad = math.radians(start_angle)
        sx = center_x + radius * math.cos(start_rad)
        sy = center_y + radius * math.sin(start_rad)
        draw.ellipse([sx - cap_r, sy - cap_r, sx + cap_r, sy + cap_r], fill=progress_color)

        # End cap
        end_rad = math.radians(end_angle)
        ex = center_x + radius * math.cos(end_rad)
        ey = center_y + radius * math.sin(end_rad)
        draw.ellipse([ex - cap_r, ey - cap_r, ex + cap_r, ey + cap_r], fill=progress_color)

    # Resize with antialiasing
    rendered = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=rendered, dark_image=rendered, size=(size, size))


def create_check_button_image(
    completed: bool,
    size: int = 34,
    primary_color: str = "#FF5288",
    border_color: str = "#F2CCD8",
    scale: int = 3
) -> ctk.CTkImage:
    """
    Renders an Apple-style circular checkbox.
    Empty circle when incomplete, filled pink circle with crisp checkmark when completed.
    """
    w, h = size * scale, size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 2 * scale
    box = [margin, margin, w - margin, h - margin]

    if completed:
        # Filled vibrant rose circle
        draw.ellipse(box, fill=primary_color)

        # Crisp white checkmark
        pts = [
            (size * 0.28 * scale, size * 0.50 * scale),
            (size * 0.44 * scale, size * 0.68 * scale),
            (size * 0.72 * scale, size * 0.35 * scale),
        ]
        line_w = int(2.8 * scale)
        draw.line([pts[0], pts[1]], fill="#FFFFFF", width=line_w)
        draw.line([pts[1], pts[2]], fill="#FFFFFF", width=line_w)
        # Smooth corner joint
        cr = line_w / 2.0
        draw.ellipse(
            [pts[1][0] - cr, pts[1][1] - cr, pts[1][0] + cr, pts[1][1] + cr],
            fill="#FFFFFF"
        )
    else:
        # Delicate hairline border
        stroke_w = int(2.0 * scale)
        draw.ellipse(box, outline=border_color, width=stroke_w)

    rendered = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=rendered, dark_image=rendered, size=(size, size))


def create_mini_dot_image(
    status: str,
    size: int = 14,
    primary_color: str = "#FF5288",
    muted_color: str = "#E8D8DE",
    scale: int = 3
) -> ctk.CTkImage:
    """
    Renders a status dot for week history strips.
    - 'completed': filled pink circle
    - 'today_pending': subtle ring waiting to be completed
    - 'missed': faint small gray dot
    """
    w, h = size * scale, size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = w / 2.0

    if status == "completed":
        r = (size * 0.38) * scale
        draw.ellipse([center - r, center - r, center + r, center + r], fill=primary_color)
    elif status == "today_pending":
        r = (size * 0.36) * scale
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            outline=primary_color,
            width=int(1.8 * scale)
        )
    else:  # 'missed' or 'future'
        r = (size * 0.22) * scale
        draw.ellipse([center - r, center - r, center + r, center + r], fill=muted_color)

    rendered = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=rendered, dark_image=rendered, size=(size, size))


def create_vertical_progress_bar_image(
    percentage: float,
    width: int = 24,
    height: int = 90,
    active_color: str = "#FF5288",
    track_color: str = "#FCE5ED",
    scale: int = 3
) -> ctk.CTkImage:
    """
    Renders an Apple-style rounded vertical bar for weekly analytics charts.
    """
    pct = max(0.0, min(100.0, percentage))
    w, h = width * scale, height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    r = w / 2.0

    # Draw background capsule
    draw.rounded_rectangle([0, 0, w, h], radius=r, fill=track_color)

    # Draw active fill from bottom up
    if pct > 0:
        fill_h = max(r * 2, (pct / 100.0) * h)
        top_y = h - fill_h
        draw.rounded_rectangle([0, top_y, w, h], radius=r, fill=active_color)

    rendered = img.resize((width, height), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=rendered, dark_image=rendered, size=(width, height))
