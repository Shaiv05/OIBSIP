"""Security analysis card — strength meter, entropy, crack time, warnings."""

import customtkinter as ctk
from .widgets import CardFrame


class SecurityCard(CardFrame):
    def __init__(self, master, t: dict, **kwargs):
        super().__init__(master, title="SECURITY ANALYSIS", t=t, **kwargs)
        self._t = t
        self._build()

    def _build(self):
        t = self._t
        pad = {"padx": 16}

        # Strength label + bar
        strength_row = ctk.CTkFrame(self, fg_color="transparent")
        strength_row.pack(fill="x", pady=(8, 4), **pad)

        self._strength_label = ctk.CTkLabel(
            strength_row,
            text="—",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=t["text_muted"],
        )
        self._strength_label.pack(side="left")

        self._entropy_label = ctk.CTkLabel(
            strength_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=t["text_muted"],
        )
        self._entropy_label.pack(side="right")

        # Strength bar
        bar_bg = ctk.CTkFrame(self, fg_color=t["strength_bg"], height=8, corner_radius=4)
        bar_bg.pack(fill="x", pady=(0, 6), **pad)
        bar_bg.pack_propagate(False)

        parent = None
        self._bar = ctk.CTkProgressBar(
    parent,
    height=12,
    corner_radius=999,
    fg_color="#2b2b2b",
    progress_color="#22c55e"
)
        self._bar.set(0)
        self._bar.pack(fill="x")

        # Stats grid
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(4, 6), **pad)

        self._crack_label = self._stat_row(stats, "Crack Time (GPU)", "—", 0)
        self._types_label = self._stat_row(stats, "Character Types", "—", 1)
        self._length_label = self._stat_row(stats, "Length", "—", 2)

        # Warnings
        self._warn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._warn_frame.pack(fill="x", pady=(0, 12), **pad)

    def _stat_row(self, parent, label: str, default: str, row: int):
        ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=self._t["text_muted"],
            anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=1)
        val = ctk.CTkLabel(
            parent,
            text=default,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self._t["text"],
            anchor="e",
        )
        val.grid(row=row, column=1, sticky="e", pady=1, padx=(12, 0))
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        return val

    def update_analysis(self, analysis: dict):
        t = self._t
        strength = analysis.get("strength", "—")
        color = analysis.get("color", t["text_muted"])
        entropy = analysis.get("entropy_bits", 0)
        bar_val = analysis.get("bar_fraction", 0)

        self._strength_label.configure(text=strength, text_color=color)
        self._entropy_label.configure(text=f"{entropy} bits entropy")
        self._bar.set(bar_val)
        self._bar.configure(progress_color=color)

        types_count = sum([
            analysis.get("has_upper", False),
            analysis.get("has_lower", False),
            analysis.get("has_digit", False),
            analysis.get("has_symbol", False),
        ])
        self._crack_label.configure(text=analysis.get("crack_time", "—"))
        self._types_label.configure(text=f"{types_count} / 4")
        self._length_label.configure(text=str(analysis.get("length", "—")))

        # Clear old warnings
        for w in self._warn_frame.winfo_children():
            w.destroy()

        warnings = analysis.get("warnings", [])
        if warnings:
            for msg in warnings[:3]:
                ctk.CTkLabel(
                    self._warn_frame,
                    text=f"⚠  {msg}",
                    font=ctk.CTkFont(size=11),
                    text_color=t["warning"],
                    anchor="w",
                    wraplength=340,
                    justify="left",
                ).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(
                self._warn_frame,
                text="✓  Password meets security requirements",
                font=ctk.CTkFont(size=11),
                text_color=t["success"],
                anchor="w",
            ).pack(anchor="w")
