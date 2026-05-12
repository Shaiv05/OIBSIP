"""Password history card — list, search, favorites, delete, export."""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

from .widgets import CardFrame
from core import storage, clipboard


class HistoryCard(CardFrame):
    def __init__(self, master, t: dict, **kwargs):
        super().__init__(master, title="PASSWORD HISTORY", t=t, **kwargs)
        self._t = t
        self._history: list = storage.load_history()
        self._search_query = ""
        self._build()

    def _build(self):
        t = self._t

        # Search + actions
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(8, 6))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh())
        ctk.CTkEntry(
            top,
            textvariable=self._search_var,
            placeholder_text="🔍  Search history…",
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=t["input_bg"],
            text_color=t["text"],
            border_color=t["border"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            top,
            text="Export",
            width=64,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=t["btn_secondary"],
            hover_color=t["btn_secondary_hover"],
            text_color=t["text"],
            corner_radius=7,
            command=self._export_menu,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            top,
            text="Clear All",
            width=70,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=t["btn_secondary"],
            hover_color=t["danger"],
            text_color=t["text"],
            corner_radius=7,
            command=self._clear_all,
        ).pack(side="left")

        # Scrollable list
        self._list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=t["scrollbar"],
            scrollbar_button_hover_color=t["accent"],
            height=280,
        )
        self._list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self._refresh()

    def _refresh(self):
        query = self._search_var.get().lower()
        for w in self._list_frame.winfo_children():
            w.destroy()

        filtered = [
            e for e in self._history
            if query in e["password"].lower()
            or query in e.get("timestamp", "").lower()
            or query in e.get("strength", "").lower()
        ]

        # Favorites first
        filtered.sort(key=lambda e: (not e.get("favorite", False),))

        if not filtered:
            ctk.CTkLabel(
                self._list_frame,
                text="No passwords in history" if not self._history else "No results match your search",
                font=ctk.CTkFont(size=13),
                text_color=self._t["text_muted"],
            ).pack(pady=20)
            return

        for i, entry in enumerate(filtered):
            self._build_row(entry, i)

    def _build_row(self, entry: dict, idx: int):
        t = self._t
        is_fav = entry.get("favorite", False)
        row_color = t["history_fav"] if is_fav else (t["history_row"] if idx % 2 == 0 else t["history_row_alt"])

        row = ctk.CTkFrame(self._list_frame, fg_color=row_color, corner_radius=8)
        row.pack(fill="x", pady=2)

        # Left: password + meta
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=6)

        strength_color = {
            "Very Weak": t["danger"],
            "Weak": "#f97316",
            "Fair": t["warning"],
            "Strong": t["success"],
            "Very Strong": "#10b981",
        }.get(entry.get("strength", ""), t["text_muted"])

        pw_label = ctk.CTkLabel(
            left,
            text=entry["password"],
            font=ctk.CTkFont(family="Courier New", size=12, weight="bold"),
            text_color=t["text"],
            anchor="w",
        )
        pw_label.pack(anchor="w")

        meta = ctk.CTkFrame(left, fg_color="transparent")
        meta.pack(anchor="w")
        ctk.CTkLabel(meta, text=entry.get("timestamp", ""), font=ctk.CTkFont(size=10), text_color=t["text_dim"]).pack(side="left")
        ctk.CTkLabel(meta, text=f"  •  {entry.get('strength', '?')}", font=ctk.CTkFont(size=10, weight="bold"), text_color=strength_color).pack(side="left")
        ctk.CTkLabel(meta, text=f"  {entry.get('entropy', 0)} bits", font=ctk.CTkFont(size=10), text_color=t["text_dim"]).pack(side="left")

        # Right: actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="right", padx=6, pady=6)

        entry_id = entry["id"]

        fav_symbol = "★" if is_fav else "☆"
        ctk.CTkButton(
            actions, text=fav_symbol, width=28, height=28,
            fg_color="transparent", hover_color=t["surface2"],
            text_color="#f59e0b" if is_fav else t["text_muted"],
            font=ctk.CTkFont(size=14),
            command=lambda eid=entry_id: self._toggle_fav(eid),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="⎘", width=28, height=28,
            fg_color="transparent", hover_color=t["surface2"],
            text_color=t["text_muted"], font=ctk.CTkFont(size=14),
            command=lambda pw=entry["password"]: clipboard.copy_to_clipboard(pw),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="✕", width=28, height=28,
            fg_color="transparent", hover_color=t["danger"],
            text_color=t["text_muted"], font=ctk.CTkFont(size=14),
            command=lambda eid=entry_id: self._delete(eid),
        ).pack(side="left", padx=2)

    def add_entry(self, entry: dict):
        self._history.insert(0, entry)
        self._refresh()

    def _toggle_fav(self, entry_id: str):
        self._history = storage.toggle_favorite(entry_id)
        self._refresh()

    def _delete(self, entry_id: str):
        self._history = storage.delete_entry(entry_id)
        self._refresh()

    def _clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all password history? This cannot be undone."):
            storage.clear_history()
            self._history = []
            self._refresh()

    def _export_menu(self):
        win = ctk.CTkToplevel(self)
        win.title("Export History")
        win.geometry("260x140")
        win.resizable(False, False)
        win.grab_set()

        t = self._t
        ctk.CTkLabel(win, text="Export Format", font=ctk.CTkFont(size=14, weight="bold"), text_color=t["text"]).pack(pady=(18, 10))

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="TXT", width=100, height=36, fg_color=t["accent"], hover_color=t["accent_hover"],
            command=lambda: self._do_export("txt", win),
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="JSON", width=100, height=36, fg_color=t["btn_secondary"], hover_color=t["btn_secondary_hover"],
            text_color=t["text"],
            command=lambda: self._do_export("json", win),
        ).pack(side="left", padx=8)

    def _do_export(self, fmt: str, win):
        win.destroy()
        path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(), f"*.{fmt}")],
            initialfile=f"passwords.{fmt}",
        )
        if path:
            if fmt == "txt":
                storage.export_history_txt(path, self._history)
            else:
                storage.export_history_json(path, self._history)
