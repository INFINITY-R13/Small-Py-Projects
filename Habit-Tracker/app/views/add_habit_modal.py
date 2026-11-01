"""
Apple-style Modal Sheet for Creating or Editing a Habit.
Minimalist layout with emoji selector, routine segmented buttons, and clean inputs.
"""

from typing import Callable, Optional
import customtkinter as ctk
from app.config import THEME, FONTS, CURATED_EMOJIS, ROUTINES, CATEGORIES, FREQUENCIES
from app.models import Habit


class AddHabitModal(ctk.CTkToplevel):
    """
    A sleek modal dialog to add or edit habit definitions.
    """

    def __init__(
        self,
        master,
        habit: Optional[Habit] = None,
        theme_mode: str = "light",
        on_save: Optional[Callable[[Habit], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.habit = habit
        self.is_edit = habit is not None
        self.theme_mode = theme_mode
        self.theme = THEME[theme_mode]
        self.on_save = on_save

        # Window settings
        title_text = "Edit Ritual" if self.is_edit else "New Ritual"
        self.title(title_text)
        self.geometry("480x620")
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_base"])

        # Modal behavior
        self.transient(master)
        self.grab_set()

        # State variables
        default_emoji = habit.emoji if habit else "🌸"
        self.selected_emoji = ctk.StringVar(value=default_emoji)
        self.selected_routine = ctk.StringVar(value=habit.routine if habit else "Anytime")
        self.selected_category = ctk.StringVar(value=habit.category if habit else "Wellness")
        self.selected_frequency = ctk.StringVar(value=habit.frequency if habit else "Every Day")

        self._build_ui()
        self._center_window(master)

    def _center_window(self, master) -> None:
        """Centers modal window over the master window."""
        self.update_idletasks()
        try:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            master_w = master.winfo_width()
            master_h = master.winfo_height()

            w = 480
            h = 620
            x = master_x + (master_w - w) // 2
            y = master_y + (master_h - h) // 2
            self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=28, pady=24)

        # Header Title & Subtitle
        header_text = "Edit Habit" if self.is_edit else "New Ritual"
        lbl_header = ctk.CTkLabel(
            main_frame,
            text=header_text,
            font=FONTS["title_medium"],
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        lbl_header.pack(fill="x", anchor="w")

        lbl_sub = ctk.CTkLabel(
            main_frame,
            text="Build consistency with intention and mindful rhythm.",
            font=FONTS["caption"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_sub.pack(fill="x", anchor="w", pady=(2, 18))

        # 1. Habit Name Entry
        lbl_name = ctk.CTkLabel(
            main_frame,
            text="HABIT NAME",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_name.pack(fill="x", anchor="w", pady=(0, 4))

        self.entry_name = ctk.CTkEntry(
            main_frame,
            placeholder_text="e.g. 15-min Morning Sunlight, Drink Matcha",
            height=42,
            corner_radius=12,
            border_width=1,
            border_color=self.theme["card_border"],
            fg_color=self.theme["card_bg"],
            text_color=self.theme["text_primary"],
            font=FONTS["body"],
        )
        if self.habit:
            self.entry_name.insert(0, self.habit.name)
        self.entry_name.pack(fill="x", pady=(0, 16))

        # 2. Icon / Emoji Selector
        lbl_emoji = ctk.CTkLabel(
            main_frame,
            text="CHOOSE ICON",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_emoji.pack(fill="x", anchor="w", pady=(0, 6))

        emoji_card = ctk.CTkFrame(
            main_frame,
            fg_color=self.theme["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["card_border"],
            height=100,
        )
        emoji_card.pack(fill="x", pady=(0, 16))

        # Grid of curated emojis
        self.emoji_buttons = []
        for idx, (emoji_char, label) in enumerate(CURATED_EMOJIS[:14]):
            row = idx // 7
            col = idx % 7
            is_active = (emoji_char == self.selected_emoji.get())

            btn = ctk.CTkButton(
                emoji_card,
                text=emoji_char,
                width=36,
                height=36,
                corner_radius=10,
                font=("Apple Color Emoji", 18) if "Apple Color Emoji" else ("Helvetica Neue", 16),
                fg_color=self.theme["primary_pink"] if is_active else "transparent",
                hover_color=self.theme["soft_pink"],
                command=lambda e=emoji_char: self._select_emoji(e),
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.emoji_buttons.append((emoji_char, btn))

        # Custom emoji inline entry
        custom_row = ctk.CTkFrame(emoji_card, fg_color="transparent")
        custom_row.grid(row=2, column=0, columnspan=7, pady=(4, 6))
        lbl_custom = ctk.CTkLabel(
            custom_row,
            text="Custom emoji / icon: ",
            font=FONTS["caption"],
            text_color=self.theme["text_tertiary"],
        )
        lbl_custom.pack(side="left")
        self.entry_custom_emoji = ctk.CTkEntry(
            custom_row,
            width=50,
            height=28,
            corner_radius=8,
            fg_color=self.theme["bg_secondary"],
            border_width=0,
            justify="center",
        )
        self.entry_custom_emoji.pack(side="left", padx=4)
        btn_apply_custom = ctk.CTkButton(
            custom_row,
            text="Set",
            width=36,
            height=28,
            corner_radius=8,
            fg_color=self.theme["soft_pink"],
            hover_color=self.theme["soft_pink_hover"],
            text_color=self.theme["primary_pink"],
            font=FONTS["caption_bold"],
            command=self._apply_custom_emoji,
        )
        btn_apply_custom.pack(side="left")

        # 3. Routine Selector (Time of day)
        lbl_routine = ctk.CTkLabel(
            main_frame,
            text="TIME OF DAY / ROUTINE",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_routine.pack(fill="x", anchor="w", pady=(0, 4))

        self.seg_routine = ctk.CTkSegmentedButton(
            main_frame,
            values=ROUTINES,
            variable=self.selected_routine,
            corner_radius=12,
            selected_color=self.theme["primary_pink"],
            selected_hover_color=self.theme["primary_hover"],
            unselected_color=self.theme["card_bg"],
            unselected_hover_color=self.theme["soft_pink"],
            font=FONTS["body"],
            height=36,
        )
        self.seg_routine.pack(fill="x", pady=(0, 16))

        # 4. Category & Frequency Dropdowns
        dropdown_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        dropdown_row.pack(fill="x", pady=(0, 20))
        dropdown_row.grid_columnconfigure(0, weight=1)
        dropdown_row.grid_columnconfigure(1, weight=1)

        # Category
        cat_box = ctk.CTkFrame(dropdown_row, fg_color="transparent")
        cat_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        lbl_cat = ctk.CTkLabel(
            cat_box,
            text="CATEGORY",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_cat.pack(fill="x", anchor="w", pady=(0, 4))

        self.opt_category = ctk.CTkOptionMenu(
            cat_box,
            values=CATEGORIES,
            variable=self.selected_category,
            corner_radius=12,
            fg_color=self.theme["card_bg"],
            button_color=self.theme["soft_pink"],
            button_hover_color=self.theme["soft_pink_hover"],
            text_color=self.theme["text_primary"],
            dropdown_fg_color=self.theme["card_bg"],
            dropdown_text_color=self.theme["text_primary"],
            dropdown_hover_color=self.theme["soft_pink"],
            font=FONTS["body"],
            height=36,
        )
        self.opt_category.pack(fill="x")

        # Frequency
        freq_box = ctk.CTkFrame(dropdown_row, fg_color="transparent")
        freq_box.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        lbl_freq = ctk.CTkLabel(
            freq_box,
            text="FREQUENCY",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_freq.pack(fill="x", anchor="w", pady=(0, 4))

        self.opt_frequency = ctk.CTkOptionMenu(
            freq_box,
            values=FREQUENCIES,
            variable=self.selected_frequency,
            corner_radius=12,
            fg_color=self.theme["card_bg"],
            button_color=self.theme["soft_pink"],
            button_hover_color=self.theme["soft_pink_hover"],
            text_color=self.theme["text_primary"],
            dropdown_fg_color=self.theme["card_bg"],
            dropdown_text_color=self.theme["text_primary"],
            dropdown_hover_color=self.theme["soft_pink"],
            font=FONTS["body"],
            height=36,
        )
        self.opt_frequency.pack(fill="x")

        # Validation error message label
        self.lbl_error = ctk.CTkLabel(
            main_frame,
            text="",
            font=FONTS["caption_bold"],
            text_color=self.theme["primary_pink"],
        )
        self.lbl_error.pack(fill="x", pady=(0, 8))

        # 5. Bottom Buttons (Cancel & Save)
        btn_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")

        btn_cancel = ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=100,
            height=40,
            corner_radius=12,
            fg_color=self.theme["bg_secondary"],
            hover_color=self.theme["soft_pink"],
            text_color=self.theme["text_secondary"],
            font=FONTS["body_bold"],
            command=self.destroy,
        )
        btn_cancel.pack(side="left")

        save_btn_text = "Save Changes" if self.is_edit else "Create Ritual"
        btn_save = ctk.CTkButton(
            btn_row,
            text=save_btn_text,
            height=40,
            corner_radius=12,
            fg_color=self.theme["primary_pink"],
            hover_color=self.theme["primary_hover"],
            text_color="#FFFFFF",
            font=FONTS["body_bold"],
            command=self._handle_save,
        )
        btn_save.pack(side="right", fill="x", expand=True, padx=(12, 0))

    def _select_emoji(self, emoji_char: str) -> None:
        self.selected_emoji.set(emoji_char)
        for char, btn in self.emoji_buttons:
            if char == emoji_char:
                btn.configure(fg_color=self.theme["primary_pink"])
            else:
                btn.configure(fg_color="transparent")

    def _apply_custom_emoji(self) -> None:
        custom = self.entry_custom_emoji.get().strip()
        if custom:
            self.selected_emoji.set(custom)
            for _, btn in self.emoji_buttons:
                btn.configure(fg_color="transparent")
            self.lbl_error.configure(text=f"Selected icon: {custom}")

    def _handle_save(self) -> None:
        name = self.entry_name.get().strip()
        if not name:
            self.lbl_error.configure(text="Please enter a habit name.")
            return

        if self.is_edit and self.habit:
            self.habit.name = name
            self.habit.emoji = self.selected_emoji.get()
            self.habit.routine = self.selected_routine.get()
            self.habit.category = self.selected_category.get()
            self.habit.frequency = self.selected_frequency.get()
            target_habit = self.habit
        else:
            target_habit = Habit(
                name=name,
                emoji=self.selected_emoji.get(),
                routine=self.selected_routine.get(),
                category=self.selected_category.get(),
                frequency=self.selected_frequency.get(),
            )

        if self.on_save:
            self.on_save(target_habit)

        self.destroy()
