"""
Apple-style Minimalist Habit Card Component.
Displays habit emoji badge, title, metadata pills, 7-day mini streak dots,
and interactive completion checkmark.
"""

from datetime import date, timedelta
from typing import Callable, Optional
import customtkinter as ctk
from app.config import THEME, FONTS
from app.models import Habit
from app.utils.graphics import create_check_button_image, create_mini_dot_image


class HabitCard(ctk.CTkFrame):
    """
    A minimalist card representing a single habit with quick check-off,
    visual streak counter, and recent adherence dots.
    """

    def __init__(
        self,
        master,
        habit: Habit,
        target_date: Optional[str] = None,
        theme_mode: str = "light",
        on_toggle: Optional[Callable[[Habit, bool], None]] = None,
        on_edit: Optional[Callable[[Habit], None]] = None,
        on_delete: Optional[Callable[[Habit], None]] = None,
        **kwargs
    ):
        self.habit = habit
        self.target_date = target_date or date.today().isoformat()
        self.theme_mode = theme_mode
        self.theme = THEME[theme_mode]
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        super().__init__(
            master,
            fg_color=self.theme["card_bg"],
            corner_radius=18,
            border_width=1,
            border_color=self.theme["card_border"],
            **kwargs
        )

        self._build_ui()

    def _build_ui(self) -> None:
        # Layout: Grid with 3 main sections:
        # Col 0: Emoji avatar box
        # Col 1: Habit details, metadata & mini dots
        # Col 2: Action buttons (edit, delete) & Check button
        self.grid_columnconfigure(1, weight=1)

        # 1. Emoji Container Box
        self.emoji_frame = ctk.CTkFrame(
            self,
            width=50,
            height=50,
            corner_radius=14,
            fg_color=self.theme["soft_pink"],
            border_width=0,
        )
        self.emoji_frame.grid(row=0, column=0, rowspan=2, padx=(16, 14), pady=16, sticky="nw")
        self.emoji_frame.grid_propagate(False)

        self.emoji_label = ctk.CTkLabel(
            self.emoji_frame,
            text=self.habit.emoji,
            font=("Apple Color Emoji", 24) if "Apple Color Emoji" else ("Helvetica Neue", 22),
            text_color=self.theme["text_primary"],
        )
        self.emoji_label.place(relx=0.5, rely=0.5, anchor="center")

        # 2. Main Content Frame (Title & Metadata)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, padx=(0, 10), pady=(14, 4), sticky="nsew")

        # Habit Title
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text=self.habit.name,
            font=FONTS["title_small"],
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        self.title_label.pack(fill="x", anchor="w")

        # Metadata Row (Category pill, Routine pill, Streak pill)
        self.meta_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.meta_frame.pack(fill="x", pady=(4, 6), anchor="w")

        # Category Pill
        self.cat_pill = ctk.CTkLabel(
            self.meta_frame,
            text=f"  {self.habit.category}  ",
            font=FONTS["caption"],
            text_color=self.theme["text_secondary"],
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            height=20,
        )
        self.cat_pill.pack(side="left", padx=(0, 6))

        # Routine Pill (if not Anytime)
        if self.habit.routine != "Anytime":
            routine_icons = {"Morning": "☀️", "Afternoon": "🌤️", "Evening": "🌙"}
            r_icon = routine_icons.get(self.habit.routine, "")
            self.routine_pill = ctk.CTkLabel(
                self.meta_frame,
                text=f"  {r_icon} {self.habit.routine}  ",
                font=FONTS["caption"],
                text_color=self.theme["text_secondary"],
                fg_color=self.theme["bg_secondary"],
                corner_radius=10,
                height=20,
            )
            self.routine_pill.pack(side="left", padx=(0, 6))

        # Streak Badge
        curr_streak, _ = self.habit.calculate_streaks()
        streak_text = f" 🔥 {curr_streak}d streak " if curr_streak > 0 else " ⚡️ New "
        self.streak_pill = ctk.CTkLabel(
            self.meta_frame,
            text=streak_text,
            font=FONTS["caption_bold"],
            text_color=self.theme["streak_badge_text"],
            fg_color=self.theme["streak_badge_bg"],
            corner_radius=10,
            height=20,
        )
        self.streak_pill.pack(side="left")

        # Mini 7-Day History Dots Row
        self.dots_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dots_frame.grid(row=1, column=1, padx=(0, 10), pady=(0, 14), sticky="w")

        today_obj = date.today()
        # Last 7 days
        recent_days = self.habit.get_recent_days(7, end_date=today_obj)

        for day_obj, is_done in recent_days:
            iso_str = day_obj.isoformat()
            if is_done:
                status = "completed"
            elif iso_str == today_obj.isoformat():
                status = "today_pending"
            else:
                status = "missed"

            dot_img = create_mini_dot_image(
                status=status,
                size=12,
                primary_color=self.theme["primary_pink"],
                muted_color=self.theme["divider"],
            )

            day_col = ctk.CTkFrame(self.dots_frame, fg_color="transparent")
            day_col.pack(side="left", padx=3)

            day_name = day_obj.strftime("%a")[0]  # First letter (M, T, W...)
            lbl_name = ctk.CTkLabel(
                day_col,
                text=day_name,
                font=FONTS["subscript"],
                text_color=self.theme["text_tertiary"],
                height=10,
            )
            lbl_name.pack(side="top")

            lbl_dot = ctk.CTkLabel(day_col, image=dot_img, text="")
            lbl_dot.pack(side="top", pady=(1, 0))

        # 3. Actions & Check Button Frame (Right side)
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=2, rowspan=2, padx=(8, 16), pady=14, sticky="e")

        # Secondary action buttons (Edit & Delete) - subtle icons
        self.btn_edit = ctk.CTkButton(
            self.actions_frame,
            text="✎",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_secondary"],
            font=("Helvetica Neue", 13),
            command=self._handle_edit,
        )
        self.btn_edit.pack(side="left", padx=(0, 4))

        self.btn_delete = ctk.CTkButton(
            self.actions_frame,
            text="✕",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_tertiary"],
            font=("Helvetica Neue", 12),
            command=self._handle_delete,
        )
        self.btn_delete.pack(side="left", padx=(0, 10))

        # Checkmark Toggle Button
        is_done_today = self.habit.is_completed(self.target_date)
        self.check_img = create_check_button_image(
            completed=is_done_today,
            size=36,
            primary_color=self.theme["primary_pink"],
            border_color=self.theme["soft_pink_border"],
        )

        self.btn_check = ctk.CTkButton(
            self.actions_frame,
            image=self.check_img,
            text="",
            width=38,
            height=38,
            corner_radius=19,
            fg_color="transparent",
            hover_color=self.theme["soft_pink"],
            command=self._handle_toggle,
        )
        self.btn_check.pack(side="left")

    def _handle_toggle(self) -> None:
        """Toggles habit completion and triggers callback."""
        new_state = self.habit.toggle(self.target_date)

        # Refresh check button visual
        new_img = create_check_button_image(
            completed=new_state,
            size=36,
            primary_color=self.theme["primary_pink"],
            border_color=self.theme["soft_pink_border"],
        )
        self.btn_check.configure(image=new_img)

        # Update streak pill
        curr_streak, _ = self.habit.calculate_streaks()
        streak_text = f" 🔥 {curr_streak}d streak " if curr_streak > 0 else " ⚡️ New "
        self.streak_pill.configure(text=streak_text)

        if self.on_toggle:
            self.on_toggle(self.habit, new_state)

    def _handle_edit(self) -> None:
        if self.on_edit:
            self.on_edit(self.habit)

    def _handle_delete(self) -> None:
        if self.on_delete:
            self.on_delete(self.habit)

    def set_target_date(self, new_date: str) -> None:
        """Update target date display if viewing past days."""
        self.target_date = new_date
        is_done = self.habit.is_completed(new_date)
        new_img = create_check_button_image(
            completed=is_done,
            size=36,
            primary_color=self.theme["primary_pink"],
            border_color=self.theme["soft_pink_border"],
        )
        self.btn_check.configure(image=new_img)
