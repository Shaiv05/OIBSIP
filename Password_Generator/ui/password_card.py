"""Password output card — display, show/hide, copy, QR."""

import threading
import io
import customtkinter as ctk
from PIL import Image

from .widgets import CardFrame, GlowButton
from core import clipboard


class PasswordCard(CardFrame):
    def __init__(self, master, t: dict, app_ref, **kwargs):
        super().__init__(master, title="GENERATED PASSWORD", t=t, **kwargs)
        self._t = t
        self._app = app_ref
        self._password = ""
        self._show = True
        self._build()

    def _build(self):
        t = self._t

        # Password display
        pw_frame = ctk.CTkFrame(self, fg_color=t["input_bg"], corner_radius=10, border_width=1, border_color=t["border"])
        pw_frame.pack(fill="x", padx=16, pady=(8, 0))

        self._pw_var = ctk.StringVar(value="Click Generate to create a password")
        self._pw_entry = ctk.CTkEntry(
            pw_frame,
            textvariable=self._pw_var,
            font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
            text_color=t["text"],
            fg_color="transparent",
            border_width=0,
            show="",
            state="readonly",
            height=52,
        )
        self._pw_entry.pack(side="left", fill="x", expand=True, padx=(12, 0))

        self._toggle_btn = ctk.CTkButton(
            pw_frame,
            text="👁",
            width=38,
            height=38,
            fg_color="transparent",
            hover_color=t["surface2"],
            text_color=t["text_muted"],
            font=ctk.CTkFont(size=16),
            command=self._toggle_visibility,
        )
        self._toggle_btn.pack(side="right", padx=4, pady=6)

        # Action buttons row
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(10, 14))

        self._copy_btn = GlowButton(
            btn_row,
            text="⎘  Copy",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=t["accent"],
            hover_color=t["accent_hover"],
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=self._copy,
            glow_color=t["accent_glow"],
        )
        self._copy_btn.pack(side="left", padx=(0, 8))

        self._qr_btn = ctk.CTkButton(
            btn_row,
            text="⬡  QR Code",
            font=ctk.CTkFont(size=13),
            fg_color=t["btn_secondary"],
            hover_color=t["btn_secondary_hover"],
            text_color=t["text"],
            height=36,
            corner_radius=8,
            command=self._show_qr,
        )
        self._qr_btn.pack(side="left", padx=(0, 8))

        self._status_label = ctk.CTkLabel(
            btn_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=t["success"],
        )
        self._status_label.pack(side="left")

    def set_password(self, password: str, show: bool = True):
        self._password = password
        self._show = show
        self._pw_entry.configure(state="normal")
        self._pw_var.set(password if show else "•" * len(password))
        self._pw_entry.configure(state="readonly", show="" if show else "")
        self._pw_entry.configure(show="")

    def _toggle_visibility(self):
        self._show = not self._show
        if self._show:
            self._pw_entry.configure(show="")
            self._pw_var.set(self._password)
            self._toggle_btn.configure(text="👁")
        else:
            self._pw_entry.configure(show="•")
            self._toggle_btn.configure(text="🙈")

    def _copy(self):
        if not self._password or self._password.startswith("Click"):
            return
        ok = clipboard.copy_to_clipboard(self._password)
        if ok:
            self._show_status("✓ Copied!", self._t["success"])
            settings = self._app.get_settings()
            if settings.get("auto_clear_clipboard"):
                delay = settings.get("auto_clear_delay", 30)
                clipboard.schedule_clear(delay, on_cleared=lambda: self._show_status("Clipboard cleared", self._t["text_muted"]))
        else:
            self._show_status("Copy failed", self._t["danger"])

    def _show_status(self, msg: str, color: str):
        self._status_label.configure(text=msg, text_color=color)
        self.after(2500, lambda: self._status_label.configure(text=""))

    def _show_qr(self):
        if not self._password or self._password.startswith("Click"):
            return
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(self._password)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            win = ctk.CTkToplevel(self)
            win.title("QR Code")
            win.resizable(False, False)
            win.grab_set()

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            pil_img = Image.open(buf)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(240, 240))
            ctk.CTkLabel(win, image=ctk_img, text="").pack(padx=20, pady=16)
            ctk.CTkLabel(win, text="Scan to use the password", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(0, 16))
        except ImportError:
            self._show_status("Install 'qrcode[pil]' for QR codes", self._t["warning"])
