"""A small, elegant desktop to-do list with Things 3 / Apple-inspired UI and JSON storage."""

from __future__ import annotations

import json
import shutil
import sys
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4

DATA_FILE = Path(__file__).with_name("tasks.json")


class FlatButton(tk.Label):
    """A cross-platform flat button that respects background, foreground,

    borders, and hover colors reliably on macOS, Windows, and Linux.
    Bypasses macOS Aqua's rigid native button rendering.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: callable | None = None,
        font: tuple[str, int, str] | tuple[str, int] = ("Helvetica", 10),
        bg: str = "#ffffff",
        fg: str = "#000000",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        active_bg: str | None = None,
        padx: int = 10,
        pady: int = 5,
        cursor: str = "hand2",
        state: str = "normal",
        highlightthickness: int = 0,
        highlightbackground: str = "#ffffff",
        relief: str = "flat",
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            font=font,
            bg=bg,
            fg=fg,
            padx=padx,
            pady=pady,
            cursor=cursor if state != "disabled" else "arrow",
            highlightthickness=highlightthickness,
            highlightbackground=highlightbackground,
            relief=relief,
            **kwargs,
        )
        self.command = command
        self._normal_bg = bg
        self._normal_fg = fg
        self._hover_bg = hover_bg or bg
        self._hover_fg = hover_fg or fg
        self._active_bg = active_bg or hover_bg or bg
        self._state = state

        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_command(self, command: callable) -> None:
        self.command = command

    def set_colors(
        self,
        bg: str,
        fg: str,
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        active_bg: str | None = None,
    ) -> None:
        self._normal_bg = bg
        self._normal_fg = fg
        self._hover_bg = hover_bg if hover_bg is not None else bg
        self._hover_fg = hover_fg if hover_fg is not None else fg
        self._active_bg = active_bg if active_bg is not None else self._hover_bg
        self.configure(bg=bg, fg=fg)

    def set_state(self, state: str, disabled_fg: str | None = None) -> None:
        self._state = state
        if state == "disabled":
            self.configure(cursor="arrow")
            if disabled_fg:
                self.configure(fg=disabled_fg)
        else:
            self.configure(cursor="hand2", fg=self._normal_fg)

    def _on_click(self, _event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self.configure(bg=self._active_bg)

    def _on_release(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self.configure(bg=self._normal_bg)
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            if self.command:
                self.command()

    def _on_enter(self, _event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self.configure(bg=self._hover_bg, fg=self._hover_fg)

    def _on_leave(self, _event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self.configure(bg=self._normal_bg, fg=self._normal_fg)


@dataclass(frozen=True)
class Theme:
    """Defines the color palette for the UI."""

    name: str
    bg: str
    card: str
    input_bg: str
    text: str
    text_secondary: str
    muted: str
    border: str
    accent: str
    accent_hover: str
    accent_text: str
    pill_track_bg: str
    pill_active_bg: str
    pill_active_fg: str
    pill_hover_bg: str
    danger: str
    disabled: str


LIGHT_THEME = Theme(
    name="light",
    bg="#fbfbfd",              # Apple airy off-white
    card="#ffffff",            # Pure white card
    input_bg="#f5f5f7",        # Apple system gray 6
    text="#1d1d1f",            # Apple SF primary text
    text_secondary="#48484a",  # Apple SF secondary text
    muted="#86868b",           # Apple SF tertiary / muted
    border="#e5e5ea",          # Apple hairline separator
    accent="#0071e3",          # Apple system blue
    accent_hover="#0077ed",
    accent_text="#ffffff",
    pill_track_bg="#f2f2f7",   # Segmented control capsule track
    pill_active_bg="#ffffff",  # Active pill
    pill_active_fg="#1d1d1f",  # Active pill text
    pill_hover_bg="#e5e5ea",   # Inactive pill hover
    danger="#ff3b30",          # Apple system red
    disabled="#c7c7cc",        # Apple disabled text
)

DARK_THEME = Theme(
    name="dark",
    bg="#161618",              # Dark slate canvas
    card="#212124",            # Elevated dark surface
    input_bg="#2c2c2e",        # Input field background
    text="#f5f5f7",            # Crisp light text
    text_secondary="#aeaeb2",  # Secondary text
    muted="#86868b",           # Muted text
    border="#323236",          # Subtle border
    accent="#2997ff",          # Apple dark mode blue
    accent_hover="#409cff",
    accent_text="#ffffff",
    pill_track_bg="#1c1c1e",   # Dark segmented control capsule track
    pill_active_bg="#3a3a3c",  # Active dark pill
    pill_active_fg="#ffffff",  # Active dark pill text
    pill_hover_bg="#2c2c2e",   # Inactive pill hover
    danger="#ff453a",          # Apple dark mode red
    disabled="#48484a",        # Disabled text
)


@dataclass
class Task:
    """Represents a single to-do item."""

    title: str
    id: str = field(default_factory=lambda: uuid4().hex)
    done: bool = False

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "title": self.title, "done": self.done}

    @classmethod
    def from_dict(cls, data: object) -> Task | None:
        if not isinstance(data, dict):
            return None
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return None
        task_id = str(data.get("id") or uuid4().hex)
        return cls(id=task_id, title=title.strip(), done=bool(data.get("done", False)))


class TodoApp:
    PLACEHOLDER_TEXT = "Add a to-do..."

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("To Do List")
        self.root.geometry("780x680")
        self.root.minsize(580, 500)

        self.theme: Theme = LIGHT_THEME
        self.tasks: list[Task] = []
        self.task_rows: list[tuple[tk.Label, tk.Frame]] = []
        self.status_text = tk.StringVar(value="Your to-dos are saved locally.")
        self.active_filter = "all"  # "all" | "active" | "completed"
        self._is_placeholder = True
        self._editing_task_id: str | None = None

        self._load_data()
        self._build_ui()
        self._apply_theme()
        self._render_tasks()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.shell = tk.Frame(self.root, padx=28, pady=24)
        self.shell.grid(row=0, column=0, sticky="nsew")
        self.shell.columnconfigure(0, weight=1)
        self.shell.rowconfigure(1, weight=1)

        # Header section
        self.header = tk.Frame(self.shell)
        self.header.grid(row=0, column=0, sticky="ew", pady=(4, 20))
        self.header.columnconfigure(0, weight=1)

        self.header_left = tk.Frame(self.header)
        self.header_left.grid(row=0, column=0, sticky="w")

        self.subtitle_label = tk.Label(
            self.header_left,
            text="THINGS TO DO",
            font=("Helvetica", 9, "bold"),
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 4))

        self.title_label = tk.Label(
            self.header_left,
            text="Today",
            font=("Helvetica", 28, "bold"),
        )
        self.title_label.pack(anchor="w")

        self.header_right = tk.Frame(self.header)
        self.header_right.grid(row=0, column=1, sticky="e")

        self.summary_label = tk.Label(
            self.header_right,
            text="",
            font=("Helvetica", 11),
        )
        self.summary_label.pack(side="left", padx=(0, 14))

        self.theme_btn = FlatButton(
            self.header_right,
            text="🌙 Dark",
            command=self.toggle_theme,
            font=("Helvetica", 9, "bold"),
            padx=11,
            pady=5,
        )
        self.theme_btn.pack(side="right")

        # Main Card container
        self.card = tk.Frame(self.shell, highlightthickness=1)
        self.card.grid(row=1, column=0, sticky="nsew")
        self.card.columnconfigure(0, weight=1)
        self.card.rowconfigure(2, weight=1)

        # Add task input area
        self.add_area = tk.Frame(self.card, padx=22, pady=18)
        self.add_area.grid(row=0, column=0, sticky="ew")
        self.add_area.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            self.add_area,
            font=("Helvetica", 12),
            relief="flat",
            bd=0,
            highlightthickness=1,
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=11, padx=(0, 12))
        self.entry.insert(0, self.PLACEHOLDER_TEXT)
        self.entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.entry.bind("<Return>", lambda _event: self.add_task())

        self.add_button = FlatButton(
            self.add_area,
            text="+ Add",
            command=self.add_task,
            font=("Helvetica", 11, "bold"),
            padx=18,
            pady=9,
        )
        self.add_button.grid(row=0, column=1, sticky="ew")

        # Divider between input and task list
        self.divider = tk.Frame(self.card, height=1)
        self.divider.grid(row=1, column=0, sticky="ew")

        # Task list area
        self.list_area = tk.Frame(self.card, padx=22, pady=16)
        self.list_area.grid(row=2, column=0, sticky="nsew")
        self.list_area.columnconfigure(0, weight=1)
        self.list_area.rowconfigure(1, weight=1)

        # List sub-header: Title, Filter Pills Capsule, and Clear Completed button
        self.list_header = tk.Frame(self.list_area)
        self.list_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.list_header.columnconfigure(1, weight=1)

        self.my_tasks_label = tk.Label(
            self.list_header,
            text="TASKS",
            font=("Helvetica", 9, "bold"),
        )
        self.my_tasks_label.grid(row=0, column=0, sticky="w", padx=(0, 14))

        # Filter buttons container (Apple-style Segmented Control Capsule)
        self.filters_capsule = tk.Frame(self.list_header, padx=2, pady=2)
        self.filters_capsule.grid(row=0, column=1, sticky="w")

        self.filter_buttons: dict[str, FlatButton] = {}
        for filter_key, filter_label in [("all", "All"), ("active", "Active"), ("completed", "Completed")]:
            btn = FlatButton(
                self.filters_capsule,
                text=filter_label,
                command=lambda k=filter_key: self.set_filter(k),
                font=("Helvetica", 9),
                padx=10,
                pady=3,
            )
            btn.pack(side="left", padx=1)
            self.filter_buttons[filter_key] = btn

        self.clear_button = FlatButton(
            self.list_header,
            text="Clear completed",
            command=self.clear_completed,
            font=("Helvetica", 10),
            padx=6,
            pady=3,
        )
        self.clear_button.grid(row=0, column=2, sticky="e")

        # Scrollable canvas for task rows
        self.list_frame = tk.Frame(self.list_area)
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.list_frame, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.rows_frame = tk.Frame(self.canvas)
        self.rows_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_rows)

        # Cross-platform mousewheel handling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        if not sys.platform.startswith("win") and sys.platform != "darwin":
            self.canvas.bind_all("<Button-4>", self._on_linux_scroll_up)
            self.canvas.bind_all("<Button-5>", self._on_linux_scroll_down)

        # Footer status text
        self.footer = tk.Frame(self.shell)
        self.footer.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self.status_label = tk.Label(
            self.footer,
            textvariable=self.status_text,
            font=("Helvetica", 9),
        )
        self.status_label.pack(anchor="w")

    # --- Theme Engine ---

    def toggle_theme(self) -> None:
        self.theme = DARK_THEME if self.theme.name == "light" else LIGHT_THEME
        self._apply_theme()
        self._render_tasks()
        self._save_data()

    def _apply_theme(self) -> None:
        t = self.theme
        self.root.configure(bg=t.bg)
        self.shell.configure(bg=t.bg)
        self.header.configure(bg=t.bg)
        self.header_left.configure(bg=t.bg)
        self.header_right.configure(bg=t.bg)
        self.title_label.configure(bg=t.bg, fg=t.text)
        self.subtitle_label.configure(bg=t.bg, fg=t.accent)
        self.summary_label.configure(bg=t.bg, fg=t.muted)

        self.theme_btn.configure(text="☀️ Light" if t.name == "dark" else "🌙 Dark")
        self.theme_btn.set_colors(
            bg=t.pill_track_bg,
            fg=t.text,
            hover_bg=t.pill_hover_bg,
            hover_fg=t.text,
        )

        self.card.configure(bg=t.card, highlightbackground=t.border)
        self.add_area.configure(bg=t.card)
        self.entry.configure(
            bg=t.input_bg,
            fg=t.muted if self._is_placeholder else t.text,
            insertbackground=t.text,
            highlightbackground=t.border,
            highlightcolor=t.accent,
        )
        self.add_button.set_colors(
            bg=t.accent,
            fg=t.accent_text,
            hover_bg=t.accent_hover,
            hover_fg=t.accent_text,
        )
        self.divider.configure(bg=t.border)
        self.list_area.configure(bg=t.card)
        self.list_header.configure(bg=t.card)
        self.my_tasks_label.configure(bg=t.card, fg=t.muted)
        self.filters_capsule.configure(bg=t.pill_track_bg)
        self._update_filter_buttons_style()
        self._update_clear_button_style()
        self.list_frame.configure(bg=t.card)
        self.canvas.configure(bg=t.card)
        self.rows_frame.configure(bg=t.card)
        self.footer.configure(bg=t.bg)
        self.status_label.configure(bg=t.bg, fg=t.muted)

    def _update_filter_buttons_style(self) -> None:
        t = self.theme
        self.filters_capsule.configure(bg=t.pill_track_bg)
        for key, btn in self.filter_buttons.items():
            is_active = key == self.active_filter
            if is_active:
                btn.set_colors(
                    bg=t.pill_active_bg,
                    fg=t.pill_active_fg,
                    hover_bg=t.pill_active_bg,
                    hover_fg=t.pill_active_fg,
                )
                btn.configure(font=("Helvetica", 9, "bold"))
            else:
                btn.set_colors(
                    bg=t.pill_track_bg,
                    fg=t.muted,
                    hover_bg=t.pill_hover_bg,
                    hover_fg=t.text,
                )
                btn.configure(font=("Helvetica", 9, "normal"))

    def _update_clear_button_style(self) -> None:
        t = self.theme
        completed_count = sum(task.done for task in self.tasks)
        if completed_count > 0:
            self.clear_button.set_state("normal")
            self.clear_button.set_colors(
                bg=t.card,
                fg=t.accent,
                hover_bg=t.card,
                hover_fg=t.accent_hover,
            )
        else:
            self.clear_button.set_state("disabled", disabled_fg=t.disabled)
            self.clear_button.set_colors(
                bg=t.card,
                fg=t.disabled,
                hover_bg=t.card,
                hover_fg=t.disabled,
            )

    # --- Mousewheel Event Handling ---

    def _on_mousewheel(self, event: tk.Event) -> None:
        if not self.canvas.winfo_exists():
            return
        if sys.platform == "darwin":
            # On macOS Tkinter, event.delta is typically +/- 1..5
            delta = -int(event.delta) if event.delta else 0
        elif sys.platform.startswith("win"):
            # On Windows, event.delta is multiples of +/- 120
            delta = int(-event.delta / 120) if event.delta else 0
        else:
            delta = -1 if event.delta > 0 else 1
        if delta:
            self.canvas.yview_scroll(delta, "units")

    def _on_linux_scroll_up(self, _event: tk.Event) -> None:
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(self, _event: tk.Event) -> None:
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(1, "units")

    # --- Entry Placeholder Handling ---

    def _on_entry_focus_in(self, _event: tk.Event) -> None:
        if self._is_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.theme.text)
            self._is_placeholder = False

    def _on_entry_focus_out(self, _event: tk.Event) -> None:
        if not self.entry.get().strip():
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.PLACEHOLDER_TEXT)
            self.entry.configure(fg=self.theme.muted)
            self._is_placeholder = True

    # --- Data Persistence ---

    def _load_data(self) -> None:
        if not DATA_FILE.exists():
            return
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, dict):
                raise ValueError("Unexpected data format.")

            # Load saved theme preference
            saved_theme = payload.get("theme")
            if saved_theme == "dark":
                self.theme = DARK_THEME
            else:
                self.theme = LIGHT_THEME

            # Load tasks
            saved_tasks = payload.get("tasks", [])
            if not isinstance(saved_tasks, list):
                raise ValueError("The saved task list has an unexpected format.")
            loaded = [Task.from_dict(item) for item in saved_tasks]
            self.tasks = [task for task in loaded if task is not None]
        except (OSError, json.JSONDecodeError, ValueError, AttributeError) as error:
            # Back up corrupted file so subsequent saves do not erase user data
            backup_path = DATA_FILE.with_suffix(".corrupted.bak")
            try:
                shutil.copy2(DATA_FILE, backup_path)
                self.status_text.set(
                    f"Warning: Could not read tasks ({error}). Backup saved to {backup_path.name}."
                )
            except OSError:
                self.status_text.set(f"Could not read saved tasks: {error}")

    def _save_data(self) -> None:
        temporary_file = DATA_FILE.with_suffix(".tmp")
        try:
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(
                    {
                        "version": 1,
                        "theme": self.theme.name,
                        "tasks": [task.to_dict() for task in self.tasks],
                    },
                    file,
                    indent=2,
                    ensure_ascii=False,
                )
                file.write("\n")
            temporary_file.replace(DATA_FILE)
            self.status_text.set("Your to-dos are saved locally.")
        except OSError as error:
            if temporary_file.exists():
                try:
                    temporary_file.unlink()
                except OSError:
                    pass
            self.status_text.set(f"Could not save tasks: {error}")

    # --- Filtering ---

    def set_filter(self, filter_key: str) -> None:
        if filter_key not in ("all", "active", "completed"):
            return
        self.active_filter = filter_key
        self._update_filter_buttons_style()
        self._render_tasks()

    def _get_visible_tasks(self) -> list[Task]:
        if self.active_filter == "active":
            return [task for task in self.tasks if not task.done]
        if self.active_filter == "completed":
            return [task for task in self.tasks if task.done]
        return self.tasks

    # --- Task Operations ---

    def add_task(self) -> None:
        if self._is_placeholder:
            self.status_text.set("Type a task before adding it.")
            self.entry.focus_set()
            return
        title = self.entry.get().strip()
        if not title:
            self.status_text.set("Type a task before adding it.")
            self.entry.focus_set()
            return

        self.tasks.append(Task(title=title, done=False))
        self._save_data()

        self.entry.delete(0, tk.END)
        self.entry.configure(fg=self.theme.text)
        self.entry.focus_set()
        self._render_tasks()

    def toggle_task(self, task_id: str, completed: bool) -> None:
        for task in self.tasks:
            if task.id == task_id:
                task.done = completed
                break
        self._save_data()

        if self.active_filter == "all":
            self._update_task_row_style(task_id, completed)
            self._update_summary()
        else:
            self._render_tasks()

    def _update_task_row_style(self, task_id: str, completed: bool) -> None:
        t = self.theme
        for label, _row in self.task_rows:
            if getattr(label, "_task_id", None) == task_id:
                label.configure(
                    fg=t.muted if completed else t.text,
                    font=("Helvetica", 11, "overstrike" if completed else "normal"),
                )
                break

    def delete_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self._save_data()
        self._render_tasks()

    def clear_completed(self) -> None:
        completed_count = sum(task.done for task in self.tasks)
        if not completed_count:
            self.status_text.set("There are no completed tasks to clear.")
            return
        if not messagebox.askyesno(
            "Clear completed tasks",
            f"Remove {completed_count} completed task{'s' if completed_count != 1 else ''}?",
            parent=self.root,
        ):
            return
        self.tasks = [task for task in self.tasks if not task.done]
        self._save_data()
        self._render_tasks()

    def start_edit_task(self, task: Task, label: tk.Label, row: tk.Frame) -> None:
        """Enables inline editing for a task title."""
        if self._editing_task_id is not None:
            return  # Allow editing one item at a time
        self._editing_task_id = task.id
        t = self.theme

        label.pack_forget()
        edit_entry = tk.Entry(
            row,
            font=("Helvetica", 11),
            relief="flat",
            bd=0,
            bg=t.input_bg,
            fg=t.text,
            insertbackground=t.text,
            highlightthickness=1,
            highlightbackground=t.accent,
            highlightcolor=t.accent,
        )
        edit_entry.insert(0, task.title)
        edit_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        edit_entry.focus_set()
        edit_entry.select_range(0, tk.END)

        def finish_edit(_event: tk.Event | None = None) -> None:
            if self._editing_task_id != task.id:
                return
            self._editing_task_id = None
            edit_entry.unbind("<FocusOut>")
            new_title = edit_entry.get().strip()
            edit_entry.destroy()
            label.pack(side="left", fill="x", expand=True)

            if new_title and new_title != task.title:
                task.title = new_title
                label.configure(text=new_title)
                self._save_data()
                self._update_scroll_region()
            elif not new_title:
                self.status_text.set("Task title cannot be empty.")

        def cancel_edit(_event: tk.Event | None = None) -> None:
            if self._editing_task_id != task.id:
                return
            self._editing_task_id = None
            edit_entry.unbind("<FocusOut>")
            edit_entry.destroy()
            label.pack(side="left", fill="x", expand=True)

        edit_entry.bind("<Return>", finish_edit)
        edit_entry.bind("<FocusOut>", finish_edit)
        edit_entry.bind("<Escape>", cancel_edit)

    # --- UI Rendering & Layout ---

    def _update_summary(self) -> None:
        remaining = sum(not task.done for task in self.tasks)
        total = len(self.tasks)

        self.summary_label.configure(
            text=f"{remaining} left" if remaining else ("All done" if total else "No to-dos")
        )
        self._update_clear_button_style()

    def _render_tasks(self) -> None:
        for child in self.rows_frame.winfo_children():
            child.destroy()
        self.task_rows.clear()
        self._editing_task_id = None

        self._update_summary()
        t = self.theme

        visible_tasks = self._get_visible_tasks()
        if not visible_tasks:
            empty_message = (
                "No to-dos yet. Enjoy your day!"
                if not self.tasks
                else f"No {self.active_filter} to-dos."
            )
            tk.Label(
                self.rows_frame,
                text=empty_message,
                bg=t.card,
                fg=t.muted,
                font=("Helvetica", 11),
                pady=32,
            ).pack(fill="x")
            return

        canvas_width = self.canvas.winfo_width()
        wrap = max(240, canvas_width - 160) if canvas_width > 1 else 500

        for index, task in enumerate(visible_tasks):
            row = tk.Frame(self.rows_frame, bg=t.card, pady=9)
            row.pack(fill="x")

            checked = tk.BooleanVar(value=task.done)
            check = tk.Checkbutton(
                row,
                variable=checked,
                command=lambda current_id=task.id, var=checked: self.toggle_task(
                    current_id, bool(var.get())
                ),
                bg=t.card,
                activebackground=t.card,
                selectcolor=t.card,
                relief="flat",
                bd=0,
                cursor="hand2",
            )
            check.pack(side="left", padx=(0, 10))

            # Delete button (packed on right edge)
            delete_button = FlatButton(
                row,
                text="×",
                command=lambda current_id=task.id: self.delete_task(current_id),
                font=("Helvetica", 16),
                bg=t.card,
                fg=t.muted,
                hover_bg=t.card,
                hover_fg=t.danger,
                padx=6,
                pady=1,
            )
            delete_button.pack(side="right")

            # Inline edit button (packed to the left of delete button)
            edit_button = FlatButton(
                row,
                text="✎",
                command=lambda tsk=task, l=None, r=row: None,  # Will attach below
                font=("Helvetica", 12),
                bg=t.card,
                fg=t.muted,
                hover_bg=t.card,
                hover_fg=t.accent,
                padx=6,
                pady=1,
            )
            edit_button.pack(side="right")

            label = tk.Label(
                row,
                text=task.title,
                bg=t.card,
                fg=t.muted if task.done else t.text,
                font=("Helvetica", 11, "overstrike" if task.done else "normal"),
                justify="left",
                anchor="w",
                wraplength=wrap,
                cursor="hand2",
            )
            setattr(label, "_task_id", task.id)
            label.pack(side="left", fill="x", expand=True)

            # Connect edit button and double-click to start inline editing
            edit_button.set_command(
                lambda tsk=task, l=label, r=row: self.start_edit_task(tsk, l, r)
            )
            label.bind(
                "<Double-Button-1>",
                lambda _e, tsk=task, l=label, r=row: self.start_edit_task(tsk, l, r),
            )

            self.task_rows.append((label, row))

            if index < len(visible_tasks) - 1:
                tk.Frame(self.rows_frame, bg=t.border, height=1).pack(fill="x")

    def _update_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_rows(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.rows_window, width=event.width)
        wrap = max(240, event.width - 160)
        for label, _row in self.task_rows:
            label.configure(wraplength=wrap)


def main() -> None:
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
