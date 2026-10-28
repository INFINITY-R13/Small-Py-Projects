"""
Main Window for the Contact Book Application.
Provides a modern two-pane master-detail interface with live search,
filters, quick actions, and birthday reminders.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from datetime import date
from typing import Optional, List

from database import Database
from models import Contact
from ui.theme import (
    BG_APP,
    BG_SIDEBAR,
    BG_SURFACE,
    BG_SURFACE_HOVER,
    BG_SELECTED,
    BORDER_COLOR,
    BORDER_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    TEXT_LINK,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_PRIMARY_TEXT,
    ACCENT_STAR,
    ACCENT_STAR_BG,
    ACCENT_INSTA,
    ACCENT_INSTA_BG,
    BADGE_BG_DEFAULT,
    BADGE_TEXT_DEFAULT,
    BADGE_BG_BIRTHDAY,
    BADGE_TEXT_BIRTHDAY,
    DANGER_COLOR,
    DANGER_BG,
    DANGER_HOVER,
    SUCCESS_COLOR,
    SUCCESS_BG,
    FONT_TITLE,
    FONT_BOLD,
    FONT_SUBTITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_AVATAR_LARGE,
)
from ui.components import AvatarCanvas, ModernButton, Toast
from ui.contact_dialog import ContactDialog
from utils.exporters import (
    export_contacts_to_csv,
    export_contacts_to_json,
    import_contacts_from_csv,
    import_contacts_from_json,
)


class MainWindow(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.selected_contact: Optional[Contact] = None
        self.active_contacts: List[Contact] = []

        # Filter and Sort State
        self.current_filter = "all"  # "all", "favorites", "birthdays_soon"
        self.current_category = "all"
        self.current_sort = "name_asc"

        # Window Setup
        self.title("Contact Book")
        self.geometry("1060x680")
        self.minsize(860, 560)
        self.config(bg=BG_APP)

        self._build_header()
        self._build_main_content()
        self._bind_shortcuts()

        # Initial Load
        self.refresh_contact_list()

    def _build_header(self):
        """Top action bar with Branding, Search input, and Quick Actions."""
        header_frame = tk.Frame(self, bg=BG_SURFACE, padx=20, pady=12)
        header_frame.pack(fill=tk.X)

        # Brand / Logo
        brand_frame = tk.Frame(header_frame, bg=BG_SURFACE)
        brand_frame.pack(side=tk.LEFT)

        lbl_logo = tk.Label(
            brand_frame,
            text="📒 Contact Book",
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            font=FONT_TITLE,
        )
        lbl_logo.pack(side=tk.LEFT)

        # Search Bar (Center)
        search_container = tk.Frame(header_frame, bg=BG_SURFACE)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=30)

        search_box = tk.Frame(search_container, bg=BORDER_COLOR, padx=1, pady=1)
        search_box.pack(fill=tk.X)

        search_inner = tk.Frame(search_box, bg=BG_SURFACE)
        search_inner.pack(fill=tk.X)

        lbl_search_icon = tk.Label(
            search_inner,
            text="🔍",
            bg=BG_SURFACE,
            fg=TEXT_MUTED,
            font=FONT_SMALL,
            padx=8,
        )
        lbl_search_icon.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_change())

        self.search_entry = tk.Entry(
            search_inner,
            textvariable=self.search_var,
            font=FONT_BODY,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            bd=0,
            relief=tk.FLAT,
            insertbackground=TEXT_PRIMARY,
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        # Clear search button
        self.btn_clear_search = tk.Label(
            search_inner,
            text="✕",
            bg=BG_SURFACE,
            fg=TEXT_MUTED,
            font=FONT_SMALL,
            cursor="pointinghand",
            padx=8,
        )
        self.btn_clear_search.pack(side=tk.RIGHT)
        self.btn_clear_search.bind("<Button-1>", lambda e: self.search_var.set(""))

        # Right Action Buttons
        actions_frame = tk.Frame(header_frame, bg=BG_SURFACE)
        actions_frame.pack(side=tk.RIGHT)

        # Backup / Export Dropdown Menu
        self.btn_more = ModernButton(
            actions_frame,
            text="⇅ Backup / Data",
            command=self._show_data_menu,
            bg="#F1F5F9",
            fg=TEXT_PRIMARY,
            hover_bg="#E2E8F0",
            font=FONT_BODY_BOLD,
            padx=12,
            pady=6,
        )
        self.btn_more.pack(side=tk.LEFT, padx=(0, 8))

        # + Add Contact Button
        btn_add = ModernButton(
            actions_frame,
            text="➕ New Contact",
            command=self.open_new_contact_dialog,
            bg=ACCENT_PRIMARY,
            fg=ACCENT_PRIMARY_TEXT,
            hover_bg=ACCENT_PRIMARY_HOVER,
            font=FONT_BODY_BOLD,
            padx=16,
            pady=6,
        )
        btn_add.pack(side=tk.LEFT)

        # Bottom subtle separator
        tk.Frame(self, bg=BORDER_COLOR, height=1).pack(fill=tk.X)

    def _build_main_content(self):
        """Split view: Left Sidebar (List) & Right Surface (Details)."""
        content_container = tk.Frame(self, bg=BG_APP)
        content_container.pack(fill=tk.BOTH, expand=True)

        # ==========================================================
        # LEFT SIDEBAR
        # ==========================================================
        self.sidebar_frame = tk.Frame(content_container, bg=BG_SIDEBAR, width=380)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # Filter Tabs (All / Favorites / Birthdays)
        tabs_frame = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR, padx=12, pady=10)
        tabs_frame.pack(fill=tk.X)

        self.tab_buttons = {}
        for key, label in [("all", "All"), ("favorites", "⭐ Favs"), ("birthdays_soon", "🎂 Birthdays")]:
            btn = tk.Label(
                tabs_frame,
                text=label,
                bg="#E2E8F0" if key == "all" else BG_SIDEBAR,
                fg=TEXT_PRIMARY,
                font=FONT_BODY_BOLD,
                padx=10,
                pady=5,
                cursor="pointinghand",
                relief=tk.FLAT,
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            btn.bind("<Button-1>", lambda e, k=key: self._set_filter(k))
            self.tab_buttons[key] = btn

        # Category and Sort Row
        filter_meta_row = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR, padx=14, pady=4)
        filter_meta_row.pack(fill=tk.X)

        # Category
        tk.Label(filter_meta_row, text="Group:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY, font=FONT_SMALL).pack(side=tk.LEFT)
        self.cat_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(
            filter_meta_row,
            textvariable=self.cat_var,
            values=["All"] + self.db.get_all_categories(),
            state="readonly",
            width=10,
            font=FONT_SMALL,
        )
        self.cat_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self._on_category_select())

        # Sort
        tk.Label(filter_meta_row, text="Sort:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY, font=FONT_SMALL).pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="Name (A-Z)")
        self.sort_combo = ttk.Combobox(
            filter_meta_row,
            textvariable=self.sort_var,
            values=["Name (A-Z)", "Name (Z-A)", "Recently Added", "Upcoming Birthday"],
            state="readonly",
            width=13,
            font=FONT_SMALL,
        )
        self.sort_combo.pack(side=tk.LEFT, padx=(4, 0))
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self._on_sort_select())

        # Divider
        tk.Frame(self.sidebar_frame, bg=BORDER_COLOR, height=1).pack(fill=tk.X, pady=(6, 0))

        # Scrollable Contact Cards List
        list_container = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.list_canvas = tk.Canvas(list_container, bg=BG_SIDEBAR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.scrollable_list_frame = tk.Frame(self.list_canvas, bg=BG_SIDEBAR)

        self.scrollable_list_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")),
        )

        self.canvas_window = self.list_canvas.create_window((0, 0), window=self.scrollable_list_frame, anchor="nw")

        self.list_canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)
        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_canvas.bind("<Configure>", self._on_list_canvas_configure)

        # Mousewheel scroll support
        self.list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Sidebar Footer / Status
        self.sidebar_footer = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR, padx=14, pady=8)
        self.sidebar_footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(self.sidebar_frame, bg=BORDER_COLOR, height=1).pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_stats = tk.Label(
            self.sidebar_footer,
            text="",
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            font=FONT_SMALL,
        )
        self.lbl_stats.pack(side=tk.LEFT)

        # Vertical Divider
        tk.Frame(content_container, bg=BORDER_COLOR, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ==========================================================
        # RIGHT DETAIL PANEL
        # ==========================================================
        self.detail_frame = tk.Frame(content_container, bg=BG_SURFACE)
        self.detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._show_empty_detail_view()

    def _on_list_canvas_configure(self, event):
        self.list_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Support macOS delta and Windows/Linux delta
        if hasattr(event, "delta") and event.delta:
            delta = int(-1 * (event.delta / 120)) if abs(event.delta) >= 120 else int(-1 * event.delta)
            self.list_canvas.yview_scroll(delta, "units")

    # -------------------------------------------------------------
    # DETAIL PANEL RENDERING
    # -------------------------------------------------------------
    def _show_empty_detail_view(self):
        """Displays when no contact is selected."""
        for w in self.detail_frame.winfo_children():
            w.destroy()

        empty_box = tk.Frame(self.detail_frame, bg=BG_SURFACE)
        empty_box.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        lbl_icon = tk.Label(empty_box, text="👤", font=("Helvetica Neue", 52), bg=BG_SURFACE, fg=TEXT_MUTED)
        lbl_icon.pack(pady=(0, 10))

        lbl_msg = tk.Label(
            empty_box,
            text="No Contact Selected",
            font=FONT_TITLE,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
        )
        lbl_msg.pack(pady=(0, 6))

        lbl_sub = tk.Label(
            empty_box,
            text="Select a contact from the list or add a new one to view details.",
            font=FONT_BODY,
            bg=BG_SURFACE,
            fg=TEXT_SECONDARY,
        )
        lbl_sub.pack(pady=(0, 18))

        btn_add = ModernButton(
            empty_box,
            text="➕ Create Contact",
            command=self.open_new_contact_dialog,
            bg=ACCENT_PRIMARY,
            fg=ACCENT_PRIMARY_TEXT,
            hover_bg=ACCENT_PRIMARY_HOVER,
            font=FONT_BODY_BOLD,
            padx=18,
            pady=8,
        )
        btn_add.pack()

    def _render_contact_details(self, contact: Contact):
        """Render the complete contact card with light grey theme aesthetics."""
        for w in self.detail_frame.winfo_children():
            w.destroy()

        # Main scrollable canvas for details in case window is resized small
        canvas = tk.Canvas(self.detail_frame, bg=BG_SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_SURFACE, padx=36, pady=28)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        cw = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))

        # --- Top Header: Avatar, Name, Favorite Star, Actions ---
        header = tk.Frame(scrollable_frame, bg=BG_SURFACE)
        header.pack(fill=tk.X, pady=(0, 20))

        # Avatar
        bg_col, fg_col = contact.avatar_theme
        avatar = AvatarCanvas(
            header,
            initials=contact.initials,
            bg_color=bg_col,
            text_color=fg_col,
            size=72,
            font_size=24,
        )
        avatar.pack(side=tk.LEFT, padx=(0, 18))

        # Name & Category Info
        info_col = tk.Frame(header, bg=BG_SURFACE)
        info_col.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        name_row = tk.Frame(info_col, bg=BG_SURFACE)
        name_row.pack(anchor="w")

        lbl_name = tk.Label(
            name_row,
            text=contact.name,
            font=("Helvetica Neue", 22, "bold"),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
        )
        lbl_name.pack(side=tk.LEFT, padx=(0, 8))

        # Favorite star toggle button
        star_icon = "★" if contact.is_favorite else "☆"
        star_color = ACCENT_STAR if contact.is_favorite else TEXT_MUTED
        btn_fav = tk.Label(
            name_row,
            text=star_icon,
            font=("Helvetica Neue", 20),
            bg=BG_SURFACE,
            fg=star_color,
            cursor="pointinghand",
        )
        btn_fav.pack(side=tk.LEFT)
        btn_fav.bind("<Button-1>", lambda e: self._toggle_favorite_for(contact))

        # Category pill badge
        cat_badge = tk.Frame(info_col, bg=BADGE_BG_DEFAULT, padx=10, pady=3)
        cat_badge.pack(anchor="w", pady=(6, 0))
        tk.Label(
            cat_badge,
            text=contact.category or "General",
            bg=BADGE_BG_DEFAULT,
            fg=BADGE_TEXT_DEFAULT,
            font=FONT_SMALL,
        ).pack()

        # Top Right Actions: Edit & Delete
        actions_col = tk.Frame(header, bg=BG_SURFACE)
        actions_col.pack(side=tk.RIGHT, anchor="ne")

        btn_edit = ModernButton(
            actions_col,
            text="✏️ Edit",
            command=lambda: self.open_edit_contact_dialog(contact),
            bg="#F1F5F9",
            fg=TEXT_PRIMARY,
            hover_bg="#E2E8F0",
            font=FONT_BODY_BOLD,
            padx=14,
            pady=6,
        )
        btn_edit.pack(side=tk.LEFT, padx=(0, 8))

        btn_delete = ModernButton(
            actions_col,
            text="🗑️ Delete",
            command=lambda: self._confirm_delete(contact),
            bg=DANGER_BG,
            fg=DANGER_COLOR,
            hover_bg="#FCA5A5",
            font=FONT_BODY_BOLD,
            padx=14,
            pady=6,
        )
        btn_delete.pack(side=tk.LEFT)

        # --- Quick Action Buttons Row ---
        quick_actions = tk.Frame(scrollable_frame, bg=BG_SURFACE)
        quick_actions.pack(fill=tk.X, pady=(0, 22))

        if contact.phone:
            btn_call = ModernButton(
                quick_actions,
                text="📞 Copy Phone",
                command=lambda: self._copy_to_clipboard(contact.phone, "Phone copied to clipboard!"),
                bg="#F8FAFC",
                fg=TEXT_PRIMARY,
                border_color=BORDER_COLOR,
                hover_bg="#F1F5F9",
                font=FONT_SMALL,
                padx=12,
                pady=6,
            )
            btn_call.pack(side=tk.LEFT, padx=(0, 8))

        if contact.email:
            btn_mail = ModernButton(
                quick_actions,
                text="✉️ Send Email",
                command=lambda: self._open_email_client(contact.email),
                bg="#F8FAFC",
                fg=TEXT_PRIMARY,
                border_color=BORDER_COLOR,
                hover_bg="#F1F5F9",
                font=FONT_SMALL,
                padx=12,
                pady=6,
            )
            btn_mail.pack(side=tk.LEFT, padx=(0, 8))

        if contact.clean_instagram:
            btn_insta = ModernButton(
                quick_actions,
                text=f"📸 @{contact.clean_instagram}",
                command=lambda: self._open_instagram(contact),
                bg=ACCENT_INSTA_BG,
                fg=ACCENT_INSTA,
                hover_bg="#FCE7F3",
                font=FONT_SMALL,
                padx=12,
                pady=6,
            )
            btn_insta.pack(side=tk.LEFT, padx=(0, 8))

        btn_share = ModernButton(
            quick_actions,
            text="📋 Copy Card Info",
            command=lambda: self._copy_contact_card(contact),
            bg="#F8FAFC",
            fg=TEXT_PRIMARY,
            border_color=BORDER_COLOR,
            hover_bg="#F1F5F9",
            font=FONT_SMALL,
            padx=12,
            pady=6,
        )
        btn_share.pack(side=tk.LEFT)

        # --- Birthday Reminder Card (if birth date is set) ---
        bday_info = contact.get_birthday_details()
        if bday_info["has_birthday"]:
            bday_card = tk.Frame(
                scrollable_frame,
                bg=BADGE_BG_BIRTHDAY if bday_info["is_soon"] else "#F8FAFC",
                padx=16,
                pady=14,
                highlightbackground=BORDER_COLOR,
                highlightthickness=1,
            )
            bday_card.pack(fill=tk.X, pady=(0, 20))

            bday_icon = tk.Label(
                bday_card,
                text="🎂",
                font=("Helvetica Neue", 24),
                bg=bday_card.cget("bg"),
            )
            bday_icon.pack(side=tk.LEFT, padx=(0, 14))

            bday_text_frame = tk.Frame(bday_card, bg=bday_card.cget("bg"))
            bday_text_frame.pack(side=tk.LEFT, fill=tk.Y)

            lbl_bday_title = tk.Label(
                bday_text_frame,
                text=bday_info["summary"],
                font=FONT_BOLD,
                bg=bday_card.cget("bg"),
                fg=BADGE_TEXT_BIRTHDAY if bday_info["is_soon"] else TEXT_PRIMARY,
            )
            lbl_bday_title.pack(anchor="w")

            lbl_bday_date = tk.Label(
                bday_text_frame,
                text=f"Born {bday_info['formatted_date']} • Current age: {bday_info['current_age']}",
                font=FONT_SMALL,
                bg=bday_card.cget("bg"),
                fg=TEXT_SECONDARY,
            )
            lbl_bday_date.pack(anchor="w", pady=(2, 0))

        # --- Information Sections Grid ---
        info_card = tk.Frame(scrollable_frame, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        info_card.pack(fill=tk.X, pady=(0, 20))

        def make_info_row(icon: str, label_text: str, value_text: str, action_cb=None, action_label="Copy"):
            row = tk.Frame(info_card, bg=BG_SURFACE, padx=16, pady=12)
            row.pack(fill=tk.X)

            icon_lbl = tk.Label(row, text=icon, font=("Helvetica Neue", 16), bg=BG_SURFACE)
            icon_lbl.pack(side=tk.LEFT, padx=(0, 12))

            text_frame = tk.Frame(row, bg=BG_SURFACE)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            lbl_h = tk.Label(text_frame, text=label_text, font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_SURFACE)
            lbl_h.pack(anchor="w")

            val_display = value_text if value_text else "Not specified"
            val_color = TEXT_PRIMARY if value_text else TEXT_MUTED

            lbl_v = tk.Label(text_frame, text=val_display, font=FONT_BODY_BOLD, fg=val_color, bg=BG_SURFACE)
            lbl_v.pack(anchor="w", pady=(1, 0))

            if action_cb and value_text:
                btn_action = tk.Label(
                    row,
                    text=action_label,
                    font=FONT_SMALL,
                    bg="#F1F5F9",
                    fg=TEXT_SECONDARY,
                    padx=10,
                    pady=4,
                    cursor="pointinghand",
                )
                btn_action.pack(side=tk.RIGHT)
                btn_action.bind("<Button-1>", lambda e: action_cb())

            # Separator inside card
            tk.Frame(info_card, bg=BORDER_COLOR, height=1).pack(fill=tk.X)

        make_info_row(
            "📞",
            "Phone Number",
            contact.phone,
            action_cb=lambda: self._copy_to_clipboard(contact.phone, "Phone copied!"),
            action_label="Copy",
        )
        make_info_row(
            "✉️",
            "Email Address",
            contact.email,
            action_cb=lambda: self._copy_to_clipboard(contact.email, "Email copied!"),
            action_label="Copy",
        )
        make_info_row(
            "📸",
            "Instagram Handle",
            (f"@{contact.clean_instagram}" if contact.clean_instagram else ""),
            action_cb=(lambda: self._open_instagram(contact)) if contact.clean_instagram else None,
            action_label="Open Profile ↗",
        )
        make_info_row(
            "🎂",
            "Birth Date",
            contact.birth_date if contact.birth_date else "",
        )

        # --- Notes Section ---
        if contact.notes:
            notes_card = tk.Frame(
                scrollable_frame,
                bg="#F8FAFC",
                padx=16,
                pady=14,
                highlightbackground=BORDER_COLOR,
                highlightthickness=1,
            )
            notes_card.pack(fill=tk.X, pady=(0, 20))

            tk.Label(
                notes_card,
                text="📝 Notes & Bio",
                font=FONT_BOLD,
                bg="#F8FAFC",
                fg=TEXT_PRIMARY,
            ).pack(anchor="w", pady=(0, 6))

            tk.Label(
                notes_card,
                text=contact.notes,
                font=FONT_BODY,
                bg="#F8FAFC",
                fg=TEXT_SECONDARY,
                justify=tk.LEFT,
                wraplength=520,
            ).pack(anchor="w")

        # --- Metadata Timestamps ---
        meta_frame = tk.Frame(scrollable_frame, bg=BG_SURFACE)
        meta_frame.pack(fill=tk.X, pady=(0, 10))

        ts_text = ""
        if contact.created_at:
            ts_text += f"Added on {contact.created_at}"
        if contact.updated_at and contact.updated_at != contact.created_at:
            ts_text += f" • Updated {contact.updated_at}"

        if ts_text:
            tk.Label(meta_frame, text=ts_text, font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")

    # -------------------------------------------------------------
    # CONTACT LIST POPULATION
    # -------------------------------------------------------------
    def refresh_contact_list(self):
        """Query contacts according to current search, filter, and sort, then redraw sidebar list."""
        search = self.search_var.get()
        self.active_contacts = self.db.get_all(
            search_query=search,
            filter_by=self.current_filter,
            category_filter=self.current_category,
            sort_by=self.current_sort,
        )

        # Clear existing rows in sidebar list
        for child in self.scrollable_list_frame.winfo_children():
            child.destroy()

        # Update stats
        counts = self.db.get_counts()
        self.lbl_stats.config(
            text=f"{len(self.active_contacts)} contacts shown • {counts['total']} total"
        )
        self.tab_buttons["all"].config(text=f"All ({counts['total']})")
        self.tab_buttons["favorites"].config(text=f"⭐ Favs ({counts['favorites']})")
        self.tab_buttons["birthdays_soon"].config(text=f"🎂 Birthdays ({counts['birthdays_soon']})")

        if not self.active_contacts:
            empty_item = tk.Frame(self.scrollable_list_frame, bg=BG_SIDEBAR, pady=40)
            empty_item.pack(fill=tk.X)
            tk.Label(
                empty_item,
                text="No contacts found",
                bg=BG_SIDEBAR,
                fg=TEXT_MUTED,
                font=FONT_BODY_BOLD,
            ).pack()
            if search:
                tk.Label(
                    empty_item,
                    text=f"No results matching \"{search}\"",
                    bg=BG_SIDEBAR,
                    fg=TEXT_MUTED,
                    font=FONT_SMALL,
                ).pack(pady=(4, 0))
            if not self.selected_contact or (self.selected_contact not in self.active_contacts):
                self._show_empty_detail_view()
            return

        # Render list items
        for contact in self.active_contacts:
            self._render_list_item(contact)

        # If previous selected contact still exists, keep it selected, else select first
        if self.selected_contact:
            match = next((c for c in self.active_contacts if c.id == self.selected_contact.id), None)
            if match:
                self.selected_contact = match
                self._render_contact_details(match)
            else:
                self.selected_contact = self.active_contacts[0]
                self._render_contact_details(self.active_contacts[0])
        else:
            self.selected_contact = self.active_contacts[0]
            self._render_contact_details(self.active_contacts[0])

    def _render_list_item(self, contact: Contact):
        """Render a single modern card row in the sidebar list."""
        is_selected = self.selected_contact and (self.selected_contact.id == contact.id)
        row_bg = BG_SELECTED if is_selected else BG_SIDEBAR

        row = tk.Frame(self.scrollable_list_frame, bg=row_bg, padx=12, pady=9, cursor="pointinghand")
        row.pack(fill=tk.X, pady=1)

        # Avatar
        bg_col, fg_col = contact.avatar_theme
        avatar = AvatarCanvas(
            row,
            initials=contact.initials,
            bg_color=bg_col,
            text_color=fg_col,
            size=38,
            font_size=12,
        )
        avatar.pack(side=tk.LEFT, padx=(0, 10))

        # Text information column
        text_col = tk.Frame(row, bg=row_bg)
        text_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Name and upcoming birthday icon
        top_line = tk.Frame(text_col, bg=row_bg)
        top_line.pack(fill=tk.X)

        lbl_name = tk.Label(
            top_line,
            text=contact.name,
            font=FONT_BODY_BOLD,
            bg=row_bg,
            fg=TEXT_PRIMARY,
            anchor="w",
        )
        lbl_name.pack(side=tk.LEFT)

        bday = contact.get_birthday_details()
        if bday["is_soon"]:
            lbl_bday_badge = tk.Label(
                top_line,
                text=f"🎂 {bday['badge']}",
                font=("Helvetica Neue", 9, "bold"),
                bg=BADGE_BG_BIRTHDAY,
                fg=BADGE_TEXT_BIRTHDAY,
                padx=4,
                pady=1,
            )
            lbl_bday_badge.pack(side=tk.LEFT, padx=(6, 0))

        # Secondary line: Phone / Category
        sub_text = contact.phone if contact.phone else (contact.email or f"@{contact.clean_instagram}")
        if not sub_text:
            sub_text = contact.category or "Contact"

        lbl_sub = tk.Label(
            text_col,
            text=sub_text,
            font=FONT_SMALL,
            bg=row_bg,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        lbl_sub.pack(fill=tk.X, pady=(2, 0))

        # Star favorite icon on right
        star_icon = "★" if contact.is_favorite else "☆"
        star_color = ACCENT_STAR if contact.is_favorite else TEXT_MUTED
        lbl_star = tk.Label(
            row,
            text=star_icon,
            font=("Helvetica Neue", 16),
            bg=row_bg,
            fg=star_color,
            cursor="pointinghand",
            padx=4,
        )
        lbl_star.pack(side=tk.RIGHT)
        lbl_star.bind("<Button-1>", lambda e, c=contact: self._toggle_favorite_for(c))

        # Hover & Click events
        def on_enter(_):
            if not (self.selected_contact and self.selected_contact.id == contact.id):
                for w in (row, text_col, top_line, lbl_name, lbl_sub, lbl_star):
                    w.config(bg=BG_SURFACE_HOVER)

        def on_leave(_):
            if not (self.selected_contact and self.selected_contact.id == contact.id):
                for w in (row, text_col, top_line, lbl_name, lbl_sub, lbl_star):
                    w.config(bg=BG_SIDEBAR)

        def on_select(_):
            self.selected_contact = contact
            self.refresh_contact_list()
            self._render_contact_details(contact)

        for w in (row, text_col, top_line, lbl_name, lbl_sub, avatar):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_select)

    # -------------------------------------------------------------
    # ACTIONS & EVENT HANDLERS
    # -------------------------------------------------------------
    def _on_search_change(self):
        query = self.search_var.get().strip()
        self.btn_clear_search.config(text="✕" if query else "")
        self.refresh_contact_list()

    def _set_filter(self, filter_name: str):
        self.current_filter = filter_name
        for k, btn in self.tab_buttons.items():
            btn.config(bg="#E2E8F0" if k == filter_name else BG_SIDEBAR)
        self.refresh_contact_list()

    def _on_category_select(self):
        cat = self.cat_var.get()
        self.current_category = "all" if cat == "All" else cat
        self.refresh_contact_list()

    def _on_sort_select(self):
        choice = self.sort_var.get()
        if choice == "Name (A-Z)":
            self.current_sort = "name_asc"
        elif choice == "Name (Z-A)":
            self.current_sort = "name_desc"
        elif choice == "Recently Added":
            self.current_sort = "recent"
        elif choice == "Upcoming Birthday":
            self.current_sort = "birthday"
        self.refresh_contact_list()

    def _toggle_favorite_for(self, contact: Contact):
        self.db.toggle_favorite(contact.id)
        # Refresh current contact info
        updated = self.db.get_by_id(contact.id)
        if updated:
            contact.is_favorite = updated.is_favorite
        self.refresh_contact_list()
        Toast.show(self, "Contact updated!", is_success=True)

    def _confirm_delete(self, contact: Contact):
        answer = messagebox.askyesno(
            "Delete Contact",
            f"Are you sure you want to delete '{contact.name}'?\nThis action cannot be undone.",
            icon="warning",
            parent=self,
        )
        if answer:
            self.db.delete_contact(contact.id)
            self.selected_contact = None
            self.refresh_contact_list()
            Toast.show(self, f"Deleted '{contact.name}'", is_success=True)

    def open_new_contact_dialog(self):
        def on_save(new_c: Contact):
            new_id = self.db.add_contact(new_c)
            new_c.id = new_id
            self.selected_contact = new_c
            # Refresh categories list in dropdown
            self.cat_combo.config(values=["All"] + self.db.get_all_categories())
            self.refresh_contact_list()
            Toast.show(self, f"Added '{new_c.name}'!", is_success=True)

        ContactDialog(self, contact=None, on_save=on_save)

    def open_edit_contact_dialog(self, contact: Contact):
        def on_save(updated_c: Contact):
            self.db.update_contact(updated_c)
            self.selected_contact = updated_c
            self.cat_combo.config(values=["All"] + self.db.get_all_categories())
            self.refresh_contact_list()
            self._render_contact_details(updated_c)
            Toast.show(self, f"Updated '{updated_c.name}'!", is_success=True)

        ContactDialog(self, contact=contact, on_save=on_save)

    def _copy_to_clipboard(self, text: str, toast_msg: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        Toast.show(self, toast_msg, is_success=True)

    def _copy_contact_card(self, contact: Contact):
        card_text = f"Name: {contact.name}\n"
        if contact.phone:
            card_text += f"Phone: {contact.phone}\n"
        if contact.email:
            card_text += f"Email: {contact.email}\n"
        if contact.clean_instagram:
            card_text += f"Instagram: @{contact.clean_instagram}\n"
        if contact.birth_date:
            card_text += f"Birth Date: {contact.birth_date}\n"
        if contact.notes:
            card_text += f"Notes: {contact.notes}\n"

        self._copy_to_clipboard(card_text.strip(), "Full contact card copied!")

    def _open_email_client(self, email: str):
        try:
            webbrowser.open(f"mailto:{email}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch email client: {str(e)}", parent=self)

    def _open_instagram(self, contact: Contact):
        url = contact.instagram_url
        if url:
            try:
                webbrowser.open(url)
                Toast.show(self, f"Opening @{contact.clean_instagram} on Instagram...", is_success=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {str(e)}", parent=self)

    # -------------------------------------------------------------
    # IMPORT / EXPORT MENU
    # -------------------------------------------------------------
    def _show_data_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="📤 Export Contacts to CSV...", command=self._export_csv)
        menu.add_command(label="📤 Export Contacts to JSON...", command=self._export_json)
        menu.add_separator()
        menu.add_command(label="📥 Import Contacts from CSV...", command=self._import_csv)
        menu.add_command(label="📥 Import Contacts from JSON...", command=self._import_json)

        # Calculate position under the Backup button
        x = self.btn_more.winfo_rootx()
        y = self.btn_more.winfo_rooty() + self.btn_more.winfo_height()
        menu.post(x, y)

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Contacts as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="contacts_backup.csv",
        )
        if not filepath:
            return
        contacts = self.db.get_all()
        ok, msg = export_contacts_to_csv(contacts, filepath)
        if ok:
            Toast.show(self, msg, is_success=True)
        else:
            messagebox.showerror("Export Failed", msg, parent=self)

    def _export_json(self):
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Contacts as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="contacts_backup.json",
        )
        if not filepath:
            return
        contacts = self.db.get_all()
        ok, msg = export_contacts_to_json(contacts, filepath)
        if ok:
            Toast.show(self, msg, is_success=True)
        else:
            messagebox.showerror("Export Failed", msg, parent=self)

    def _import_csv(self):
        filepath = filedialog.askopenfilename(
            parent=self,
            title="Import Contacts from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not filepath:
            return
        ok, contacts, msg = import_contacts_from_csv(filepath)
        if not ok:
            messagebox.showerror("Import Failed", msg, parent=self)
            return

        added = 0
        for c in contacts:
            self.db.add_contact(c)
            added += 1

        self.refresh_contact_list()
        Toast.show(self, f"Imported {added} contacts successfully!", is_success=True)

    def _import_json(self):
        filepath = filedialog.askopenfilename(
            parent=self,
            title="Import Contacts from JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not filepath:
            return
        ok, contacts, msg = import_contacts_from_json(filepath)
        if not ok:
            messagebox.showerror("Import Failed", msg, parent=self)
            return

        added = 0
        for c in contacts:
            self.db.add_contact(c)
            added += 1

        self.refresh_contact_list()
        Toast.show(self, f"Imported {added} contacts successfully!", is_success=True)

    # -------------------------------------------------------------
    # SHORTCUTS
    # -------------------------------------------------------------
    def _bind_shortcuts(self):
        # Focus search: Cmd+F or Ctrl+F
        self.bind("<Command-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())

        # New contact: Cmd+N or Ctrl+N
        self.bind("<Command-n>", lambda e: self.open_new_contact_dialog())
        self.bind("<Control-n>", lambda e: self.open_new_contact_dialog())

        # Delete selected: Cmd+Backspace or Delete
        self.bind("<Command-BackSpace>", lambda e: self._delete_current_if_selected())

    def _delete_current_if_selected(self):
        if self.selected_contact:
            self._confirm_delete(self.selected_contact)
