"""
Export and Import utilities for CSV and JSON contact backups.
"""

import csv
import json
from typing import List, Tuple
from models import Contact
from utils.validators import (
    validate_name,
    validate_phone,
    validate_email,
    parse_and_validate_birth_date,
    validate_instagram,
)


def export_contacts_to_csv(contacts: List[Contact], filepath: str) -> Tuple[bool, str]:
    """Export list of contacts to a CSV file."""
    try:
        fieldnames = [
            "name",
            "phone",
            "email",
            "birth_date",
            "instagram",
            "category",
            "is_favorite",
            "notes",
            "created_at",
            "updated_at",
        ]
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in contacts:
                writer.writerow({
                    "name": c.name,
                    "phone": c.phone,
                    "email": c.email,
                    "birth_date": c.birth_date,
                    "instagram": c.clean_instagram,
                    "category": c.category,
                    "is_favorite": 1 if c.is_favorite else 0,
                    "notes": c.notes,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                })
        return True, f"Successfully exported {len(contacts)} contacts to CSV."
    except Exception as e:
        return False, f"Failed to export CSV: {str(e)}"


def export_contacts_to_json(contacts: List[Contact], filepath: str) -> Tuple[bool, str]:
    """Export list of contacts to a JSON file."""
    try:
        data = []
        for c in contacts:
            data.append({
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "birth_date": c.birth_date,
                "instagram": c.clean_instagram,
                "category": c.category,
                "is_favorite": bool(c.is_favorite),
                "notes": c.notes,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            })
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, f"Successfully exported {len(contacts)} contacts to JSON."
    except Exception as e:
        return False, f"Failed to export JSON: {str(e)}"


def import_contacts_from_csv(filepath: str) -> Tuple[bool, List[Contact], str]:
    """Import contacts from CSV file."""
    contacts: List[Contact] = []
    skipped = 0
    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Find matching keys case-insensitively
                clean_row = {k.strip().lower(): v for k, v in row.items() if k}
                name = clean_row.get("name", "").strip()
                if not name:
                    skipped += 1
                    continue

                phone = clean_row.get("phone", clean_row.get("phone number", clean_row.get("mobile", ""))).strip()
                email = clean_row.get("email", clean_row.get("email address", "")).strip()
                bdate = clean_row.get("birth_date", clean_row.get("birth date", clean_row.get("birthday", ""))).strip()
                insta = clean_row.get("instagram", clean_row.get("instagram handle", "")).strip()
                category = clean_row.get("category", "General").strip() or "General"
                notes = clean_row.get("notes", "").strip()
                is_fav_val = str(clean_row.get("is_favorite", clean_row.get("favorite", "0"))).lower()
                is_fav = is_fav_val in ("1", "true", "yes", "y")

                # Sanitize date if provided
                _, valid_bdate = parse_and_validate_birth_date(bdate)
                _, valid_insta = validate_instagram(insta)

                contacts.append(
                    Contact(
                        name=name,
                        phone=phone,
                        email=email,
                        birth_date=valid_bdate if valid_bdate else bdate,
                        instagram=valid_insta if valid_insta else insta,
                        category=category,
                        is_favorite=is_fav,
                        notes=notes,
                    )
                )

        msg = f"Imported {len(contacts)} contacts."
        if skipped > 0:
            msg += f" (Skipped {skipped} rows without names)."
        return True, contacts, msg
    except Exception as e:
        return False, [], f"Failed to import CSV: {str(e)}"


def import_contacts_from_json(filepath: str) -> Tuple[bool, List[Contact], str]:
    """Import contacts from JSON file."""
    contacts: List[Contact] = []
    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return False, [], "Invalid JSON format: expected a list of contact objects."

        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "").strip()
            if not name:
                continue

            phone = str(item.get("phone", "")).strip()
            email = str(item.get("email", "")).strip()
            bdate = str(item.get("birth_date", item.get("birthday", ""))).strip()
            insta = str(item.get("instagram", "")).strip()
            category = str(item.get("category", "General")).strip() or "General"
            is_fav = bool(item.get("is_favorite", item.get("favorite", False)))
            notes = str(item.get("notes", "")).strip()

            _, valid_bdate = parse_and_validate_birth_date(bdate)
            _, valid_insta = validate_instagram(insta)

            contacts.append(
                Contact(
                    name=name,
                    phone=phone,
                    email=email,
                    birth_date=valid_bdate if valid_bdate else bdate,
                    instagram=valid_insta if valid_insta else insta,
                    category=category,
                    is_favorite=is_fav,
                    notes=notes,
                )
            )

        return True, contacts, f"Imported {len(contacts)} contacts from JSON."
    except Exception as e:
        return False, [], f"Failed to import JSON: {str(e)}"
