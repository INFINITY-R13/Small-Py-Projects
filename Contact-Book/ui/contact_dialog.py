"""
Add/Edit Contact Modal Dialog with validation and light grey aesthetic styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from models import Contact
from utils.validators import (
    validate_name,
    validate_phone,
    validate_email,
    parse_and_validate_birth_date,
    validate_instagram,
)
from ui.theme import (
    BG_APP,
    BG_SURFACE,
    BORDER_COLOR,
    BORDER_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_PRIMARY_TEXT,
    FONT_TITLE,
    FONT_BOLD,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    DANGER_COLOR,
    ACCENT_STAR,
)
from ui.components import ModernButton


class ContactDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        contact: Optional[Contact] = None,
        on_save: Optional[Callable[[Contact], None]] = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.contact = contact
        self.on_save = on_save
        self.is_edit = contact is not None

        self.title("Edit Contact" if self.is_edit else "New Contact")
        self.config(bg=BG_APP)
        self.resizable(False, False)

        # Transience and modal behavior
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._populate_fields()
        self._center_window()

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", self._on_enter_press)

    def _center_window(self):
        self.update_idletasks()
        w = 480
        h = 620
        px = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        py = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(50, px)}+{max(50, py)}")

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_SURFACE, padx=24, pady=18)
        header.pack(fill=tk.X)

        title_text = "✏️ Edit Contact" if self.is_edit else "✨ Create New Contact"
        subtitle_text = "Update the contact details below" if self.is_edit else "Add contact details, social links and birthday"

        lbl_title = tk.Label(header, text=title_text, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_TITLE)
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(header, text=subtitle_text, bg=BG_SURFACE, fg=TEXT_SECONDARY, font=FONT_SMALL)
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Divider
        tk.Frame(self, bg=BORDER_COLOR, height=1).pack(fill=tk.X)

        # Form Container
        body = tk.Frame(self, bg=BG_APP, padx=24, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        # Error label
        self.error_label = tk.Label(body, text="", bg=BG_APP, fg=DANGER_COLOR, font=FONT_SMALL, wraplength=430)
        self.error_label.pack(fill=tk.X, pady=(0, 6))

        # Helper to create styled form fields
        def make_field(label_text: str, hint: str = ""):
            row = tk.Frame(body, bg=BG_APP)
            row.pack(fill=tk.X, pady=(0, 9))

            lbl_frame = tk.Frame(row, bg=BG_APP)
            lbl_frame.pack(fill=tk.X, anchor="w", pady=(0, 3))

            lbl = tk.Label(lbl_frame, text=label_text, bg=BG_APP, fg=TEXT_PRIMARY, font=FONT_BOLD)
            lbl.pack(side=tk.LEFT)

            if hint:
                lbl_hint = tk.Label(lbl_frame, text=f" ({hint})", bg=BG_APP, fg=TEXT_MUTED, font=FONT_SMALL)
                lbl_hint.pack(side=tk.LEFT)

            entry_box = tk.Frame(row, bg=BORDER_COLOR, padx=1, pady=1)
            entry_box.pack(fill=tk.X)

            entry = tk.Entry(
                entry_box,
                font=FONT_BODY,
                bg=BG_SURFACE,
                fg=TEXT_PRIMARY,
                bd=0,
                relief=tk.FLAT,
                insertbackground=TEXT_PRIMARY,
            )
            entry.pack(fill=tk.X, ipady=6, padx=8)
            return entry

        self.name_entry = make_field("Full Name *", "required")
        self.phone_entry = make_field("Phone Number", "e.g. +1 (555) 123-4567")
        self.email_entry = make_field("Email Address", "e.g. alex@example.com")
        self.birth_date_entry = make_field("Birth Date", "YYYY-MM-DD or DD/MM/YYYY")
        self.instagram_entry = make_field("Instagram", "@username or link")

        # Category and Favorite Row
        meta_row = tk.Frame(body, bg=BG_APP)
        meta_row.pack(fill=tk.X, pady=(0, 9))

        # Category
        cat_frame = tk.Frame(meta_row, bg=BG_APP)
        cat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(cat_frame, text="Category / Group", bg=BG_APP, fg=TEXT_PRIMARY, font=FONT_BOLD).pack(anchor="w", pady=(0, 3))
        self.category_var = tk.StringVar(value="General")
        self.category_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            values=["General", "Friends", "Family", "Work", "VIP"],
            state="readonly",
            font=FONT_BODY,
        )
        self.category_combo.pack(fill=tk.X, ipady=3)

        # Favorite Checkbox
        fav_frame = tk.Frame(meta_row, bg=BG_APP)
        fav_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(fav_frame, text="Favorite Contact", bg=BG_APP, fg=TEXT_PRIMARY, font=FONT_BOLD).pack(anchor="w", pady=(0, 3))
        self.is_favorite_var = tk.BooleanVar(value=False)
        self.fav_chk = tk.Checkbutton(
            fav_frame,
            text="⭐ Star as Favorite",
            variable=self.is_favorite_var,
            bg=BG_APP,
            fg=TEXT_PRIMARY,
            font=FONT_BODY,
            activebackground=BG_APP,
            highlightthickness=0,
            bd=0,
        )
        self.fav_chk.pack(anchor="w", pady=(2, 0))

        # Notes
        notes_row = tk.Frame(body, bg=BG_APP)
        notes_row.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Label(notes_row, text="Notes", bg=BG_APP, fg=TEXT_PRIMARY, font=FONT_BOLD).pack(anchor="w", pady=(0, 3))
        notes_box = tk.Frame(notes_row, bg=BORDER_COLOR, padx=1, pady=1)
        notes_box.pack(fill=tk.BOTH, expand=True)

        self.notes_text = tk.Text(
            notes_box,
            font=FONT_BODY,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            bd=0,
            relief=tk.FLAT,
            height=3,
            wrap=tk.WORD,
            insertbackground=TEXT_PRIMARY,
        )
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Footer Actions
        footer = tk.Frame(self, bg=BG_SURFACE, padx=24, pady=14)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        btn_cancel = ModernButton(
            footer,
            text="Cancel",
            command=self.destroy,
            bg="#E2E8F0",
            fg=TEXT_PRIMARY,
            hover_bg="#CBD5E1",
            font=FONT_BODY_BOLD,
            padx=18,
            pady=7,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(8, 0))

        btn_save = ModernButton(
            footer,
            text="Save Contact",
            command=self._save,
            bg=ACCENT_PRIMARY,
            fg=ACCENT_PRIMARY_TEXT,
            hover_bg=ACCENT_PRIMARY_HOVER,
            font=FONT_BODY_BOLD,
            padx=20,
            pady=7,
        )
        btn_save.pack(side=tk.RIGHT)

        # Focus initial field
        self.name_entry.focus_set()

    def _populate_fields(self):
        if not self.contact:
            return
        self.name_entry.insert(0, self.contact.name)
        self.phone_entry.insert(0, self.contact.phone)
        self.email_entry.insert(0, self.contact.email)
        self.birth_date_entry.insert(0, self.contact.birth_date)
        self.instagram_entry.insert(0, self.contact.instagram)
        self.category_var.set(self.contact.category or "General")
        self.is_favorite_var.set(self.contact.is_favorite)
        self.notes_text.insert("1.0", self.contact.notes)

    def _on_enter_press(self, event):
        # Ignore return when inside notes multiline text
        if event.widget == self.notes_text:
            return
        self._save()

    def _save(self):
        # Validation
        raw_name = self.name_entry.get()
        name_valid, clean_name = validate_name(raw_name)
        if not name_valid:
            self.error_label.config(text=f"⚠️ {clean_name}")
            self.name_entry.focus_set()
            return

        raw_phone = self.phone_entry.get()
        phone_valid, clean_phone = validate_phone(raw_phone)
        if not phone_valid:
            self.error_label.config(text=f"⚠️ {clean_phone}")
            self.phone_entry.focus_set()
            return

        raw_email = self.email_entry.get()
        email_valid, clean_email = validate_email(raw_email)
        if not email_valid:
            self.error_label.config(text=f"⚠️ {clean_email}")
            self.email_entry.focus_set()
            return

        raw_bdate = self.birth_date_entry.get()
        bdate_valid, clean_bdate = parse_and_validate_birth_date(raw_bdate)
        if not bdate_valid:
            self.error_label.config(text=f"⚠️ {clean_bdate}")
            self.birth_date_entry.focus_set()
            return

        raw_insta = self.instagram_entry.get()
        insta_valid, clean_insta = validate_instagram(raw_insta)
        if not insta_valid:
            self.error_label.config(text=f"⚠️ {clean_insta}")
            self.instagram_entry.focus_set()
            return

        notes = self.notes_text.get("1.0", tk.END).strip()
        category = self.category_var.get() or "General"
        is_fav = self.is_favorite_var.get()

        if self.is_edit and self.contact:
            updated = Contact(
                id=self.contact.id,
                name=clean_name,
                phone=clean_phone,
                email=clean_email,
                birth_date=clean_bdate,
                instagram=clean_insta,
                category=category,
                is_favorite=is_fav,
                notes=notes,
                created_at=self.contact.created_at,
            )
        else:
            updated = Contact(
                name=clean_name,
                phone=clean_phone,
                email=clean_email,
                birth_date=clean_bdate,
                instagram=clean_insta,
                category=category,
                is_favorite=is_fav,
                notes=notes,
            )

        if self.on_save:
            self.on_save(updated)

        self.destroy()
