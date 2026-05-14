"""
src/ui/theme.py — Centralised styling for the dark-mode UI.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import THEME, FONT_FAMILY


def apply_ttk_styles(style) -> None:
    """Configure all ttk widget styles for the dark theme."""
    T = THEME
    F = FONT_FAMILY

    style.theme_use("clam")

    # ── Base ───────────────────────────────────────────────────────────────
    style.configure(".",
        background=T["bg"],
        foreground=T["text"],
        font=(F, 10),
        borderwidth=0,
        focusthickness=0,
    )

    # ── Frames ─────────────────────────────────────────────────────────────
    style.configure("TFrame",       background=T["bg"])
    style.configure("Card.TFrame",  background=T["surface"],  relief="flat")
    style.configure("Card2.TFrame", background=T["surface2"], relief="flat")

    # ── Labels ─────────────────────────────────────────────────────────────
    style.configure("TLabel",
        background=T["bg"], foreground=T["text"], font=(F, 10))
    style.configure("Card.TLabel",
        background=T["surface"], foreground=T["text"], font=(F, 10))
    style.configure("Muted.TLabel",
        background=T["surface"], foreground=T["text_muted"], font=(F, 9))
    style.configure("Title.TLabel",
        background=T["bg"], foreground=T["text"],
        font=(F, 22, "bold"))
    style.configure("Subtitle.TLabel",
        background=T["bg"], foreground=T["text_muted"], font=(F, 10))
    style.configure("BMIValue.TLabel",
        background=T["surface"], foreground=T["accent"],
        font=(F, 36, "bold"))
    style.configure("Category.TLabel",
        background=T["surface"], foreground=T["text"],
        font=(F, 14, "bold"))
    style.configure("Tip.TLabel",
        background=T["surface2"], foreground=T["text_muted"],
        font=(F, 9), wraplength=440, justify="left")

    # Category-specific label styles
    for name, colour in [
        ("Normal",   "#34D399"),
        ("Warning",  "#FBBF24"),
        ("Danger",   "#F87171"),
    ]:
        style.configure(f"{name}.Category.TLabel",
            background=T["surface"], foreground=colour, font=(F, 14, "bold"))

    # ── Buttons ────────────────────────────────────────────────────────────
    style.configure("TButton",
        background=T["accent"], foreground="#ffffff",
        font=(F, 10, "bold"), padding=(16, 9), relief="flat", borderwidth=0)
    style.map("TButton",
        background=[("active", "#5A7AE8"), ("pressed", "#4A6AD4")])

    style.configure("Danger.TButton",
        background=T["danger"], foreground="#ffffff",
        font=(F, 10, "bold"), padding=(16, 9))
    style.map("Danger.TButton",
        background=[("active", "#E55555")])

    style.configure("Ghost.TButton",
        background=T["surface2"], foreground=T["text"],
        font=(F, 10), padding=(16, 9))
    style.map("Ghost.TButton",
        background=[("active", T["border"])])

    # ── Entries ────────────────────────────────────────────────────────────
    style.configure("TEntry",
        fieldbackground=T["entry_bg"], foreground=T["text"],
        insertcolor=T["text"], borderwidth=1, relief="solid",
        font=(F, 11), padding=(8, 6))
    style.map("TEntry",
        bordercolor=[("focus", T["accent"])])

    # ── Combobox ───────────────────────────────────────────────────────────
    style.configure("TCombobox",
        fieldbackground=T["entry_bg"], foreground=T["text"],
        background=T["entry_bg"], selectbackground=T["accent"],
        font=(F, 11), padding=(8, 6))
    style.map("TCombobox",
        fieldbackground=[("readonly", T["entry_bg"])],
        foreground=[("readonly", T["text"])])

    # ── Radiobutton ────────────────────────────────────────────────────────
    style.configure("TRadiobutton",
        background=T["surface"], foreground=T["text"], font=(F, 10))
    style.map("TRadiobutton",
        background=[("active", T["surface"])])

    # ── Separator ─────────────────────────────────────────────────────────
    style.configure("TSeparator", background=T["border"])

    # ── Scrollbar ─────────────────────────────────────────────────────────
    style.configure("TScrollbar",
        background=T["surface2"], troughcolor=T["surface"],
        arrowcolor=T["text_muted"], borderwidth=0)

    # ── Notebook (tabs) ───────────────────────────────────────────────────
    style.configure("TNotebook",
        background=T["bg"], borderwidth=0)
    style.configure("TNotebook.Tab",
        background=T["surface"], foreground=T["text_muted"],
        font=(F, 10), padding=(14, 7))
    style.map("TNotebook.Tab",
        background=[("selected", T["surface2"])],
        foreground=[("selected", T["text"])],
        expand=[("selected", [1, 1, 1, 0])])
