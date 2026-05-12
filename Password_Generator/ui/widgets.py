"""Reusable custom widgets and helpers."""

import customtkinter as ctk
from typing import Callable


class GlowButton(ctk.CTkButton):
    """Button with animated glow/pulse effect on hover."""

    def __init__(self, master, glow_color: str = "#6366f140", **kwargs):
        super().__init__(master, **kwargs)
        self._glow_color = glow_color
        self._default_fg = kwargs.get("fg_color", "#6366f1")
        self._hover_fg = kwargs.get("hover_color", "#4f46e5")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None):
        self.configure(border_width=2, border_color=self._glow_color)

    def _on_leave(self, _event=None):
        self.configure(border_width=0)


class CardFrame(ctk.CTkFrame):
    """Styled card with optional title."""

    def __init__(self, master, title: str = "", t: dict = None, **kwargs):
        t = t or {}
        kwargs.setdefault("fg_color", t.get("surface", "#1a1d2e"))
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", t.get("card_border", "#1e2235"))
        super().__init__(master, **kwargs)

        if title:
            ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=t.get("text_muted", "#94a3b8"),
            ).pack(anchor="w", padx=16, pady=(12, 0))


class SectionSeparator(ctk.CTkFrame):
    def __init__(self, master, t: dict = None, **kwargs):
        t = t or {}
        kwargs["height"] = 1
        kwargs["fg_color"] = t.get("border", "#2e3250")
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)


class ToggleRow(ctk.CTkFrame):
    """Label + switch in a horizontal row."""

    def __init__(
        self,
        master,
        label: str,
        variable: ctk.BooleanVar,
        t: dict = None,
        command: Callable = None,
        **kwargs,
    ):
        t = t or {}
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=t.get("text", "#f1f5f9"),
            anchor="w",
        ).pack(side="left", expand=True, fill="x")

        ctk.CTkSwitch(
            self,
            text="",
            variable=variable,
            onvalue=True,
            offvalue=False,
            width=44,
            height=22,
            progress_color=t.get("accent", "#6366f1"),
            button_color=t.get("text", "#f1f5f9"),
            fg_color=t.get("switch_off", "#374151"),
            command=command,
        ).pack(side="right")


class LabeledSlider(ctk.CTkFrame):
    """Slider with live value label."""

    def __init__(
        self,
        master,
        label: str,
        variable: ctk.IntVar,
        from_: int,
        to: int,
        t: dict = None,
        command: Callable = None,
        **kwargs,
    ):
        t = t or {}
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=t.get("text", "#f1f5f9"),
            anchor="w",
        ).pack(side="left")

        self._val_label = ctk.CTkLabel(
            header,
            textvariable=variable,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=t.get("accent", "#6366f1"),
        )
        self._val_label.pack(side="right")

        ctk.CTkSlider(
            self,
            variable=variable,
            from_=from_,
            to=to,
            number_of_steps=to - from_,
            progress_color=t.get("accent", "#6366f1"),
            button_color=t.get("accent", "#6366f1"),
            button_hover_color=t.get("accent_hover", "#4f46e5"),
            fg_color=t.get("surface2", "#252840"),
            command=command,
        ).pack(fill="x", pady=(4, 0))
