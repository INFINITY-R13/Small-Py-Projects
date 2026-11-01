"""
Configuration settings, design constants, and color palette for the
Apple-inspired minimalist Pink Habit Tracker.
"""

from typing import Dict, Any

APP_NAME = "Bloom Habit Tracker"
APP_VERSION = "1.0.0"

# Minimalist Apple-inspired Color Palette (Blush Light & Midnight Rose Dark)
THEME = {
    "light": {
        "bg_base": "#FAF6F8",            # Soft warm porcelain blush
        "bg_secondary": "#F3EBF0",       # Muted subtle container background
        "card_bg": "#FFFFFF",            # Crisp clean white surface
        "card_border": "#F3E1E7",        # Hairline 1px border
        "card_hover": "#FFF9FB",         # Hover state for cards
        "primary_pink": "#FF5288",       # Vibrant Apple-style rose pink
        "primary_hover": "#E63E72",      # Hover state for primary buttons
        "primary_pressed": "#CC3261",    # Pressed state
        "soft_pink": "#FDEBF1",          # Pastel blush badge / background
        "soft_pink_hover": "#FCD7E3",    # Hover for soft pink pills
        "soft_pink_border": "#F8CAD8",   # Border for soft pills
        "text_primary": "#1D191B",       # Apple charcoal / nearly black
        "text_secondary": "#7D7379",     # Refined neutral secondary
        "text_tertiary": "#ADA3A9",      # Muted metadata
        "ring_bg": "#FCE5ED",            # Unfilled progress ring color
        "ring_progress": "#FF5288",      # Filled progress ring color
        "streak_badge_bg": "#FFF1F4",    # Streak pill background
        "streak_badge_text": "#E03C6E",  # Streak pill text
        "divider": "#F2E4EA",            # Subtle separator lines
        "modal_overlay": "#1D191B",      # Modal overlay tone
    },
    "dark": {
        "bg_base": "#141013",            # Deep obsidian berry
        "bg_secondary": "#1E171C",       # Muted container background
        "card_bg": "#221A20",            # Rich dark mauve surface
        "card_border": "#352731",        # Hairline subtle border
        "card_hover": "#2B2129",         # Hover state for cards
        "primary_pink": "#FF6093",       # Luminous Apple rose
        "primary_hover": "#FF4D85",      # Hover state for primary buttons
        "primary_pressed": "#E63A70",    # Pressed state
        "soft_pink": "#37202B",          # Deep translucent rose tint
        "soft_pink_hover": "#462937",    # Hover for soft pink pills
        "soft_pink_border": "#553243",   # Border for soft pills
        "text_primary": "#FDFBFC",       # Crisp clean white
        "text_secondary": "#A89BA2",     # Apple dark mode secondary
        "text_tertiary": "#6E6168",      # Muted metadata
        "ring_bg": "#36222D",            # Unfilled progress ring color
        "ring_progress": "#FF6093",      # Filled progress ring color
        "streak_badge_bg": "#3A1E2B",    # Streak pill background
        "streak_badge_text": "#FF7AA5",  # Streak pill text
        "divider": "#2C2029",            # Subtle separator lines
        "modal_overlay": "#0A0709",      # Modal overlay tone
    }
}

# Typography
FONTS = {
    "title_large": ("Helvetica Neue", 26, "bold"),
    "title_medium": ("Helvetica Neue", 18, "bold"),
    "title_small": ("Helvetica Neue", 15, "bold"),
    "body_bold": ("Helvetica Neue", 13, "bold"),
    "body": ("Helvetica Neue", 13),
    "caption_bold": ("Helvetica Neue", 11, "bold"),
    "caption": ("Helvetica Neue", 11),
    "subscript": ("Helvetica Neue", 9),
    "stat_number": ("Helvetica Neue", 28, "bold"),
    "stat_label": ("Helvetica Neue", 11),
}

# Default Curated Emojis for quick selection
CURATED_EMOJIS = [
    ("💧", "Hydrate"),
    ("🏃", "Exercise"),
    ("🧘", "Meditate"),
    ("📚", "Reading"),
    ("🍵", "Tea / Matcha"),
    ("🥑", "Healthy Eat"),
    ("💻", "Deep Work"),
    ("💤", "Sleep Well"),
    ("🌿", "Outdoors"),
    ("✨", "Gratitude"),
    ("✍️", "Journal"),
    ("🎨", "Creative"),
    ("🌸", "Self Care"),
    ("🎯", "Focus Goal"),
    ("🧴", "Skincare"),
    ("🚶", "Walk 10k"),
]

# Habit Routines / Times of Day
ROUTINES = ["Anytime", "Morning", "Afternoon", "Evening"]

# Habit Categories
CATEGORIES = [
    "Health",
    "Mindfulness",
    "Productivity",
    "Fitness",
    "Self Care",
    "Learning",
    "Personal",
]

# Target Frequencies
FREQUENCIES = [
    "Every Day",
    "Weekdays (Mon-Fri)",
    "Weekends (Sat-Sun)",
    "4 Days a Week",
]

# Minimalist Motivational Quotes
AESTHETIC_QUOTES = [
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Aristotle"),
    ("Small disciplines repeated with consistency every day lead to great achievements.", "John C. Maxwell"),
    ("You do not rise to the level of your goals. You fall to the level of your systems.", "James Clear"),
    ("Habits change into character.", "Ovid"),
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("Small steps every day add up to big results.", "Anonymous"),
    ("Bloom where you are planted, one daily petal at a time.", "Aesthetic Proverb"),
    ("Peace comes from within. Do not seek it without.", "Buddha"),
    ("Success is the sum of small efforts, repeated day in and day out.", "Robert Collier"),
]
