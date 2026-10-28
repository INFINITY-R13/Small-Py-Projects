"""
Data Validators and Sanitizers for Contact Book.
"""

import re
from datetime import datetime
from typing import Tuple, Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
INSTAGRAM_REGEX = re.compile(r"^[a-zA-Z0-9._]{1,30}$")


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate contact name."""
    clean = name.strip()
    if not clean:
        return False, "Contact name cannot be empty."
    if len(clean) > 80:
        return False, "Contact name is too long (max 80 characters)."
    return True, clean


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate and format phone number.
    Returns (is_valid, formatted_phone_or_error).
    Phone is optional; if empty, it's valid.
    """
    clean = phone.strip()
    if not clean:
        return True, ""

    # Allow common international characters: +, digits, spaces, -, (, ), .
    digits = re.sub(r"\D", "", clean)
    if len(digits) < 7:
        return False, "Phone number must contain at least 7 digits."
    if len(digits) > 16:
        return False, "Phone number is too long (max 16 digits)."

    return True, clean


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address.
    Email is optional; if empty, it's valid.
    """
    clean = email.strip()
    if not clean:
        return True, ""

    if not EMAIL_REGEX.match(clean):
        return False, "Invalid email format (e.g. name@example.com)."

    return True, clean.lower()


def parse_and_validate_birth_date(birth_date_str: str) -> Tuple[bool, str]:
    """
    Parse birth date from multiple common formats and return ISO format YYYY-MM-DD.
    Accepts: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, YYYY/MM/DD, DD-MM-YYYY.
    Optional; if empty, it's valid.
    """
    clean = birth_date_str.strip()
    if not clean:
        return True, ""

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]

    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(clean, fmt).date()
            break
        except ValueError:
            continue

    if not parsed_date:
        return False, "Invalid date format. Please use YYYY-MM-DD (e.g. 1998-05-15)."

    today = datetime.now().date()
    if parsed_date > today:
        return False, "Birth date cannot be in the future."
    if parsed_date.year < 1900:
        return False, "Birth date year must be after 1900."

    return True, parsed_date.strftime("%Y-%m-%d")


def validate_instagram(handle: str) -> Tuple[bool, str]:
    """
    Validate and sanitize Instagram handle.
    Removes @, url links, trailing slashes.
    Optional; if empty, it's valid.
    """
    clean = handle.strip()
    if not clean:
        return True, ""

    if "instagram.com/" in clean:
        clean = clean.split("instagram.com/")[-1]
    clean = clean.lstrip("@").strip().rstrip("/")

    if not clean:
        return True, ""

    if not INSTAGRAM_REGEX.match(clean):
        return False, "Instagram handle should only contain letters, numbers, periods, and underscores (1-30 chars)."

    return True, clean
