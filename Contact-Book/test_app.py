"""
Comprehensive tests for Contact Book app functionality.
"""

import os
import tempfile
import unittest
from datetime import date
from models import Contact
from database import Database
from utils.validators import (
    validate_name,
    validate_phone,
    validate_email,
    parse_and_validate_birth_date,
    validate_instagram,
)
from utils.exporters import (
    export_contacts_to_csv,
    export_contacts_to_json,
    import_contacts_from_csv,
    import_contacts_from_json,
)


class TestContactBook(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_contacts.db")
        self.db = Database(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sample_seeding(self):
        contacts = self.db.get_all()
        self.assertGreaterEqual(len(contacts), 5)
        counts = self.db.get_counts()
        self.assertGreaterEqual(counts["total"], 5)
        self.assertGreaterEqual(counts["favorites"], 1)

    def test_add_and_get_contact(self):
        c = Contact(
            name="Test User",
            phone="+1 555 999 8888",
            email="test@domain.com",
            birth_date="1999-05-20",
            instagram="@test_dev",
            category="Work",
            is_favorite=True,
            notes="Testing contact creation",
        )
        c_id = self.db.add_contact(c)
        retrieved = self.db.get_by_id(c_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test User")
        self.assertEqual(retrieved.clean_instagram, "test_dev")
        self.assertTrue(retrieved.is_favorite)

    def test_search_and_filter(self):
        results = self.db.get_all(search_query="Vance")
        self.assertTrue(any(c.name == "Elena Vance" for c in results))

        fav_results = self.db.get_all(filter_by="favorites")
        self.assertTrue(all(c.is_favorite for c in fav_results))

    def test_birthday_calculation(self):
        today = date.today()
        # Today's birthday
        c_today = Contact(name="Birthday Person", birth_date=f"2000-{today.month:02d}-{today.day:02d}")
        b_info = c_today.get_birthday_details()
        self.assertTrue(b_info["has_birthday"])
        self.assertTrue(b_info["is_today"])
        self.assertEqual(b_info["days_until"], 0)

    def test_validators(self):
        # Name
        self.assertTrue(validate_name("John Doe")[0])
        self.assertFalse(validate_name("   ")[0])

        # Email
        self.assertTrue(validate_email("user@example.com")[0])
        self.assertFalse(validate_email("not-an-email")[0])
        self.assertTrue(validate_email("")[0])  # Optional

        # Phone
        self.assertTrue(validate_phone("+1 (555) 234-5678")[0])
        self.assertFalse(validate_phone("123")[0])  # Too short

        # Instagram
        self.assertEqual(validate_instagram("@my_insta")[1], "my_insta")
        self.assertEqual(validate_instagram("https://instagram.com/my_insta/")[1], "my_insta")

        # Birth date
        ok, parsed = parse_and_validate_birth_date("15/08/1995")
        self.assertTrue(ok)
        self.assertEqual(parsed, "1995-08-15")

    def test_export_and_import(self):
        contacts = self.db.get_all()
        csv_path = os.path.join(self.temp_dir.name, "export.csv")
        json_path = os.path.join(self.temp_dir.name, "export.json")

        # CSV
        ok, msg = export_contacts_to_csv(contacts, csv_path)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(csv_path))

        ok, imported_csv, msg = import_contacts_from_csv(csv_path)
        self.assertTrue(ok)
        self.assertEqual(len(imported_csv), len(contacts))

        # JSON
        ok, msg = export_contacts_to_json(contacts, json_path)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(json_path))

        ok, imported_json, msg = import_contacts_from_json(json_path)
        self.assertTrue(ok)
        self.assertEqual(len(imported_json), len(contacts))


if __name__ == "__main__":
    unittest.main()
