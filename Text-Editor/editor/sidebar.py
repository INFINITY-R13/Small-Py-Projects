"""
Collapsible File Explorer Sidebar for Aura Text Editor.
Displays directory trees with clean icons, handles open folder, and file selection.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Optional

from editor.tab_bar import get_file_icon


class FileExplorerSidebar(tk.Frame):
    """Aesthetic File Explorer sidebar with folder tree and quick actions."""

    def __init__(
        self,
        master,
        theme: dict,
        root_dir: Optional[str] = None,
        on_file_open: Optional[Callable[[str], None]] = None,
        on_toggle: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, bg=theme["sidebar_bg"], **kwargs)
        self.theme = theme
        self.root_dir = root_dir
        self.on_file_open_cb = on_file_open
        self.on_toggle_cb = on_toggle
        self.item_paths = {}

        self._init_ui()
        if self.root_dir and os.path.isdir(self.root_dir):
            self.load_directory(self.root_dir)

    def _init_ui(self):
        self.config(width=240, bg=self.theme["sidebar_bg"])

        # Header bar
        self.header_frame = tk.Frame(self, bg=self.theme["sidebar_bg"], pady=8, padx=12)
        self.header_frame.pack(side="top", fill="x")

        self.title_label = tk.Label(
            self.header_frame,
            text="EXPLORER",
            bg=self.theme["sidebar_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 10, "bold"),
        )
        self.title_label.pack(side="left")

        # Action buttons on header right
        self.actions_frame = tk.Frame(self.header_frame, bg=self.theme["sidebar_bg"])
        self.actions_frame.pack(side="right")

        self.btn_open_folder = tk.Label(
            self.actions_frame,
            text="📂",
            bg=self.theme["sidebar_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 11),
            cursor="hand2",
            padx=4,
        )
        self.btn_open_folder.pack(side="left")
        self.btn_open_folder.bind("<Button-1>", lambda e: self.choose_folder())

        self.btn_refresh = tk.Label(
            self.actions_frame,
            text="⟳",
            bg=self.theme["sidebar_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 12),
            cursor="hand2",
            padx=4,
        )
        self.btn_refresh.pack(side="left")
        self.btn_refresh.bind("<Button-1>", lambda e: self.refresh())

        self.btn_collapse = tk.Label(
            self.actions_frame,
            text="◀",
            bg=self.theme["sidebar_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 9),
            cursor="hand2",
            padx=4,
        )
        self.btn_collapse.pack(side="left")
        if self.on_toggle_cb:
            self.btn_collapse.bind("<Button-1>", lambda e: self.on_toggle_cb())

        for btn in (self.btn_open_folder, self.btn_refresh, self.btn_collapse):
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.theme["accent"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=self.theme["fg_dim"]))

        # Thin divider below header
        self.header_divider = tk.Frame(self, bg=self.theme["border"], height=1)
        self.header_divider.pack(side="top", fill="x")

        # Treeview styling
        self.style = ttk.Style()
        self._apply_treeview_style()

        # Treeview widget
        self.tree_frame = tk.Frame(self, bg=self.theme["sidebar_bg"])
        self.tree_frame.pack(side="top", fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.tree_frame,
            show="tree",
            selectmode="browse",
            style="Sidebar.Treeview",
        )
        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        # Right divider border
        self.right_border = tk.Frame(self, bg=self.theme["border"], width=1)
        self.right_border.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        # Events
        self.tree.bind("<Double-Button-1>", self._on_item_double_click)
        self.tree.bind("<Return>", self._on_item_double_click)
        self.tree.bind("<<TreeviewOpen>>", self._on_item_expanded)

    def _apply_treeview_style(self):
        try:
            self.style.theme_use("default")
        except tk.TclError:
            pass

        self.style.configure(
            "Sidebar.Treeview",
            background=self.theme["sidebar_bg"],
            foreground=self.theme["fg"],
            fieldbackground=self.theme["sidebar_bg"],
            font=("Helvetica Neue", 11),
            rowheight=24,
            borderwidth=0,
            highlightthickness=0,
        )
        self.style.map(
            "Sidebar.Treeview",
            background=[("selected", self.theme["selection_bg"])],
            foreground=[("selected", self.theme.get("selection_fg", "#ffffff"))],
        )

    def choose_folder(self):
        chosen = filedialog.askdirectory(title="Open Folder in Aura")
        if chosen:
            self.load_directory(chosen)

    def refresh(self):
        if self.root_dir and os.path.isdir(self.root_dir):
            self.load_directory(self.root_dir)

    def load_directory(self, folder_path: str):
        self.root_dir = folder_path
        self.tree.delete(*self.tree.get_children())
        self.item_paths.clear()

        folder_name = os.path.basename(folder_path) or folder_path
        root_node = self.tree.insert(
            "",
            "end",
            text=f"📁 {folder_name}",
            open=True,
        )
        self.item_paths[root_node] = folder_path
        self._populate_node(root_node, folder_path)

    def _populate_node(self, parent_node: str, parent_path: str):
        try:
            entries = sorted(os.scandir(parent_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except (PermissionError, OSError):
            return

        for entry in entries:
            # Skip hidden files like .git
            if entry.name.startswith("."):
                continue

            if entry.is_dir():
                sub_node = self.tree.insert(
                    parent_node,
                    "end",
                    text=f"📁 {entry.name}",
                    open=False,
                )
                self.item_paths[sub_node] = entry.path
                # Add dummy child so expand arrow appears
                dummy = self.tree.insert(sub_node, "end", text="")
                self.item_paths[dummy] = None
            else:
                icon = get_file_icon(entry.path)
                file_node = self.tree.insert(
                    parent_node,
                    "end",
                    text=f"{icon} {entry.name}",
                )
                self.item_paths[file_node] = entry.path

    def _on_item_expanded(self, event):
        item = self.tree.focus()
        path = self.item_paths.get(item)
        if path and os.path.isdir(path):
            # Check if has dummy node
            children = self.tree.get_children(item)
            if len(children) == 1 and self.item_paths.get(children[0]) is None:
                self.tree.delete(children[0])
                self._populate_node(item, path)

    def _on_item_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        path = self.item_paths.get(item)
        if not path:
            return

        if os.path.isfile(path):
            if self.on_file_open_cb:
                self.on_file_open_cb(path)
        elif os.path.isdir(path):
            is_open = self.tree.item(item, "open")
            self.tree.item(item, open=not is_open)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=theme["sidebar_bg"])
        self.header_frame.config(bg=theme["sidebar_bg"])
        self.title_label.config(bg=theme["sidebar_bg"], fg=theme["fg_dim"])
        self.actions_frame.config(bg=theme["sidebar_bg"])
        self.btn_open_folder.config(bg=theme["sidebar_bg"], fg=theme["fg_dim"])
        self.btn_refresh.config(bg=theme["sidebar_bg"], fg=theme["fg_dim"])
        self.btn_collapse.config(bg=theme["sidebar_bg"], fg=theme["fg_dim"])
        self.header_divider.config(bg=theme["border"])
        self.tree_frame.config(bg=theme["sidebar_bg"])
        self.right_border.config(bg=theme["border"])
        self._apply_treeview_style()
