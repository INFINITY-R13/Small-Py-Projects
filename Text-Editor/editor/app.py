"""
Main Application Orchestrator for Aura Text Editor.
Coordinates tabs, file I/O, sidebar, search, status bar, zen mode, and menus.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Optional

from editor.code_editor import CodeEditor
from editor.find_replace import FindReplaceBar
from editor.sidebar import FileExplorerSidebar
from editor.status_bar import StatusBar
from editor.syntax import detect_language
from editor.tab_bar import AestheticTabBar
from editor.themes import DEFAULT_THEME, THEMES, get_theme


class AuraApp:
    """Aesthetic Text & Code Editor application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme_name = DEFAULT_THEME
        self.theme = get_theme(self.current_theme_name)

        # Tab state
        self.tabs: Dict[int, dict] = {}
        self.active_tab_id: Optional[int] = None
        self._next_tab_id = 1

        # Sidebar and Zen mode state
        self.sidebar_visible = True
        self.zen_mode = False

        self._setup_window()
        self._init_ui()
        self._setup_menus()
        self._bind_global_shortcuts()

        # Start with a clean tab
        self.new_file()

        # Load current working directory into sidebar
        cwd = os.getcwd()
        if os.path.isdir(cwd):
            self.sidebar.load_directory(cwd)

    def _setup_window(self):
        self.root.title("Aura Editor")
        self.root.geometry("1180x760")
        self.root.minsize(720, 500)
        self.root.config(bg=self.theme["bg"])

        # Center window on screen
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, (screen_w - 1180) // 2)
        y = max(0, (screen_h - 760) // 2)
        self.root.geometry(f"1180x760+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

    def _init_ui(self):
        # 1. Top Header Bar
        self.header_frame = tk.Frame(self.root, bg=self.theme["header_bg"], height=40, padx=14, pady=6)
        self.header_frame.pack(side="top", fill="x")

        # Logo / Badge
        self.logo_label = tk.Label(
            self.header_frame,
            text="◈ AURA",
            bg=self.theme["header_bg"],
            fg=self.theme["accent"],
            font=("Helvetica Neue", 13, "bold"),
        )
        self.logo_label.pack(side="left", padx=(0, 16))

        # Action Buttons
        self.header_btns = []
        btn_defs = [
            ("+ New", self.new_file),
            ("📂 Open", self.open_file_dialog),
            ("💾 Save", self.save_file),
            ("🔍 Find", self.open_find_replace),
            ("☰ Sidebar", self.toggle_sidebar),
            ("⛶ Zen", self.toggle_zen_mode),
        ]

        for text, cmd in btn_defs:
            btn = self._create_header_btn(self.header_frame, text, cmd)
            btn.pack(side="left", padx=(0, 6))
            self.header_btns.append(btn)

        # Right side header: Theme quick toggle button
        self.btn_theme_toggle = tk.Label(
            self.header_frame,
            text=f"🎨 {self.theme['name']}",
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            font=("Helvetica Neue", 11),
            cursor="hand2",
            padx=10,
            pady=4,
        )
        self.btn_theme_toggle.pack(side="right")
        self.btn_theme_toggle.bind("<Button-1>", lambda e: self.cycle_theme())
        self.btn_theme_toggle.bind("<Enter>", lambda e: self.btn_theme_toggle.config(bg=self.theme["btn_hover"]))
        self.btn_theme_toggle.bind("<Leave>", lambda e: self.btn_theme_toggle.config(bg=self.theme["btn_bg"]))

        # Thin header border
        self.header_border = tk.Frame(self.root, bg=self.theme["border"], height=1)
        self.header_border.pack(side="top", fill="x")

        # 2. Tab Bar
        self.tab_bar = AestheticTabBar(
            self.root,
            theme=self.theme,
            on_tab_select=self.switch_to_tab,
            on_tab_close=self.close_tab,
            on_new_tab=self.new_file,
        )
        self.tab_bar.pack(side="top", fill="x")

        # 3. Main Workspace Area (Sidebar + Editor Area)
        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(side="top", fill="both", expand=True)

        # Sidebar (File Explorer)
        self.sidebar = FileExplorerSidebar(
            self.main_container,
            theme=self.theme,
            on_file_open=self.open_file_path,
            on_toggle=self.toggle_sidebar,
        )
        self.sidebar.pack(side="left", fill="y")

        # Right container (Editor + FindBar + Welcome)
        self.right_container = tk.Frame(self.main_container, bg=self.theme["editor_bg"])
        self.right_container.pack(side="left", fill="both", expand=True)

        # Find & Replace bar (initially hidden)
        self.find_bar = FindReplaceBar(
            self.right_container,
            theme=self.theme,
            get_active_editor=self.get_active_editor,
        )

        # Editors container
        self.editors_container = tk.Frame(self.right_container, bg=self.theme["editor_bg"])
        self.editors_container.pack(fill="both", expand=True)

        # Welcome Card (Empty state when 0 tabs open)
        self.welcome_frame = self._create_welcome_view(self.editors_container)

        # 4. Bottom Status Bar
        self.status_bar = StatusBar(
            self.root,
            theme=self.theme,
            on_change_language=self.set_active_tab_language,
            on_change_theme=self.set_theme,
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _create_header_btn(self, parent, text: str, command) -> tk.Label:
        btn = tk.Label(
            parent,
            text=text,
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            font=("Helvetica Neue", 11),
            cursor="hand2",
            padx=10,
            pady=4,
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.theme["btn_hover"]))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.theme["btn_bg"]))
        return btn

    def _create_welcome_view(self, parent) -> tk.Frame:
        """Aesthetic welcome landing view when no tabs are open."""
        welcome = tk.Frame(parent, bg=self.theme["editor_bg"])

        center_box = tk.Frame(welcome, bg=self.theme["editor_bg"])
        center_box.place(relx=0.5, rely=0.45, anchor="center")

        logo = tk.Label(
            center_box,
            text="◈",
            font=("Helvetica Neue", 52),
            bg=self.theme["editor_bg"],
            fg=self.theme["accent"],
        )
        logo.pack(pady=(0, 6))

        title = tk.Label(
            center_box,
            text="AURA TEXT EDITOR",
            font=("Helvetica Neue", 22, "bold"),
            bg=self.theme["editor_bg"],
            fg=self.theme["fg"],
        )
        title.pack(pady=(0, 4))

        subtitle = tk.Label(
            center_box,
            text="An aesthetic, lightweight & fast text editor",
            font=("Helvetica Neue", 13),
            bg=self.theme["editor_bg"],
            fg=self.theme["fg_dim"],
        )
        subtitle.pack(pady=(0, 24))

        # Quick action buttons
        actions = tk.Frame(center_box, bg=self.theme["editor_bg"])
        actions.pack(pady=(0, 28))

        btn_new = tk.Label(
            actions,
            text="✨ New File",
            bg=self.theme["accent"],
            fg=self.theme["accent_fg"],
            font=("Helvetica Neue", 12, "bold"),
            cursor="hand2",
            padx=16,
            pady=8,
        )
        btn_new.pack(side="left", padx=8)
        btn_new.bind("<Button-1>", lambda e: self.new_file())

        btn_open = tk.Label(
            actions,
            text="📂 Open File",
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            font=("Helvetica Neue", 12),
            cursor="hand2",
            padx=16,
            pady=8,
        )
        btn_open.pack(side="left", padx=8)
        btn_open.bind("<Button-1>", lambda e: self.open_file_dialog())

        btn_folder = tk.Label(
            actions,
            text="📁 Open Folder",
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            font=("Helvetica Neue", 12),
            cursor="hand2",
            padx=16,
            pady=8,
        )
        btn_folder.pack(side="left", padx=8)
        btn_folder.bind("<Button-1>", lambda e: self.sidebar.choose_folder())

        # Shortcuts cheatsheet
        shortcuts_box = tk.Frame(center_box, bg=self.theme["sidebar_bg"], padx=20, pady=14)
        shortcuts_box.pack()

        shortcuts = [
            ("⌘N / Ctrl+N", "New Tab"),
            ("⌘O / Ctrl+O", "Open File"),
            ("⌘S / Ctrl+S", "Save File"),
            ("⌘F / Ctrl+F", "Find & Replace"),
            ("⌘B / Ctrl+B", "Toggle Sidebar"),
            ("⌘/ / Ctrl+/", "Toggle Comment"),
            ("F11", "Zen Mode"),
        ]

        # Store welcome view references for live theme switching
        self.welcome_elements = {
            "welcome": welcome,
            "center_box": center_box,
            "logo": logo,
            "title": title,
            "subtitle": subtitle,
            "actions": actions,
            "btn_new": btn_new,
            "btn_open": btn_open,
            "btn_folder": btn_folder,
            "shortcuts_box": shortcuts_box,
            "shortcut_rows": [],
        }

        for i, (key, desc) in enumerate(shortcuts):
            row = tk.Frame(shortcuts_box, bg=self.theme["sidebar_bg"])
            row.pack(fill="x", pady=2)

            k_lbl = tk.Label(
                row,
                text=key,
                bg=self.theme["btn_bg"],
                fg=self.theme["accent"],
                font=("Menlo", 11, "bold"),
                padx=6,
                pady=1,
            )
            k_lbl.pack(side="left")

            d_lbl = tk.Label(
                row,
                text=desc,
                bg=self.theme["sidebar_bg"],
                fg=self.theme["fg_dim"],
                font=("Helvetica Neue", 11),
                padx=10,
            )
            d_lbl.pack(side="left")
            self.welcome_elements["shortcut_rows"].append((row, k_lbl, d_lbl))

        return welcome

    def _setup_menus(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New File", accelerator="Cmd+N", command=self.new_file)
        file_menu.add_command(label="Open File...", accelerator="Cmd+O", command=self.open_file_dialog)
        file_menu.add_command(label="Open Folder...", accelerator="Cmd+Shift+O", command=self.sidebar.choose_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Cmd+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Cmd+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Cmd+W", command=lambda: self.close_tab(self.active_tab_id))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Cmd+Q", command=self.on_quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Cmd+Z", command=self._undo)
        edit_menu.add_command(label="Redo", accelerator="Cmd+Shift+Z", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Cmd+X", command=self._cut)
        edit_menu.add_command(label="Copy", accelerator="Cmd+C", command=self._copy)
        edit_menu.add_command(label="Paste", accelerator="Cmd+V", command=self._paste)
        edit_menu.add_command(label="Select All", accelerator="Cmd+A", command=self._select_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace", accelerator="Cmd+F", command=self.open_find_replace)
        edit_menu.add_command(label="Toggle Comment", accelerator="Cmd+/", command=self._toggle_comment)
        edit_menu.add_command(label="Duplicate Line", accelerator="Cmd+D", command=self._duplicate_line)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Toggle Sidebar", accelerator="Cmd+B", command=self.toggle_sidebar)
        view_menu.add_command(label="Zen Mode (Distraction Free)", accelerator="F11", command=self.toggle_zen_mode)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._zoom(1))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._zoom(-1))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=self._reset_zoom)
        menubar.add_cascade(label="View", menu=view_menu)

        # Themes Menu
        theme_menu = tk.Menu(menubar, tearoff=False)
        for t_name in THEMES.keys():
            theme_menu.add_command(label=t_name, command=lambda n=t_name: self.set_theme(n))
        menubar.add_cascade(label="Theme", menu=theme_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="About Aura Editor", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _bind_global_shortcuts(self):
        # Native Mac command keys and cross-platform control keys
        for prefix in ("<Command-", "<Control-"):
            self.root.bind(f"{prefix}n>", lambda e: self.new_file())
            self.root.bind(f"{prefix}N>", lambda e: self.new_file())
            self.root.bind(f"{prefix}o>", lambda e: self.open_file_dialog())
            self.root.bind(f"{prefix}O>", lambda e: self.open_file_dialog())
            self.root.bind(f"{prefix}s>", lambda e: self.save_file())
            self.root.bind(f"{prefix}S>", lambda e: self.save_file_as())
            self.root.bind(f"{prefix}w>", lambda e: self.close_tab(self.active_tab_id))
            self.root.bind(f"{prefix}W>", lambda e: self.close_tab(self.active_tab_id))
            self.root.bind(f"{prefix}f>", lambda e: self.open_find_replace())
            self.root.bind(f"{prefix}F>", lambda e: self.open_find_replace())
            self.root.bind(f"{prefix}b>", lambda e: self.toggle_sidebar())
            self.root.bind(f"{prefix}B>", lambda e: self.toggle_sidebar())

        # Zen mode
        self.root.bind("<F11>", lambda e: self.toggle_zen_mode())
        self.root.bind("<Escape>", self._on_escape)

    def _on_escape(self, event):
        if self.find_bar.winfo_ismapped():
            self.find_bar.close()
        elif self.zen_mode:
            self.toggle_zen_mode()

    # --- Tab Management ---

    def new_file(self, content: str = "", filepath: Optional[str] = None):
        tab_id = self._next_tab_id
        self._next_tab_id += 1

        title = os.path.basename(filepath) if filepath else "Untitled"

        editor = CodeEditor(
            self.editors_container,
            theme=self.theme,
            filepath=filepath,
            on_modified=lambda mod, tid=tab_id: self._on_editor_modified(tid, mod),
            on_cursor_move=self.status_bar.update_stats,
        )

        if content:
            editor.text.insert("1.0", content)
            editor.text.edit_reset()
            editor.set_modified(False)
            editor.highlighter.highlight_all()

        tab_item = self.tab_bar.add_tab(tab_id=tab_id, title=title, filepath=filepath)

        self.tabs[tab_id] = {
            "editor": editor,
            "filepath": filepath,
            "tab_item": tab_item,
        }

        self.welcome_frame.pack_forget()
        self.switch_to_tab(tab_id)

    def switch_to_tab(self, tab_id: int):
        if tab_id not in self.tabs:
            return

        # Hide current active editor
        if self.active_tab_id and self.active_tab_id in self.tabs:
            self.tabs[self.active_tab_id]["editor"].pack_forget()

        self.active_tab_id = tab_id
        active_info = self.tabs[tab_id]
        editor = active_info["editor"]
        editor.pack(fill="both", expand=True)

        self.tab_bar.select_tab(tab_id)
        editor.text.focus_set()

        # Update status bar
        lang = editor.highlighter.language
        self.status_bar.set_language(lang)
        editor._schedule_stats_update()

        # Update window title
        fname = os.path.basename(active_info["filepath"]) if active_info["filepath"] else "Untitled"
        prefix = "● " if editor.is_modified else ""
        self.root.title(f"{prefix}Aura Editor — {fname}")

    def close_tab(self, tab_id: Optional[int]):
        if not tab_id or tab_id not in self.tabs:
            return

        info = self.tabs[tab_id]
        editor = info["editor"]

        # Check for unsaved changes
        if editor.is_modified:
            name = os.path.basename(info["filepath"]) if info["filepath"] else "Untitled"
            resp = messagebox.askyesnocancel(
                "Unsaved Changes",
                f'Do you want to save the changes you made to "{name}"?',
                parent=self.root,
            )
            if resp is None:  # Cancel
                return
            elif resp:  # Save
                if not self.save_file(tab_id):
                    return

        # Destroy editor and tab item
        editor.destroy()
        self.tab_bar.remove_tab(tab_id)
        del self.tabs[tab_id]

        # Switch to another tab or show welcome
        if self.tabs:
            remaining_ids = list(self.tabs.keys())
            self.switch_to_tab(remaining_ids[-1])
        else:
            self.active_tab_id = None
            self.welcome_frame.pack(fill="both", expand=True)
            self.root.title("Aura Editor")
            self.status_bar.update_stats(1, 1, 0, 0, 0, 0)

    def _on_editor_modified(self, tab_id: int, modified: bool):
        if tab_id in self.tabs:
            self.tabs[tab_id]["tab_item"].set_modified(modified)
            if tab_id == self.active_tab_id:
                fname = os.path.basename(self.tabs[tab_id]["filepath"]) if self.tabs[tab_id]["filepath"] else "Untitled"
                prefix = "● " if modified else ""
                self.root.title(f"{prefix}Aura Editor — {fname}")

    def get_active_editor(self) -> Optional[CodeEditor]:
        if self.active_tab_id and self.active_tab_id in self.tabs:
            return self.tabs[self.active_tab_id]["editor"]
        return None

    # --- File Operations ---

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Open File in Aura",
            filetypes=[
                ("All Supported Files", "*.py *.md *.json *.html *.css *.js *.ts *.sh *.txt *.sql"),
                ("Python Files", "*.py *.pyw"),
                ("Markdown Files", "*.md *.markdown"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*"),
            ],
            parent=self.root,
        )
        if filepath:
            self.open_file_path(filepath)

    def open_file_path(self, filepath: str):
        # Check if already open
        for tid, info in self.tabs.items():
            if info["filepath"] == filepath:
                self.switch_to_tab(tid)
                return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not read file:\n{e}", parent=self.root)
            return

        # If current tab is empty Untitled, reuse it
        cur_editor = self.get_active_editor()
        if (
            cur_editor
            and self.tabs[self.active_tab_id]["filepath"] is None
            and not cur_editor.is_modified
            and len(cur_editor.text.get("1.0", "end-1c").strip()) == 0
        ):
            cur_editor.text.delete("1.0", "end")
            cur_editor.text.insert("1.0", content)
            cur_editor.text.edit_reset()
            cur_editor.set_filepath(filepath)
            cur_editor.set_modified(False)

            self.tabs[self.active_tab_id]["filepath"] = filepath
            self.tabs[self.active_tab_id]["tab_item"].set_filepath(filepath)
            self.switch_to_tab(self.active_tab_id)
        else:
            self.new_file(content=content, filepath=filepath)

    def save_file(self, tab_id: Optional[int] = None) -> bool:
        tid = tab_id or self.active_tab_id
        if not tid or tid not in self.tabs:
            return False

        info = self.tabs[tid]
        filepath = info["filepath"]

        if not filepath:
            return self.save_file_as(tid)

        try:
            content = info["editor"].text.get("1.0", "end-1c")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            info["editor"].set_modified(False)
            info["tab_item"].set_modified(False)
            fname = os.path.basename(filepath)
            self.root.title(f"Aura Editor — {fname}")
            return True
        except Exception as e:
            messagebox.showerror("Error Saving File", f"Could not save file:\n{e}", parent=self.root)
            return False

    def save_file_as(self, tab_id: Optional[int] = None) -> bool:
        tid = tab_id or self.active_tab_id
        if not tid or tid not in self.tabs:
            return False

        filepath = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".txt",
            filetypes=[
                ("Python File", "*.py"),
                ("Markdown File", "*.md"),
                ("JSON File", "*.json"),
                ("Text File", "*.txt"),
                ("All Files", "*.*"),
            ],
            parent=self.root,
        )
        if not filepath:
            return False

        self.tabs[tid]["filepath"] = filepath
        self.tabs[tid]["editor"].set_filepath(filepath)
        self.tabs[tid]["tab_item"].set_filepath(filepath)
        return self.save_file(tid)

    # --- Search, View & Editing Helpers ---

    def open_find_replace(self):
        editor = self.get_active_editor()
        sel_text = ""
        if editor:
            try:
                sel_ranges = editor.text.tag_ranges("sel")
                if sel_ranges:
                    sel_text = editor.text.get(sel_ranges[0], sel_ranges[1])
            except tk.TclError:
                pass
        self.find_bar.open_find(sel_text)

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar.pack(side="left", fill="y", before=self.right_container)
        else:
            self.sidebar.pack_forget()

    def toggle_zen_mode(self):
        self.zen_mode = not self.zen_mode
        if self.zen_mode:
            # Hide non-essentials
            self.header_frame.pack_forget()
            self.header_border.pack_forget()
            self.tab_bar.pack_forget()
            self.sidebar.pack_forget()
            self.status_bar.pack_forget()
            self.root.attributes("-fullscreen", True)
        else:
            self.root.attributes("-fullscreen", False)
            self.header_frame.pack(side="top", fill="x", before=self.main_container)
            self.header_border.pack(side="top", fill="x", before=self.main_container)
            self.tab_bar.pack(side="top", fill="x", before=self.main_container)
            if self.sidebar_visible:
                self.sidebar.pack(side="left", fill="y", before=self.right_container)
            self.status_bar.pack(side="bottom", fill="x")

    def set_active_tab_language(self, lang_key: str):
        editor = self.get_active_editor()
        if editor:
            editor.highlighter.set_language(lang_key)

    # --- Themes ---

    def cycle_theme(self):
        theme_names = list(THEMES.keys())
        idx = theme_names.index(self.current_theme_name)
        next_theme = theme_names[(idx + 1) % len(theme_names)]
        self.set_theme(next_theme)

    def set_theme(self, theme_name: str):
        self.current_theme_name = theme_name
        self.theme = get_theme(theme_name)

        self.root.config(bg=self.theme["bg"])
        self.header_frame.config(bg=self.theme["header_bg"])
        self.logo_label.config(bg=self.theme["header_bg"], fg=self.theme["accent"])
        self.header_border.config(bg=self.theme["border"])
        self.main_container.config(bg=self.theme["bg"])
        self.right_container.config(bg=self.theme["editor_bg"])
        self.editors_container.config(bg=self.theme["editor_bg"])

        for btn in self.header_btns:
            btn.config(bg=self.theme["btn_bg"], fg=self.theme["fg"])

        self.btn_theme_toggle.config(
            text=f"🎨 {self.theme['name']}",
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
        )

        self.tab_bar.apply_theme(self.theme)
        self.sidebar.apply_theme(self.theme)
        self.find_bar.apply_theme(self.theme)
        self.status_bar.apply_theme(self.theme)

        for tab_info in self.tabs.values():
            tab_info["editor"].apply_theme(self.theme)

        # Update welcome frame colors if initialized
        if hasattr(self, "welcome_elements"):
            we = self.welcome_elements
            we["welcome"].config(bg=self.theme["editor_bg"])
            we["center_box"].config(bg=self.theme["editor_bg"])
            we["logo"].config(bg=self.theme["editor_bg"], fg=self.theme["accent"])
            we["title"].config(bg=self.theme["editor_bg"], fg=self.theme["fg"])
            we["subtitle"].config(bg=self.theme["editor_bg"], fg=self.theme["fg_dim"])
            we["actions"].config(bg=self.theme["editor_bg"])
            we["btn_new"].config(bg=self.theme["accent"], fg=self.theme["accent_fg"])
            we["btn_open"].config(bg=self.theme["btn_bg"], fg=self.theme["fg"])
            we["btn_folder"].config(bg=self.theme["btn_bg"], fg=self.theme["fg"])
            we["shortcuts_box"].config(bg=self.theme["sidebar_bg"])
            for row, k_lbl, d_lbl in we["shortcut_rows"]:
                row.config(bg=self.theme["sidebar_bg"])
                k_lbl.config(bg=self.theme["btn_bg"], fg=self.theme["accent"])
                d_lbl.config(bg=self.theme["sidebar_bg"], fg=self.theme["fg_dim"])

    # --- Standard Edit Actions ---

    def _undo(self):
        editor = self.get_active_editor()
        if editor:
            try:
                editor.text.edit_undo()
                editor.gutter.redraw()
            except tk.TclError:
                pass

    def _redo(self):
        editor = self.get_active_editor()
        if editor:
            try:
                editor.text.edit_redo()
                editor.gutter.redraw()
            except tk.TclError:
                pass

    def _cut(self):
        editor = self.get_active_editor()
        if editor:
            editor.text.event_generate("<<Cut>>")

    def _copy(self):
        editor = self.get_active_editor()
        if editor:
            editor.text.event_generate("<<Copy>>")

    def _paste(self):
        editor = self.get_active_editor()
        if editor:
            editor.text.event_generate("<<Paste>>")

    def _select_all(self):
        editor = self.get_active_editor()
        if editor:
            editor.text.tag_add("sel", "1.0", "end")

    def _toggle_comment(self):
        editor = self.get_active_editor()
        if editor:
            editor.toggle_comment()

    def _duplicate_line(self):
        editor = self.get_active_editor()
        if editor:
            editor.duplicate_line()

    def _zoom(self, delta: int):
        editor = self.get_active_editor()
        if editor:
            editor.zoom(delta)

    def _reset_zoom(self):
        editor = self.get_active_editor()
        if editor:
            editor.reset_zoom()

    def _show_shortcuts(self):
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "⌘N / Ctrl+N : New Tab\n"
            "⌘O / Ctrl+O : Open File\n"
            "⌘S / Ctrl+S : Save File\n"
            "⌘W / Ctrl+W : Close Tab\n"
            "⌘F / Ctrl+F : Find & Replace\n"
            "⌘B / Ctrl+B : Toggle Sidebar\n"
            "⌘/ / Ctrl+/ : Toggle Line Comment\n"
            "⌘D / Ctrl+D : Duplicate Line\n"
            "Alt+Up / Alt+Down : Move Line\n"
            "⌘= / ⌘- : Zoom In / Out\n"
            "F11 : Zen Mode (Distraction-free)\n"
            "Esc : Close Find Bar / Exit Zen",
            parent=self.root,
        )

    def _show_about(self):
        messagebox.showinfo(
            "About Aura Editor",
            "Aura Text Editor v1.0\n\n"
            "An aesthetic, modern, distraction-free code and text editor built in Python.\n\n"
            "Featuring Tokyo Night, Catppuccin, Dracula, and Nord themes,\n"
            "synchronized line numbers, regex syntax highlighting, smart indentation,\n"
            "bracket matching, and multi-tab workflows.",
            parent=self.root,
        )

    def on_quit(self):
        # Check all modified tabs
        unsaved = [info for info in self.tabs.values() if info["editor"].is_modified]
        if unsaved:
            names = [
                os.path.basename(i["filepath"]) if i["filepath"] else "Untitled"
                for i in unsaved
            ]
            resp = messagebox.askyesnocancel(
                "Unsaved Documents",
                f"You have {len(unsaved)} unsaved document(s):\n"
                + "\n".join(f"• {n}" for n in names[:5])
                + "\n\nDo you want to save your changes before quitting?",
                parent=self.root,
            )
            if resp is None:  # Cancel
                return
            elif resp:  # Save
                for info in unsaved:
                    for tid, tab_val in self.tabs.items():
                        if tab_val == info:
                            if not self.save_file(tid):
                                return

        self.root.destroy()
