"""
Main Application Window for Bloom Habit Tracker.
Apple-style minimalist interface with Blush Pink / Midnight Rose palette,
interactive weekly calendar strip, circular progress ring, and routine filters.
"""

from datetime import date, datetime, timedelta
from typing import Optional
import customtkinter as ctk

from app.config import THEME, FONTS, APP_NAME
from app.models import Habit
from app.storage import HabitStore
from app.utils.graphics import create_circular_progress_image, create_mini_dot_image
from app.views.add_habit_modal import AddHabitModal
from app.views.habit_card import HabitCard
from app.views.stats_modal import StatsModal


class MainWindow(ctk.CTk):
    """
    Main Desktop Window presenting Apple-inspired habit tracker dashboard.
    """

    def __init__(self, store: Optional[HabitStore] = None):
        super().__init__()

        self.store = store or HabitStore()
        self.theme_mode = "light"  # "light" or "dark"
        self.theme = THEME[self.theme_mode]

        # Selected date for viewing / logging (defaults to today)
        self.selected_date = date.today()
        self.selected_filter = "All"  # All, Morning, Afternoon, Evening, Completed

        # Window Setup
        self.title(f"{APP_NAME}")
        self.geometry("780x860")
        self.minsize(680, 720)
        ctk.set_appearance_mode("Light")
        self.configure(fg_color=self.theme["bg_base"])

        # Habit card references
        self.card_widgets = []

        self._build_ui()
        self.refresh_dashboard()

    def _build_ui(self) -> None:
        """Constructs the application layout."""
        # Main container with breathing room padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=28, pady=24)

        # 1. Top Header Bar (Date, Title, Action Buttons)
        self._build_header(self.main_container)

        # 2. Week Calendar Strip (Apple Fitness / Calendar style)
        self._build_week_strip(self.main_container)

        # 3. Daily Momentum Ring Card
        self._build_progress_card(self.main_container)

        # 4. Routine Filter Tabs
        self._build_filter_bar(self.main_container)

        # 5. Scrollable Habit Cards Container
        self._build_habits_scroll_area(self.main_container)

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        self.header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 14))
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Left: Today's date and title
        titles_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        titles_frame.grid(row=0, column=0, sticky="w")

        today_str = date.today().strftime("%A, %B %-d").upper()
        self.lbl_date = ctk.CTkLabel(
            titles_frame,
            text=today_str,
            font=FONTS["caption_bold"],
            text_color=self.theme["primary_pink"],
            anchor="w",
        )
        self.lbl_date.pack(fill="x", anchor="w")

        self.lbl_greeting = ctk.CTkLabel(
            titles_frame,
            text="Today's Rituals",
            font=FONTS["title_large"],
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        self.lbl_greeting.pack(fill="x", anchor="w", pady=(2, 0))

        # Right: Action Buttons
        actions_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")

        # Theme Toggle Button
        theme_icon = "🌙" if self.theme_mode == "light" else "☀️"
        self.btn_theme = ctk.CTkButton(
            actions_frame,
            text=theme_icon,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_primary"],
            border_width=1,
            border_color=self.theme["card_border"],
            font=("Apple Color Emoji", 14) if "Apple Color Emoji" else ("Helvetica Neue", 13),
            command=self._toggle_theme,
        )
        self.btn_theme.pack(side="left", padx=(0, 8))

        # Insights Button
        self.btn_stats = ctk.CTkButton(
            actions_frame,
            text="📊 Insights",
            width=90,
            height=36,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_primary"],
            border_width=1,
            border_color=self.theme["card_border"],
            font=FONTS["body_bold"],
            command=self._open_stats_modal,
        )
        self.btn_stats.pack(side="left", padx=(0, 8))

        # Add Ritual Primary Button
        self.btn_add = ctk.CTkButton(
            actions_frame,
            text="+ New Habit",
            height=36,
            corner_radius=18,
            fg_color=self.theme["primary_pink"],
            hover_color=self.theme["primary_hover"],
            text_color="#FFFFFF",
            font=FONTS["body_bold"],
            command=self._open_add_modal,
        )
        self.btn_add.pack(side="left")

    def _build_week_strip(self, parent: ctk.CTkFrame) -> None:
        """Constructs Apple Fitness style 7-day strip."""
        self.week_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.week_container.pack(fill="x", pady=(0, 16))

        # Header with optional Jump to Today button
        strip_header = ctk.CTkFrame(self.week_container, fg_color="transparent")
        strip_header.pack(fill="x", pady=(0, 8))

        self.lbl_viewing = ctk.CTkLabel(
            strip_header,
            text="THIS WEEK",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
        )
        self.lbl_viewing.pack(side="left")

        self.btn_today_jump = ctk.CTkButton(
            strip_header,
            text="Jump to Today",
            width=80,
            height=22,
            corner_radius=11,
            fg_color=self.theme["soft_pink"],
            hover_color=self.theme["soft_pink_hover"],
            text_color=self.theme["primary_pink"],
            font=FONTS["caption_bold"],
            command=self._jump_to_today,
        )
        # Only packed when viewing a date other than today

        # The 7 Day Buttons Row
        self.days_strip_frame = ctk.CTkFrame(
            self.week_container,
            fg_color=self.theme["card_bg"],
            corner_radius=18,
            border_width=1,
            border_color=self.theme["card_border"],
            height=70,
        )
        self.days_strip_frame.pack(fill="x")
        for i in range(7):
            self.days_strip_frame.grid_columnconfigure(i, weight=1)

        self.day_buttons = []

    def _render_week_strip_buttons(self) -> None:
        """Populates the 7-day week strip."""
        for w in self.day_buttons:
            w.destroy()
        self.day_buttons.clear()

        # Compute Monday to Sunday of the current week (or window containing selected date)
        today = date.today()
        # Find start of the week (Monday)
        start_of_week = self.selected_date - timedelta(days=self.selected_date.weekday())

        for idx in range(7):
            d = start_of_week + timedelta(days=idx)
            is_selected = (d == self.selected_date)
            is_today = (d == today)
            iso = d.isoformat()

            # Check completion status on this day
            done_count = sum(1 for h in self.store.habits if h.is_completed(iso))
            total_count = len(self.store.habits)

            day_cell = ctk.CTkFrame(
                self.days_strip_frame,
                fg_color=self.theme["primary_pink"] if is_selected else "transparent",
                corner_radius=14,
                cursor="pointinghand",
            )
            day_cell.grid(row=0, column=idx, padx=4, pady=6, sticky="nsew")

            # Day Abbreviation (e.g. MON)
            lbl_name = ctk.CTkLabel(
                day_cell,
                text=d.strftime("%a")[:3].upper(),
                font=FONTS["caption_bold"],
                text_color="#FFFFFF" if is_selected else self.theme["text_secondary"],
            )
            lbl_name.pack(pady=(6, 1))

            # Day Number (e.g. 28)
            lbl_num = ctk.CTkLabel(
                day_cell,
                text=str(d.day),
                font=FONTS["body_bold"],
                text_color="#FFFFFF" if is_selected else self.theme["text_primary"],
            )
            lbl_num.pack(pady=(0, 2))

            # Indicator dot underneath
            if total_count > 0 and done_count == total_count:
                dot_status = "completed"
            elif done_count > 0:
                dot_status = "today_pending"
            else:
                dot_status = "missed"

            dot_color = "#FFFFFF" if is_selected else self.theme["primary_pink"]
            dot_img = create_mini_dot_image(
                status=dot_status,
                size=8,
                primary_color=dot_color,
                muted_color=self.theme["divider"] if not is_selected else "#FFFFFF88",
            )
            lbl_dot = ctk.CTkLabel(day_cell, image=dot_img, text="")
            lbl_dot.pack(pady=(0, 4))

            # Bind clicks to select date
            def make_handler(target_d):
                return lambda e: self._select_date(target_d)

            handler = make_handler(d)
            day_cell.bind("<Button-1>", handler)
            lbl_name.bind("<Button-1>", handler)
            lbl_num.bind("<Button-1>", handler)
            lbl_dot.bind("<Button-1>", handler)

            self.day_buttons.append(day_cell)

        # Update Jump to Today button visibility
        if self.selected_date != today:
            self.btn_today_jump.pack(side="right")
        else:
            self.btn_today_jump.pack_forget()

    def _build_progress_card(self, parent: ctk.CTkFrame) -> None:
        """Builds the hero progress ring card."""
        self.progress_card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=20,
            border_width=1,
            border_color=self.theme["card_border"],
            height=130,
        )
        self.progress_card.pack(fill="x", pady=(0, 16))
        self.progress_card.grid_columnconfigure(1, weight=1)

        # Left: Circular Ring graphic
        self.ring_container = ctk.CTkFrame(self.progress_card, fg_color="transparent", width=120, height=120)
        self.ring_container.grid(row=0, column=0, padx=16, pady=12, sticky="w")
        self.ring_container.grid_propagate(False)

        self.lbl_ring_img = ctk.CTkLabel(self.ring_container, text="")
        self.lbl_ring_img.place(relx=0.5, rely=0.5, anchor="center")

        # Center text inside the ring (Percentage and counts)
        self.lbl_ring_pct = ctk.CTkLabel(
            self.ring_container,
            text="0%",
            font=("Helvetica Neue", 16, "bold"),
            text_color=self.theme["text_primary"],
        )
        self.lbl_ring_pct.place(relx=0.5, rely=0.42, anchor="center")

        self.lbl_ring_sub = ctk.CTkLabel(
            self.ring_container,
            text="0 of 0",
            font=FONTS["subscript"],
            text_color=self.theme["text_secondary"],
        )
        self.lbl_ring_sub.place(relx=0.5, rely=0.60, anchor="center")

        # Right: Progress text and streak momentum
        info_frame = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(0, 16), pady=16, sticky="nsew")

        self.lbl_momentum_title = ctk.CTkLabel(
            info_frame,
            text="Today's Momentum",
            font=FONTS["title_small"],
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        self.lbl_momentum_title.pack(fill="x", anchor="w")

        self.lbl_momentum_sub = ctk.CTkLabel(
            info_frame,
            text="Small daily habits compound into extraordinary results.",
            font=FONTS["body"],
            text_color=self.theme["text_secondary"],
            anchor="w",
            wraplength=480,
            justify="left",
        )
        self.lbl_momentum_sub.pack(fill="x", anchor="w", pady=(4, 8))

        # Overall streak pill row
        stats_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        stats_row.pack(fill="x", anchor="w")

        self.lbl_hero_streak = ctk.CTkLabel(
            stats_row,
            text="🔥 Best Streak: 0 days",
            font=FONTS["caption_bold"],
            text_color=self.theme["streak_badge_text"],
            fg_color=self.theme["streak_badge_bg"],
            corner_radius=10,
            height=22,
        )
        self.lbl_hero_streak.pack(side="left", padx=(0, 8))

        self.lbl_hero_total = ctk.CTkLabel(
            stats_row,
            text="✨ 0 Completed",
            font=FONTS["caption"],
            text_color=self.theme["text_secondary"],
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            height=22,
        )
        self.lbl_hero_total.pack(side="left")

    def _build_filter_bar(self, parent: ctk.CTkFrame) -> None:
        """Routine segmented filter tabs."""
        filter_row = ctk.CTkFrame(parent, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 12))

        filter_options = ["All", "Morning", "Afternoon", "Evening", "Completed"]
        self.filter_var = ctk.StringVar(value="All")

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_row,
            values=filter_options,
            variable=self.filter_var,
            corner_radius=14,
            selected_color=self.theme["primary_pink"],
            selected_hover_color=self.theme["primary_hover"],
            unselected_color=self.theme["card_bg"],
            unselected_hover_color=self.theme["soft_pink"],
            font=FONTS["body_bold"],
            height=34,
            command=self._on_filter_changed,
        )
        self.seg_filter.pack(side="left")

    def _build_habits_scroll_area(self, parent: ctk.CTkFrame) -> None:
        """Scrollable list of habit cards."""
        self.scroll_habits = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.theme["soft_pink"],
            scrollbar_button_hover_color=self.theme["primary_pink"],
        )
        self.scroll_habits.pack(fill="both", expand=True)

        # Empty state container
        self.empty_frame = ctk.CTkFrame(self.scroll_habits, fg_color="transparent")

    def refresh_dashboard(self) -> None:
        """Re-computes stats and refreshes all visual components."""
        iso_date = self.selected_date.isoformat()
        is_today = (self.selected_date == date.today())

        # Update Greeting label
        if is_today:
            self.lbl_greeting.configure(text="Today's Rituals")
        else:
            formatted_date = self.selected_date.strftime("%A, %b %-d")
            self.lbl_greeting.configure(text=f"Rituals for {formatted_date}")

        # Update Stats for selected date
        daily_stats = self.store.get_stats_for_date(iso_date)
        total = daily_stats["total"]
        completed = daily_stats["completed"]
        pct = daily_stats["percentage"]

        # Render Circular Progress Ring
        ring_img = create_circular_progress_image(
            percentage=pct,
            size=110,
            stroke_width=9,
            bg_color=self.theme["ring_bg"],
            progress_color=self.theme["ring_progress"],
        )
        self.lbl_ring_img.configure(image=ring_img)
        self.lbl_ring_pct.configure(text=f"{int(pct)}%")
        self.lbl_ring_sub.configure(text=f"{completed} of {total}")

        # Momentum message
        if total == 0:
            msg = "No habits added yet. Tap '+ New Habit' above to create your first ritual!"
        elif pct == 100.0:
            msg = "All rituals completed! You are flourishing today. Keep blooming! 🌸"
        elif pct >= 50.0:
            msg = f"Over halfway there! {completed} rituals done, {total - completed} left to bloom. ✨"
        elif pct > 0.0:
            msg = "A mindful start to your day. One intentional step at a time. 💧"
        else:
            msg = "A fresh canvas awaits. Begin your first ritual of the day. 🌿"
        self.lbl_momentum_sub.configure(text=msg)

        # Overall streak & totals
        overall = self.store.get_overall_stats()
        self.lbl_hero_streak.configure(text=f" 🔥 Best Streak: {overall['best_streak']} days ")
        self.lbl_hero_total.configure(text=f" ✨ {overall['total_completions']} Total Check-ins ")

        # Update Week Strip Buttons
        self._render_week_strip_buttons()

        # Render Habit Cards
        self._render_habit_cards()

    def _render_habit_cards(self) -> None:
        """Renders the filtered list of habit cards."""
        # Clear existing cards
        for card in self.card_widgets:
            card.destroy()
        self.card_widgets.clear()
        self.empty_frame.pack_forget()

        iso_date = self.selected_date.isoformat()
        current_filter = self.filter_var.get()

        # Filter habits
        filtered = []
        for h in self.store.habits:
            if current_filter == "All":
                filtered.append(h)
            elif current_filter == "Completed":
                if h.is_completed(iso_date):
                    filtered.append(h)
            elif h.routine == current_filter:
                filtered.append(h)

        if not filtered:
            self._show_empty_state(current_filter)
            return

        for habit in filtered:
            card = HabitCard(
                self.scroll_habits,
                habit=habit,
                target_date=iso_date,
                theme_mode=self.theme_mode,
                on_toggle=self._on_habit_toggled,
                on_edit=self._on_habit_edit,
                on_delete=self._on_habit_delete,
            )
            card.pack(fill="x", pady=6)
            self.card_widgets.append(card)

    def _show_empty_state(self, current_filter: str) -> None:
        """Displays a clean minimalist empty state."""
        for w in self.empty_frame.winfo_children():
            w.destroy()

        self.empty_frame.pack(fill="both", expand=True, pady=40)

        icon_char = "🌸" if current_filter == "All" else "✨"
        lbl_icon = ctk.CTkLabel(
            self.empty_frame,
            text=icon_char,
            font=("Apple Color Emoji", 36) if "Apple Color Emoji" else ("Helvetica Neue", 32),
        )
        lbl_icon.pack(pady=(20, 8))

        if current_filter == "Completed":
            empty_title = "No rituals completed yet"
            empty_desc = "Check off habits as you finish them to see them flourish here."
        elif current_filter == "All":
            empty_title = "No rituals created yet"
            empty_desc = "Tap '+ New Habit' in the top right to start building your routine."
        else:
            empty_title = f"No {current_filter.lower()} rituals"
            empty_desc = f"Tap '+ New Habit' and assign the routine to {current_filter}."

        lbl_t = ctk.CTkLabel(
            self.empty_frame,
            text=empty_title,
            font=FONTS["title_small"],
            text_color=self.theme["text_primary"],
        )
        lbl_t.pack()

        lbl_d = ctk.CTkLabel(
            self.empty_frame,
            text=empty_desc,
            font=FONTS["caption"],
            text_color=self.theme["text_secondary"],
        )
        lbl_d.pack(pady=(4, 20))

    def _on_habit_toggled(self, habit: Habit, new_status: bool) -> None:
        """Fires when any habit checkmark is toggled."""
        self.store.save()
        self.refresh_dashboard()

    def _on_habit_edit(self, habit: Habit) -> None:
        """Opens modal to edit an existing habit."""
        modal = AddHabitModal(
            self,
            habit=habit,
            theme_mode=self.theme_mode,
            on_save=self._save_edited_habit,
        )

    def _save_edited_habit(self, habit: Habit) -> None:
        self.store.update_habit(habit)
        self.refresh_dashboard()

    def _on_habit_delete(self, habit: Habit) -> None:
        """Deletes habit from store."""
        self.store.delete_habit(habit.id)
        self.refresh_dashboard()

    def _open_add_modal(self) -> None:
        """Opens modal to create a new habit."""
        modal = AddHabitModal(
            self,
            theme_mode=self.theme_mode,
            on_save=self._add_new_habit,
        )

    def _add_new_habit(self, habit: Habit) -> None:
        self.store.add_habit(habit)
        self.refresh_dashboard()

    def _open_stats_modal(self) -> None:
        """Opens the analytics and insights sheet."""
        modal = StatsModal(
            self,
            store=self.store,
            theme_mode=self.theme_mode,
        )

    def _select_date(self, target_date: date) -> None:
        """Switches the active viewing date."""
        self.selected_date = target_date
        self.refresh_dashboard()

    def _jump_to_today(self) -> None:
        """Jumps directly back to today."""
        self.selected_date = date.today()
        self.refresh_dashboard()

    def _on_filter_changed(self, value: str) -> None:
        """Switches active routine filter."""
        self._render_habit_cards()

    def _toggle_theme(self) -> None:
        """Toggles between Blush Light and Midnight Rose themes."""
        if self.theme_mode == "light":
            self.theme_mode = "dark"
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="☀️")
        else:
            self.theme_mode = "light"
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="🌙")

        self.theme = THEME[self.theme_mode]
        self.configure(fg_color=self.theme["bg_base"])

        # Re-apply theme colors to containers
        self.days_strip_frame.configure(
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
        )
        self.progress_card.configure(
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
        )
        self.btn_theme.configure(
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_primary"],
            border_color=self.theme["card_border"],
        )
        self.btn_stats.configure(
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_primary"],
            border_color=self.theme["card_border"],
        )
        self.btn_today_jump.configure(
            fg_color=self.theme["soft_pink"],
            hover_color=self.theme["soft_pink_hover"],
            text_color=self.theme["primary_pink"],
        )
        self.lbl_ring_pct.configure(text_color=self.theme["text_primary"])
        self.lbl_ring_sub.configure(text_color=self.theme["text_secondary"])
        self.lbl_greeting.configure(text_color=self.theme["text_primary"])
        self.lbl_momentum_title.configure(text_color=self.theme["text_primary"])
        self.lbl_momentum_sub.configure(text_color=self.theme["text_secondary"])

        self.refresh_dashboard()
