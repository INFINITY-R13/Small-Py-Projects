"""
Apple Health-inspired Analytics and Insights Sheet.
Visualizes consistency trends, weekly bar chart, streak highlights,
and minimalist habit performance breakdown.
"""

from datetime import date
import random
from typing import Optional
import customtkinter as ctk
from app.config import THEME, FONTS, AESTHETIC_QUOTES
from app.storage import HabitStore
from app.utils.graphics import create_vertical_progress_bar_image


class StatsModal(ctk.CTkToplevel):
    """
    Analytics sheet displaying weekly visual bar chart, streak records,
    and habit adherence statistics.
    """

    def __init__(
        self,
        master,
        store: HabitStore,
        theme_mode: str = "light",
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.store = store
        self.theme_mode = theme_mode
        self.theme = THEME[theme_mode]

        self.title("Habit Insights & Momentum")
        self.geometry("540x660")
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_base"])

        self.transient(master)
        self.grab_set()

        self._build_ui()
        self._center_window(master)

    def _center_window(self, master) -> None:
        self.update_idletasks()
        try:
            mx = master.winfo_x()
            my = master.winfo_y()
            mw = master.winfo_width()
            mh = master.winfo_height()

            w = 540
            h = 660
            x = mx + (mw - w) // 2
            y = my + (mh - h) // 2
            self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        stats = self.store.get_overall_stats()

        # Scrollable container for smooth viewing
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.theme["soft_pink"],
            scrollbar_button_hover_color=self.theme["primary_pink"],
        )
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        # Header Title
        lbl_title = ctk.CTkLabel(
            scroll,
            text="Consistency & Insights",
            font=FONTS["title_medium"],
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        lbl_title.pack(fill="x", anchor="w")

        lbl_sub = ctk.CTkLabel(
            scroll,
            text="Your journey of continuous daily growth.",
            font=FONTS["caption"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        lbl_sub.pack(fill="x", anchor="w", pady=(2, 16))

        # 1. Metric Summary Cards (3 cards side by side)
        metrics_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 16))
        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

        metric_data = [
            ("🔥 Active Streak", f"{stats['current_max_streak']} days", self.theme["streak_badge_text"]),
            ("🏆 Best Record", f"{stats['best_streak']} days", self.theme["primary_pink"]),
            ("✨ Completed", f"{stats['total_completions']} times", self.theme["text_primary"]),
        ]

        for idx, (label, val, val_color) in enumerate(metric_data):
            card = ctk.CTkFrame(
                metrics_frame,
                fg_color=self.theme["card_bg"],
                corner_radius=14,
                border_width=1,
                border_color=self.theme["card_border"],
                height=84,
            )
            card.grid(row=0, column=idx, padx=4 if idx == 1 else 0, sticky="ew")
            card.grid_propagate(False)

            lbl_m_label = ctk.CTkLabel(
                card,
                text=label,
                font=FONTS["caption_bold"],
                text_color=self.theme["text_secondary"],
            )
            lbl_m_label.pack(pady=(12, 2))

            lbl_m_val = ctk.CTkLabel(
                card,
                text=val,
                font=FONTS["title_small"],
                text_color=val_color,
            )
            lbl_m_val.pack()

        # 2. 7-Day Activity Heatmap / Bar Chart (Apple Activity Style)
        chart_card = ctk.CTkFrame(
            scroll,
            fg_color=self.theme["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=self.theme["card_border"],
        )
        chart_card.pack(fill="x", pady=(0, 16), padx=2)

        chart_header = ctk.CTkLabel(
            chart_card,
            text="WEEKLY COMPLETION PATTERN",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        chart_header.pack(fill="x", padx=16, pady=(14, 10))

        bars_frame = ctk.CTkFrame(chart_card, fg_color="transparent")
        bars_frame.pack(fill="x", padx=12, pady=(0, 14))
        for col_idx in range(7):
            bars_frame.grid_columnconfigure(col_idx, weight=1)

        week_data = stats.get("week_summary", [])
        for col_idx, item in enumerate(week_data):
            rate = item["rate"]
            day_frame = ctk.CTkFrame(bars_frame, fg_color="transparent")
            day_frame.grid(row=0, column=col_idx, padx=2)

            bar_img = create_vertical_progress_bar_image(
                percentage=rate,
                width=22,
                height=72,
                active_color=self.theme["primary_pink"],
                track_color=self.theme["ring_bg"],
            )

            lbl_bar = ctk.CTkLabel(day_frame, image=bar_img, text="")
            lbl_bar.pack(pady=(0, 4))

            lbl_day = ctk.CTkLabel(
                day_frame,
                text=item["day_name"],
                font=FONTS["caption_bold"],
                text_color=self.theme["text_primary"] if item["date"] == date.today() else self.theme["text_secondary"],
            )
            lbl_day.pack()

            lbl_pct = ctk.CTkLabel(
                day_frame,
                text=f"{int(rate)}%",
                font=FONTS["subscript"],
                text_color=self.theme["text_tertiary"],
            )
            lbl_pct.pack()

        # 3. Habit Adherence Breakdown (30-day score)
        habits_card = ctk.CTkFrame(
            scroll,
            fg_color=self.theme["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=self.theme["card_border"],
        )
        habits_card.pack(fill="x", pady=(0, 16), padx=2)

        habits_header = ctk.CTkLabel(
            habits_card,
            text="HABIT ADHERENCE (PAST 30 DAYS)",
            font=FONTS["caption_bold"],
            text_color=self.theme["text_secondary"],
            anchor="w",
        )
        habits_header.pack(fill="x", padx=16, pady=(14, 8))

        for habit in self.store.habits:
            row = ctk.CTkFrame(habits_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            row.grid_columnconfigure(1, weight=1)

            # Emoji
            lbl_e = ctk.CTkLabel(
                row,
                text=habit.emoji,
                font=("Apple Color Emoji", 16) if "Apple Color Emoji" else ("Helvetica Neue", 14),
                width=24,
            )
            lbl_e.grid(row=0, column=0, sticky="w", padx=(0, 8))

            # Name
            lbl_n = ctk.CTkLabel(
                row,
                text=habit.name,
                font=FONTS["body"],
                text_color=self.theme["text_primary"],
                anchor="w",
            )
            lbl_n.grid(row=0, column=1, sticky="w")

            # Rate
            adherence = habit.get_completion_rate(30)
            lbl_rate = ctk.CTkLabel(
                row,
                text=f"{adherence:.0f}%",
                font=FONTS["body_bold"],
                text_color=self.theme["primary_pink"],
                width=45,
                anchor="e",
            )
            lbl_rate.grid(row=0, column=2, sticky="e")

        # Bottom space inside habits card
        ctk.CTkFrame(habits_card, fg_color="transparent", height=8).pack()

        # 4. Mindful Quote Card
        quote_text, quote_author = random.choice(AESTHETIC_QUOTES)
        quote_card = ctk.CTkFrame(
            scroll,
            fg_color=self.theme["soft_pink"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["soft_pink_border"],
        )
        quote_card.pack(fill="x", pady=(0, 18), padx=2)

        lbl_q = ctk.CTkLabel(
            quote_card,
            text=f'"{quote_text}"',
            font=("Helvetica Neue", 12, "italic"),
            text_color=self.theme["text_primary"],
            wraplength=440,
            justify="center",
        )
        lbl_q.pack(padx=16, pady=(12, 4))

        lbl_auth = ctk.CTkLabel(
            quote_card,
            text=f"— {quote_author}",
            font=FONTS["caption_bold"],
            text_color=self.theme["primary_pink"],
        )
        lbl_auth.pack(pady=(0, 10))

        # Close button
        btn_close = ctk.CTkButton(
            scroll,
            text="Done",
            height=40,
            corner_radius=12,
            fg_color=self.theme["primary_pink"],
            hover_color=self.theme["primary_hover"],
            text_color="#FFFFFF",
            font=FONTS["body_bold"],
            command=self.destroy,
        )
        btn_close.pack(fill="x", pady=(0, 12))
