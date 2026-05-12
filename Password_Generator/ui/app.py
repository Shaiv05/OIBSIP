"""Main application window — orchestrates all cards and keyboard shortcuts."""

import customtkinter as ctk
from tkinter import filedialog, messagebox

from .theme import get_theme
from .password_card import PasswordCard
from .settings_card import SettingsCard
from .security_card import SecurityCard
from .history_card import HistoryCard
from .widgets import GlowButton, CardFrame

from core import generator, security, clipboard, storage


class PassGenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._settings = storage.load_settings()
        self._current_password = ""
        self._theme_name = self._settings.get("theme", "dark")
        self._t = get_theme(self._theme_name)

        ctk.set_appearance_mode(self._theme_name)
        ctk.set_default_color_theme("blue")

        self.title("PassGen Pro")
        self.geometry("980x760")
        self.minsize(820, 600)
        self.configure(fg_color=self._t["bg"])

        self._build_ui()
        self._bind_shortcuts()

        # Generate an initial password on launch
        self.after(100, self._generate)

    # ─── UI Construction ────────────────────────────────────────────────────

    def _build_ui(self):
        t = self._t

        # Header bar
        header = ctk.CTkFrame(self, fg_color=t["surface"], corner_radius=0, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="PassGen Pro",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=t["text"],
        ).pack(side="left", padx=20)

        # Theme toggle
        self._theme_btn = ctk.CTkButton(
            header,
            text="☽  Dark" if self._theme_name == "light" else "☀  Light",
            width=90,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=t["btn_secondary"],
            hover_color=t["btn_secondary_hover"],
            text_color=t["text"],
            corner_radius=8,
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=12)

        # Settings import/export buttons
        ctk.CTkButton(
            header, text="Import Settings", width=110, height=30,
            font=ctk.CTkFont(size=12), fg_color=t["btn_secondary"],
            hover_color=t["btn_secondary_hover"], text_color=t["text"],
            corner_radius=8, command=self._import_settings,
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            header, text="Export Settings", width=110, height=30,
            font=ctk.CTkFont(size=12), fg_color=t["btn_secondary"],
            hover_color=t["btn_secondary_hover"], text_color=t["text"],
            corner_radius=8, command=self._export_settings,
        ).pack(side="right", padx=(0, 4))

        # Main content — two columns
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    def _build_left(self, parent):
        t = self._t

        # Password output card
        self._pw_card = PasswordCard(parent, t=t, app_ref=self)
        self._pw_card.pack(fill="x", pady=(0, 10))

        # Generate button (dominant CTA)
        self._gen_btn = GlowButton(
            parent,
            text="⟳  Generate Password",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=t["accent"],
            hover_color=t["accent_hover"],
            text_color="#ffffff",
            height=48,
            corner_radius=12,
            glow_color=t["accent_glow"],
            command=self._generate,
        )
        self._gen_btn.pack(fill="x", pady=(0, 10))

        # Security card
        self._sec_card = SecurityCard(parent, t=t)
        self._sec_card.pack(fill="x", pady=(0, 10))

        # Settings card (scrollable left column bottom)
        scroll_area = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=t["scrollbar"],
            scrollbar_button_hover_color=t["accent"],
        )
        scroll_area.pack(fill="both", expand=True)

        self._settings_card = SettingsCard(
            scroll_area,
            t=t,
            settings=self._settings,
            on_change=self._on_settings_change,
        )
        self._settings_card.pack(fill="x")

    def _build_right(self, parent):
        self._hist_card = HistoryCard(parent, t=self._t)
        self._hist_card.pack(fill="both", expand=True)

    # ─── Core Actions ───────────────────────────────────────────────────────

    def _generate(self):
        s = self._settings_card.get_settings_dict()
        self._settings.update(s)

        try:
            mode = s.get("mode", "strong")
            if mode == "passphrase":
                pwd = generator.generate_passphrase(
                    word_count=s.get("passphrase_words", 4),
                    separator=s.get("passphrase_separator", "-"),
                    capitalize=s.get("passphrase_capitalize", True),
                    add_number=s.get("passphrase_number", True),
                    add_symbol=s.get("passphrase_symbol", False),
                )
            else:
                length = s.get("length", 16)
                use_symbols = s.get("use_symbols", True)
                if mode == "balanced":
                    use_symbols = True
                    length = max(length, 12)

                pwd = generator.generate_password(
                    length=length,
                    use_upper=s.get("use_upper", True),
                    use_lower=s.get("use_lower", True),
                    use_digits=s.get("use_digits", True),
                    use_symbols=use_symbols,
                    exclude_similar=s.get("exclude_similar", False),
                    exclude_ambiguous=s.get("exclude_ambiguous", False),
                    exclude_custom=s.get("exclude_custom", ""),
                    no_consecutive_repeats=s.get("no_consecutive_repeats", False),
                    avoid_patterns=s.get("avoid_patterns", False),
                )

            self._current_password = pwd
            self._pw_card.set_password(pwd)

            charset_size = generator.estimate_charset_size(
                s.get("use_upper", True), s.get("use_lower", True),
                s.get("use_digits", True), s.get("use_symbols", True),
                s.get("exclude_similar", False), s.get("exclude_ambiguous", False),
            )
            analysis = security.analyze_password(pwd, charset_size)
            self._sec_card.update_analysis(analysis)

            entry = storage.add_to_history(pwd, analysis["strength"], analysis["entropy_bits"])
            self._hist_card.add_entry(entry)

            if s.get("auto_copy"):
                clipboard.copy_to_clipboard(pwd)

            storage.save_settings(self._settings)

        except ValueError as exc:
            messagebox.showwarning("Invalid Settings", str(exc))

    def _on_settings_change(self):
        """Regenerate whenever settings change (live preview)."""
        self._generate()

    def get_settings(self) -> dict:
        return self._settings

    # ─── Theme ──────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self._settings["theme"] = self._theme_name
        storage.save_settings(self._settings)
        messagebox.showinfo("Restart Required", "Please restart PassGen Pro to apply the new theme.")

    # ─── Settings import/export ─────────────────────────────────────────────

    def _import_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                new_settings = storage.import_settings_from_file(path)
                self._settings.update(new_settings)
                storage.save_settings(self._settings)
                messagebox.showinfo("Success", "Settings imported. Restart to fully apply all options.")
            except Exception as exc:
                messagebox.showerror("Import Failed", str(exc))

    def _export_settings(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="passgen_settings.json",
        )
        if path:
            s = self._settings_card.get_settings_dict()
            self._settings.update(s)
            storage.export_settings_to_file(path, self._settings)
            messagebox.showinfo("Exported", f"Settings saved to:\n{path}")

    # ─── Keyboard Shortcuts ──────────────────────────────────────────────────

    def _bind_shortcuts(self):
        self.bind("<Return>", lambda _: self._generate())
        self.bind("<Control-c>", lambda _: clipboard.copy_to_clipboard(self._current_password))
        self.bind("<Control-r>", lambda _: self._hist_card._clear_all())
        self.bind("<F5>", lambda _: self._generate())
