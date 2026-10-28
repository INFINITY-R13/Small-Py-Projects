"""
SQLite Database Layer for Contact Book.
Handles persistence, filtering, full-text searching, and sample seeding.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, date
from typing import List, Optional, Dict
from models import Contact


class Database:
    def __init__(self, db_path: str = "contacts.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    birth_date TEXT,
                    instagram TEXT,
                    category TEXT DEFAULT 'General',
                    is_favorite INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            # Create indexes for snappy searching and sorting
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_favorite ON contacts(is_favorite);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category);")
            conn.commit()

        # Seed sample contacts if empty
        self.seed_sample_data_if_empty()

    def seed_sample_data_if_empty(self):
        """Populate realistic sample contacts if database is empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            if count > 0:
                return

        today = date.today()
        # Someone with birthday in 5 days
        soon_month = (today.month % 12) + 1 if today.day > 23 else today.month
        soon_day = (today.day + 5) if today.day <= 23 else 5

        sample_contacts = [
            Contact(
                name="Elena Vance",
                phone="+1 (555) 234-5678",
                email="elena.vance@designcraft.io",
                birth_date=f"1997-{soon_month:02d}-{soon_day:02d}",
                instagram="elena_vance",
                category="Friends",
                is_favorite=True,
                notes="Lead UI/UX designer. Loves specialty coffee, typography, and photography.",
            ),
            Contact(
                name="Liam Gallagher",
                phone="+44 7911 123456",
                email="liam.g@soundwav.co.uk",
                birth_date="1995-04-18",
                instagram="liam_tunes",
                category="Work",
                is_favorite=False,
                notes="Sound engineer & podcast producer. Met at AudioTech Summit 2024.",
            ),
            Contact(
                name="Sophia Rossi",
                phone="+39 02 8901 2345",
                email="sophia.rossi@milan-art.it",
                birth_date="2000-11-28",
                instagram="sophiarossi_art",
                category="VIP",
                is_favorite=True,
                notes="Contemporary artist based in Milan. Gallery exhibition in November.",
            ),
            Contact(
                name="David Chen",
                phone="+1 (415) 890-4321",
                email="dchen@berkeley.edu",
                birth_date="1992-08-14",
                instagram="dchen_photo",
                category="Family",
                is_favorite=False,
                notes="Cousin in San Francisco. Hiking enthusiast & landscape photographer.",
            ),
            Contact(
                name="Amara Okafor",
                phone="+234 802 345 6789",
                email="amara.okafor@finpulse.ng",
                birth_date="1998-02-09",
                instagram="amara_fin",
                category="Work",
                is_favorite=True,
                notes="Fintech software architect. Co-organizer of Python Lagos meetup.",
            ),
        ]

        for c in sample_contacts:
            self.add_contact(c)

    def _row_to_contact(self, row: sqlite3.Row) -> Contact:
        return Contact(
            id=row["id"],
            name=row["name"],
            phone=row["phone"] or "",
            email=row["email"] or "",
            birth_date=row["birth_date"] or "",
            instagram=row["instagram"] or "",
            category=row["category"] or "General",
            is_favorite=bool(row["is_favorite"]),
            notes=row["notes"] or "",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    def add_contact(self, contact: Contact) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO contacts (name, phone, email, birth_date, instagram, category, is_favorite, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contact.name.strip(),
                    contact.phone.strip(),
                    contact.email.strip(),
                    contact.birth_date.strip(),
                    contact.clean_instagram,
                    contact.category.strip() or "General",
                    1 if contact.is_favorite else 0,
                    contact.notes.strip(),
                    now,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_contact(self, contact: Contact) -> bool:
        if not contact.id:
            return False
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, birth_date = ?, instagram = ?,
                    category = ?, is_favorite = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    contact.name.strip(),
                    contact.phone.strip(),
                    contact.email.strip(),
                    contact.birth_date.strip(),
                    contact.clean_instagram,
                    contact.category.strip() or "General",
                    1 if contact.is_favorite else 0,
                    contact.notes.strip(),
                    now,
                    contact.id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_contact(self, contact_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_favorite(self, contact_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END WHERE id = ?",
                (contact_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_contact(row)
        return None

    def get_all(
        self,
        search_query: str = "",
        filter_by: str = "all",
        category_filter: str = "all",
        sort_by: str = "name_asc",
    ) -> List[Contact]:
        """Query contacts with search string, filters, and sorting."""
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []

        clean_search = search_query.strip()
        if clean_search:
            like_term = f"%{clean_search}%"
            query += """ AND (
                name LIKE ? OR
                phone LIKE ? OR
                email LIKE ? OR
                instagram LIKE ? OR
                notes LIKE ?
            )"""
            params.extend([like_term, like_term, like_term, like_term, like_term])

        if filter_by == "favorites":
            query += " AND is_favorite = 1"

        if category_filter and category_filter != "all":
            query += " AND category = ?"
            params.append(category_filter)

        if sort_by == "name_desc":
            query += " ORDER BY name COLLATE NOCASE DESC"
        elif sort_by == "recent":
            query += " ORDER BY id DESC"
        else:
            query += " ORDER BY name COLLATE NOCASE ASC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            contacts = [self._row_to_contact(r) for r in rows]

        if filter_by == "birthdays_soon":
            contacts = [c for c in contacts if c.get_birthday_details()["is_soon"]]
            contacts.sort(key=lambda c: c.get_birthday_details()["days_until"] if c.get_birthday_details()["days_until"] is not None else 999)

        if sort_by == "birthday":
            contacts.sort(
                key=lambda c: (
                    0 if c.get_birthday_details()["has_birthday"] else 1,
                    c.get_birthday_details()["days_until"] if c.get_birthday_details()["days_until"] is not None else 999
                )
            )

        return contacts

    def get_counts(self) -> Dict[str, int]:
        """Get quick statistics for the sidebar tabs."""
        all_contacts = self.get_all(filter_by="all")
        fav_count = sum(1 for c in all_contacts if c.is_favorite)
        bday_count = sum(1 for c in all_contacts if c.get_birthday_details()["is_soon"])
        return {
            "total": len(all_contacts),
            "favorites": fav_count,
            "birthdays_soon": bday_count,
        }

    def get_all_categories(self) -> List[str]:
        """Get unique categories in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM contacts WHERE category IS NOT NULL AND category != '' ORDER BY category ASC")
            rows = cursor.fetchall()
            cats = [r[0] for r in rows]
        defaults = ["General", "Friends", "Family", "Work", "VIP"]
        for d in defaults:
            if d not in cats:
                cats.append(d)
        return cats
