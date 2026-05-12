"""Settings card — mode selector, length, character options, advanced options."""

from typing import Callable
import customtkinter as ctk
from .widgets import CardFrame, ToggleRow, LabeledSlider


class SettingsCard(CardFrame):
    def __init__(self, master, t: dict, settings: dict, on_change: Callable = None, **kwargs):
        super().__init__(master, title="GENERATION SETTINGS", t=t, **kwargs)
        self._t = t
        self._on_change = on_change
        self._init_vars(settings)
        self._build()

    def _init_vars(self, s: dict):
        self.mode_var = ctk.StringVar(value=s.get("mode", "strong"))
        self.length_var = ctk.IntVar(value=s.get("length", 16))
        self.use_upper = ctk.BooleanVar(value=s.get("use_upper", True))
        self.use_lower = ctk.BooleanVar(value=s.get("use_lower", True))
        self.use_digits = ctk.BooleanVar(value=s.get("use_digits", True))
        self.use_symbols = ctk.BooleanVar(value=s.get("use_symbols", True))
        self.excl_similar = ctk.BooleanVar(value=s.get("exclude_similar", False))
        self.excl_ambiguous = ctk.BooleanVar(value=s.get("exclude_ambiguous", False))
        self.no_consec = ctk.BooleanVar(value=s.get("no_consecutive_repeats", False))
        self.avoid_patterns = ctk.BooleanVar(value=s.get("avoid_patterns", False))
        self.auto_copy = ctk.BooleanVar(value=s.get("auto_copy", False))
        self.auto_clear = ctk.BooleanVar(value=s.get("auto_clear_clipboard", False))
        self.auto_clear_delay = ctk.IntVar(value=s.get("auto_clear_delay", 30))

        # Passphrase options
        self.pp_words = ctk.IntVar(value=s.get("passphrase_words", 4))
        self.pp_sep = ctk.StringVar(value=s.get("passphrase_separator", "-"))
        self.pp_capitalize = ctk.BooleanVar(value=s.get("passphrase_capitalize", True))
        self.pp_number = ctk.BooleanVar(value=s.get("passphrase_number", True))
        self.pp_symbol = ctk.BooleanVar(value=s.get("passphrase_symbol", False))
        self.excl_custom_var = ctk.StringVar(value=s.get("exclude_custom", ""))

    def _build(self):
        t = self._t
        pad = {"padx": 16}

        # Mode selector
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(8, 4), **pad)

        for mode, label in [("strong", "Strong"), ("balanced", "Balanced"), ("passphrase", "Passphrase")]:
            btn = ctk.CTkButton(
                mode_frame,
                text=label,
                height=30,
                corner_radius=7,
                font=ctk.CTkFont(size=12),
                command=lambda m=mode: self._set_mode(m),
            )
            btn.pack(side="left", padx=(0, 6))
            setattr(self, f"_mode_btn_{mode}", btn)

        self._refresh_mode_buttons()

        # Dynamic content area
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="x", **pad)
        self._build_mode_content()

    def _set_mode(self, mode: str):
        self.mode_var.set(mode)
        self._refresh_mode_buttons()
        self._build_mode_content()
        if self._on_change:
            self._on_change()

    def _refresh_mode_buttons(self):
        t = self._t
        current = self.mode_var.get()
        for mode in ["strong", "balanced", "passphrase"]:
            btn = getattr(self, f"_mode_btn_{mode}", None)
            if btn:
                if mode == current:
                    btn.configure(fg_color=t["accent"], text_color="#ffffff", hover_color=t["accent_hover"])
                else:
                    btn.configure(fg_color=t["btn_secondary"], text_color=t["text"], hover_color=t["btn_secondary_hover"])

    def _build_mode_content(self):
        for w in self._content.winfo_children():
            w.destroy()
        mode = self.mode_var.get()
        if mode == "passphrase":
            self._build_passphrase_options()
        else:
            self._build_password_options()

    def _build_password_options(self):
        t = self._t
        f = self._content

        LabeledSlider(f, "Length", self.length_var, 4, 64, t=t, command=lambda _=None: self._changed()).pack(fill="x", pady=(8, 8))

        # Character types
        ctk.CTkLabel(f, text="Character Types", font=ctk.CTkFont(size=11), text_color=t["text_muted"], anchor="w").pack(anchor="w", pady=(0, 4))

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x")

        for i, (var, label) in enumerate([
            (self.use_upper, "Uppercase  A-Z"),
            (self.use_lower, "Lowercase  a-z"),
            (self.use_digits, "Digits  0-9"),
            (self.use_symbols, "Symbols  !@#…"),
        ]):
            cb = ctk.CTkCheckBox(
                grid,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=t["text"],
                fg_color=t["accent"],
                hover_color=t["accent_hover"],
                checkmark_color="#ffffff",
                border_color=t["border"],
                command=self._changed,
            )
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=3)

        # Advanced
        ctk.CTkLabel(f, text="Advanced", font=ctk.CTkFont(size=11), text_color=t["text_muted"], anchor="w").pack(anchor="w", pady=(12, 4))

        for var, label in [
            (self.excl_similar, "Exclude similar chars  (O, 0, I, l, 1)"),
            (self.excl_ambiguous, "Exclude ambiguous symbols"),
            (self.no_consec, "No consecutive repeated characters"),
            (self.avoid_patterns, "Avoid sequential patterns"),
            (self.auto_copy, "Auto-copy after generation"),
        ]:
            ToggleRow(f, label, var, t=t, command=self._changed).pack(fill="x", pady=2)

        # Auto-clear clipboard
        ToggleRow(f, "Auto-clear clipboard after copy", self.auto_clear, t=t, command=self._changed).pack(fill="x", pady=2)

        delay_frame = ctk.CTkFrame(f, fg_color="transparent")
        delay_frame.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(delay_frame, text="  Clear after (seconds)", font=ctk.CTkFont(size=12), text_color=t["text_muted"]).pack(side="left")
        ctk.CTkEntry(delay_frame, textvariable=self.auto_clear_delay, width=55, height=26, font=ctk.CTkFont(size=12),
                     fg_color=t["input_bg"], text_color=t["text"], border_color=t["border"]).pack(side="right")

        # Exclude custom
        ctk.CTkLabel(f, text="Exclude custom characters", font=ctk.CTkFont(size=11), text_color=t["text_muted"], anchor="w").pack(anchor="w", pady=(10, 2))
        ctk.CTkEntry(
            f,
            textvariable=self.excl_custom_var,
            placeholder_text="e.g.  @ # $ …",
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color=t["input_bg"],
            text_color=t["text"],
            border_color=t["border"],
        ).pack(fill="x", pady=(0, 10))

    def _build_passphrase_options(self):
        t = self._t
        f = self._content

        LabeledSlider(f, "Word Count", self.pp_words, 2, 8, t=t, command=lambda _=None: self._changed()).pack(fill="x", pady=(8, 8))

        sep_row = ctk.CTkFrame(f, fg_color="transparent")
        sep_row.pack(fill="x", pady=4)
        ctk.CTkLabel(sep_row, text="Separator", font=ctk.CTkFont(size=13), text_color=t["text"]).pack(side="left")
        ctk.CTkEntry(sep_row, textvariable=self.pp_sep, width=60, height=28, fg_color=t["input_bg"],
                     text_color=t["text"], border_color=t["border"], font=ctk.CTkFont(size=13)).pack(side="right")

        for var, label in [
            (self.pp_capitalize, "Capitalize words"),
            (self.pp_number, "Append random number"),
            (self.pp_symbol, "Append symbol"),
        ]:
            ToggleRow(f, label, var, t=t, command=self._changed).pack(fill="x", pady=2)

    def _changed(self):
        if self._on_change:
            self._on_change()

    def get_settings_dict(self) -> dict:
        return {
            "mode": self.mode_var.get(),
            "length": self.length_var.get(),
            "use_upper": self.use_upper.get(),
            "use_lower": self.use_lower.get(),
            "use_digits": self.use_digits.get(),
            "use_symbols": self.use_symbols.get(),
            "exclude_similar": self.excl_similar.get(),
            "exclude_ambiguous": self.excl_ambiguous.get(),
            "exclude_custom": self.excl_custom_var.get(),
            "no_consecutive_repeats": self.no_consec.get(),
            "avoid_patterns": self.avoid_patterns.get(),
            "auto_copy": self.auto_copy.get(),
            "auto_clear_clipboard": self.auto_clear.get(),
            "auto_clear_delay": self.auto_clear_delay.get(),
            "passphrase_words": self.pp_words.get(),
            "passphrase_separator": self.pp_sep.get(),
            "passphrase_capitalize": self.pp_capitalize.get(),
            "passphrase_number": self.pp_number.get(),
            "passphrase_symbol": self.pp_symbol.get(),
        }
