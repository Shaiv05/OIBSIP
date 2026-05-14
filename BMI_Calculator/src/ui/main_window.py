"""
src/ui/main_window.py — Main BMI Tracker window with dark theme.
"""
from __future__ import annotations

import math
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config import APP_NAME, APP_VERSION, THEME, FONT_FAMILY
from src.core.calculator import (
    BMIRecord, calculate_bmi, get_category,
    get_health_tips, ideal_weight_range,
    lbs_to_kg, inches_to_cm, feet_inches_to_cm, kg_to_lbs, cm_to_inches,
    compute_stats,
)
from src.core.validators import (
    ValidationError, validate_name,
    validate_weight_kg, validate_weight_lbs,
    validate_height_cm, validate_height_feet,
)
from src.data.storage import (
    load_records, save_records, create_backup,
    get_all_users, get_user_records, delete_record, delete_user,
    export_csv,
)
from src.ui.theme import apply_ttk_styles


# ── Helper: rounded rectangle on canvas ──────────────────────────────────────

def _rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    pts = [
        x1+r, y1,  x2-r, y1,
        x2, y1,    x2, y1+r,
        x2, y2-r,  x2, y2,
        x2-r, y2,  x1+r, y2,
        x1, y2,    x1, y2-r,
        x1, y1+r,  x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ── BMI Gauge Canvas Widget ───────────────────────────────────────────────────

class BMIGauge(tk.Canvas):
    """Semi-circular gauge that visualises the BMI value."""

    SEGMENTS = [
        (0,   16,   "#B91C1C"),
        (16,  18.5, "#F87171"),
        (18.5,25,   "#34D399"),
        (25,  30,   "#FBBF24"),
        (30,  35,   "#F59E0B"),
        (35,  40,   "#F87171"),
        (40,  50,   "#B91C1C"),
    ]
    BMI_MIN, BMI_MAX = 10, 50

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=THEME["surface"], highlightthickness=0,
                         width=380, height=210, **kwargs)
        self._bmi: float | None = None
        self._draw_static()

    def _angle(self, bmi: float) -> float:
        """Map BMI to arc angle (180 = left, 0 = right, in degrees)."""
        clamped = max(self.BMI_MIN, min(self.BMI_MAX, bmi))
        frac = (clamped - self.BMI_MIN) / (self.BMI_MAX - self.BMI_MIN)
        return 180 - frac * 180   # 180° → 0°

    def _draw_static(self):
        self.delete("static")
        cx, cy, r_out, r_in = 190, 195, 165, 105

        for bmi_lo, bmi_hi, colour in self.SEGMENTS:
            a_start = self._angle(bmi_lo)
            a_end   = self._angle(bmi_hi)
            start_tk = a_start
            extent_tk = a_start - a_end

            # Outer arc
            self.create_arc(
                cx - r_out, cy - r_out, cx + r_out, cy + r_out,
                start=a_end, extent=extent_tk,
                outline="", fill=colour, style="pieslice",
                tags="static",
            )

        # Mask inner circle to make it a ring
        self.create_oval(
            cx - r_in, cy - r_in, cx + r_in, cy + r_in,
            fill=THEME["surface"], outline="", tags="static",
        )

        # Bottom cutoff mask (rectangle below centre)
        self.create_rectangle(0, cy, 380, 210, fill=THEME["surface"],
                              outline="", tags="static")

        # Tick labels
        for bmi_val, label in [(10, "10"), (18.5, "18.5"), (25, "25"),
                                (30, "30"), (40, "40"), (50, "50")]:
            ang = math.radians(self._angle(bmi_val))
            lx = cx + (r_out + 16) * math.cos(ang)
            ly = cy - (r_out + 16) * math.sin(ang)
            self.create_text(lx, ly, text=label,
                             fill=THEME["text_muted"], font=(FONT_FAMILY, 8),
                             tags="static")

    def update_bmi(self, bmi: float | None):
        self._bmi = bmi
        self.delete("needle", "bmi_text")
        cx, cy = 190, 195

        if bmi is None:
            self.create_text(cx, cy - 30, text="—",
                             fill=THEME["text_muted"],
                             font=(FONT_FAMILY, 28, "bold"), tags="bmi_text")
            return

        # Draw needle
        ang_deg = self._angle(bmi)
        ang_rad = math.radians(ang_deg)
        nx = cx + 135 * math.cos(ang_rad)
        ny = cy - 135 * math.sin(ang_rad)
        self.create_line(cx, cy, nx, ny, fill="#E8ECF4",
                         width=2, tags="needle", capstyle="round")
        # Glow center dot
        self.create_oval(cx-8, cy-8, cx+8, cy+8,
                         fill=THEME["accent"], outline="#3D5090",
                         width=3, tags="needle")

        # BMI text in centre
        self.create_text(cx, cy - 42, text=f"{bmi:.1f}",
                         fill=THEME["text"],
                         font=(FONT_FAMILY, 28, "bold"), tags="bmi_text")


# ── Glow Button — canvas-based with ring/glow hover effect ───────────────────

class GlowButton(tk.Canvas):
    """A styled button with a soft glowing ring on hover."""

    def __init__(self, parent, text="", command=None, style="primary",
                 width=160, height=40, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=THEME["bg"], highlightthickness=0, **kwargs)
        self._text = text
        self._command = command
        self._width = width
        self._height = height
        self._hovered = False
        self._pressed = False

        # Style presets (ring colors are muted variants for glow effect)
        styles = {
            "primary": {"bg": THEME["accent"], "fg": "#ffffff",
                        "hover": "#5A7AE8", "ring": "#4A6ACC"},
            "danger":  {"bg": THEME["danger"], "fg": "#ffffff",
                        "hover": "#E55555", "ring": "#C55050"},
            "ghost":   {"bg": THEME["surface2"], "fg": THEME["text"],
                        "hover": THEME["border"], "ring": "#3D5090"},
        }
        self._s = styles.get(style, styles["primary"])

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h, r = self._width, self._height, 12
        pad = 4  # ring padding

        bg = self._s["hover"] if self._hovered else self._s["bg"]
        if self._pressed:
            bg = self._s["hover"]

        # Outer glow ring (visible on hover)
        if self._hovered:
            _rounded_rect(self, pad-3, pad-3, w-pad+3, h-pad+3, r+3,
                          fill="", outline=self._s["ring"], width=2)

        # Main button body
        _rounded_rect(self, pad, pad, w-pad, h-pad, r,
                      fill=bg, outline="")

        # Text
        self.create_text(w/2, h/2, text=self._text,
                         fill=self._s["fg"],
                         font=(FONT_FAMILY, 10, "bold"))

    def _on_enter(self, e):
        self._hovered = True
        self._draw()

    def _on_leave(self, e):
        self._hovered = False
        self._pressed = False
        self._draw()

    def _on_press(self, e):
        self._pressed = True
        self._draw()

    def _on_release(self, e):
        self._pressed = False
        self._hovered = False
        self._draw()
        if self._command:
            self._command()

    def configure_bg(self, bg):
        """Update the parent background color for this button."""
        super().configure(bg=bg)
        self._draw()


# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}")

        # ── macOS DPI / Retina scaling fix ────────────────────────────────
        if sys.platform == "darwin":
            try:
                self.tk.call("tk", "scaling", 1.4)   # bump up for Retina
            except tk.TclError:
                pass

        self.geometry("960x920")
        self.minsize(900, 750)
        self.resizable(True, True)
        self.configure(bg=THEME["bg"])

        # State
        self.records = load_records()
        self.unit_system = tk.StringVar(value="metric")   # "metric" | "imperial"
        self.user_var    = tk.StringVar()
        self.w_var       = tk.StringVar()
        self.h_var       = tk.StringVar()
        self.h_in_var    = tk.StringVar(value="0")        # inches field (imperial)

        # Apply styles
        self.style = ttk.Style(self)
        apply_ttk_styles(self.style)

        self._build_ui()
        self._refresh_user_list()

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        T = THEME

        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=T["surface"], height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Title group
        title_frame = tk.Frame(hdr, bg=T["surface"])
        title_frame.pack(side="left", padx=32, pady=18)
        tk.Label(title_frame, text="⚕  BMI Tracker Pro", bg=T["surface"],
                 fg=T["text"], font=(FONT_FAMILY, 20, "bold")).pack(
            side="left")
        tk.Label(title_frame, text=f"  v{APP_VERSION}", bg=T["surface"],
                 fg=T["text_muted"], font=(FONT_FAMILY, 10)).pack(
            side="left", padx=(6, 0))

        # Header buttons with glow
        hdr_btn_frame = tk.Frame(hdr, bg=T["surface"])
        hdr_btn_frame.pack(side="right", padx=20, pady=14)

        backup_btn = GlowButton(hdr_btn_frame, text="💾  Backup",
                                command=self._do_backup, style="ghost", width=130, height=36)
        backup_btn.configure(bg=T["surface"])
        backup_btn.pack(side="right", padx=6)

        export_btn = GlowButton(hdr_btn_frame, text="📤  Export CSV",
                                command=self._do_export_csv, style="ghost", width=140, height=36)
        export_btn.configure(bg=T["surface"])
        export_btn.pack(side="right", padx=6)

        # ── Thin accent line with subtle glow ─────────────────────────────
        accent_line = tk.Canvas(self, bg=T["bg"], height=4, highlightthickness=0)
        accent_line.pack(fill="x")
        accent_line.create_rectangle(0, 0, 2000, 4, fill=T["accent"], outline="")

        # ── Scrollable main body ─────────────────────────────────────────
        outer = tk.Frame(self, bg=T["bg"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=T["bg"], highlightthickness=0)
        v_scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=T["bg"])
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_body_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        body.bind("<Configure>", _on_body_configure)

        def _on_canvas_configure(event):
            canvas.itemconfig(body_win, width=event.width)
        canvas.configure(width=900)
        canvas.bind("<Configure>", _on_canvas_configure)

        # macOS mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * event.delta, "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Inner padding wrapper
        body_inner = tk.Frame(body, bg=T["bg"])
        body_inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Unit toggle ──────────────────────────────────────────────────
        unit_row = tk.Frame(body_inner, bg=T["bg"])
        unit_row.pack(fill="x", pady=(0, 20))
        tk.Label(unit_row, text="Unit system:", bg=T["bg"], fg=T["text_muted"],
                 font=(FONT_FAMILY, 11)).pack(side="left")
        for val, lbl in [("metric", "  Metric (kg / cm)  "),
                          ("imperial", "  Imperial (lbs / ft·in)  ")]:
            rb = tk.Radiobutton(
                unit_row, text=lbl, variable=self.unit_system, value=val,
                bg=T["surface"], fg=T["text"], selectcolor=T["accent"],
                activebackground=T["surface"], activeforeground=T["text"],
                font=(FONT_FAMILY, 13), bd=0, indicatoron=True,
                command=self._on_unit_change,
            )
            rb.pack(side="left", padx=8)

        # ── 2-column layout: left=inputs, right=gauge ────────────────────
        cols = tk.Frame(body_inner, bg=T["bg"])
        cols.pack(fill="x")

        left = tk.Frame(cols, bg=T["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right = tk.Frame(cols, bg=T["bg"])
        right.pack(side="right")

        # ── Gauge ────────────────────────────────────────────────────────
        gauge_card = tk.Frame(right, bg=T["surface"], padx=16, pady=16,
                              highlightbackground=T["border"], highlightthickness=1)
        gauge_card.pack()
        self.gauge = BMIGauge(gauge_card)
        self.gauge.pack(pady=(4, 0))

        self.category_lbl = tk.Label(
            gauge_card, text="——", bg=T["surface"],
            fg=T["text_muted"], font=(FONT_FAMILY, 15, "bold"))
        self.category_lbl.pack(pady=(6, 0))

        self.ideal_lbl = tk.Label(
            gauge_card, text="", bg=T["surface"],
            fg=T["text_muted"], font=(FONT_FAMILY, 10))
        self.ideal_lbl.pack()

        # ── Input card ───────────────────────────────────────────────────
        inp_card = tk.Frame(left, bg=T["surface"], padx=28, pady=24,
                            highlightbackground=T["border"], highlightthickness=1)
        inp_card.pack(fill="x")

        self._section_label(inp_card, "👤  User")
        self.user_combo = ttk.Combobox(inp_card, textvariable=self.user_var,
                                       width=30, font=(FONT_FAMILY, 13))
        self.user_combo.pack(fill="x", pady=(6, 16))
        self.user_combo.bind("<<ComboboxSelected>>", lambda _: self._on_user_select())

        self._section_label(inp_card, "⚖️  Weight")
        w_row = tk.Frame(inp_card, bg=T["surface"])
        w_row.pack(fill="x", pady=(6, 16))
        self.weight_entry = ttk.Entry(w_row, textvariable=self.w_var, width=18,
                                      font=(FONT_FAMILY, 13))
        self.weight_entry.pack(side="left")
        self.weight_unit_lbl = tk.Label(w_row, text="kg", bg=T["surface"],
                                        fg=T["text_muted"], font=(FONT_FAMILY, 12))
        self.weight_unit_lbl.pack(side="left", padx=8)

        self._section_label(inp_card, "📏  Height")
        h_row = tk.Frame(inp_card, bg=T["surface"])
        h_row.pack(fill="x", pady=(6, 16))
        self.height_entry = ttk.Entry(h_row, textvariable=self.h_var, width=12,
                                      font=(FONT_FAMILY, 13))
        self.height_entry.pack(side="left")
        self.height_unit_lbl = tk.Label(h_row, text="cm", bg=T["surface"],
                                        fg=T["text_muted"], font=(FONT_FAMILY, 12))
        self.height_unit_lbl.pack(side="left", padx=8)

        # Imperial inches sub-field (hidden initially)
        self.inches_frame = tk.Frame(h_row, bg=T["surface"])
        self.inches_entry = ttk.Entry(self.inches_frame, textvariable=self.h_in_var,
                                      width=6, font=(FONT_FAMILY, 13))
        self.inches_entry.pack(side="left")
        tk.Label(self.inches_frame, text="in", bg=T["surface"],
                 fg=T["text_muted"], font=(FONT_FAMILY, 12)).pack(side="left", padx=6)

        # Notes
        self._section_label(inp_card, "📝  Notes  (optional)")
        self.notes_entry = ttk.Entry(inp_card, font=(FONT_FAMILY, 12), width=34)
        self.notes_entry.pack(fill="x", pady=(6, 0))

        # ── Action buttons ───────────────────────────────────────────────
        btn_row = tk.Frame(body_inner, bg=T["bg"])
        btn_row.pack(fill="x", pady=22)

        calc_btn = GlowButton(btn_row, text="✔  Calculate & Save",
                              command=self._on_calculate, style="primary",
                              width=185, height=42)
        calc_btn.pack(side="left", padx=(0, 8))

        hist_btn = GlowButton(btn_row, text="📋  History",
                              command=self._show_history, style="ghost",
                              width=130, height=42)
        hist_btn.pack(side="left", padx=(0, 8))

        trend_btn = GlowButton(btn_row, text="📈  Trend Chart",
                               command=self._show_trend, style="ghost",
                               width=145, height=42)
        trend_btn.pack(side="left", padx=(0, 8))

        del_btn = GlowButton(btn_row, text="🗑  Delete User",
                             command=self._delete_user, style="danger",
                             width=150, height=42)
        del_btn.pack(side="right")

        clear_btn = GlowButton(btn_row, text="✖  Clear",
                               command=self._clear, style="ghost",
                               width=110, height=42)
        clear_btn.pack(side="right", padx=(0, 8))

        # ── Health tip card ──────────────────────────────────────────────
        tip_card = tk.Frame(body_inner, bg=T["surface2"], padx=24, pady=18,
                            highlightbackground=T["border"], highlightthickness=1)
        tip_card.pack(fill="x", pady=(0, 18))
        tk.Label(tip_card, text="💡  Health Tips", bg=T["surface2"],
                 fg=T["accent"], font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")
        self.tip_lbl = tk.Label(tip_card, text="Calculate your BMI to see personalised tips.",
                                bg=T["surface2"], fg=T["text_muted"],
                                font=(FONT_FAMILY, 11), wraplength=820, justify="left")
        self.tip_lbl.pack(anchor="w", pady=(8, 0))

        # ── Stats card ───────────────────────────────────────────────────
        stat_card = tk.Frame(body_inner, bg=T["surface"], padx=28, pady=20,
                             highlightbackground=T["border"], highlightthickness=1)
        stat_card.pack(fill="x")
        tk.Label(stat_card, text="📊  Your Statistics", bg=T["surface"],
                 fg=T["text"], font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")
        self.stats_lbl = tk.Label(stat_card, text="Select a user to see stats.",
                                  bg=T["surface"], fg=T["text_muted"],
                                  font=(FONT_FAMILY, 11), justify="left")
        self.stats_lbl.pack(anchor="w", pady=(10, 0))

        # ── Status bar ───────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Label(self, textvariable=self.status_var,
                              bg=T["surface"], fg=T["text_muted"],
                              font=(FONT_FAMILY, 9), anchor="w", padx=24, pady=10)
        status_bar.pack(fill="x", side="bottom")

    def _section_label(self, parent, text: str):
        tk.Label(parent, text=text, bg=THEME["surface"],
                 fg=THEME["text_muted"], font=(FONT_FAMILY, 11, "bold")).pack(
            anchor="w", pady=(0, 4))

    # ── Event handlers ───────────────────────────────────────────────────────

    def _on_unit_change(self):
        sys = self.unit_system.get()
        if sys == "metric":
            self.weight_unit_lbl.config(text="kg")
            self.height_unit_lbl.config(text="cm")
            self.inches_frame.pack_forget()
        else:
            self.weight_unit_lbl.config(text="lbs")
            self.height_unit_lbl.config(text="ft")
            self.inches_frame.pack(side="left")
        self.w_var.set("")
        self.h_var.set("")
        self.h_in_var.set("0")

    def _on_user_select(self):
        self._refresh_stats()

    def _on_calculate(self):
        # Validate name
        try:
            user = validate_name(self.user_var.get())
        except ValidationError as e:
            messagebox.showwarning("Input Error", str(e), parent=self)
            return

        # Validate weight / height based on unit system
        try:
            if self.unit_system.get() == "metric":
                weight_kg = validate_weight_kg(self.w_var.get())
                height_cm = validate_height_cm(self.h_var.get())
            else:
                weight_lbs = validate_weight_lbs(self.w_var.get())
                ft, ins = validate_height_feet(self.h_var.get(), self.h_in_var.get())
                weight_kg = lbs_to_kg(weight_lbs)
                height_cm = feet_inches_to_cm(ft, ins)
        except ValidationError as e:
            messagebox.showwarning("Input Error", str(e), parent=self)
            return

        bmi = calculate_bmi(weight_kg, height_cm)
        category, colour, emoji = get_category(bmi)
        notes = self.notes_entry.get().strip()

        record = BMIRecord(
            user=user,
            weight_kg=weight_kg,
            height_cm=height_cm,
            bmi=bmi,
            category=category,
            unit_system=self.unit_system.get(),
            notes=notes,
        )

        self.records.append(record)
        save_records(self.records)

        # Update gauge
        self.gauge.update_bmi(bmi)
        self.category_lbl.config(text=f"{emoji}  {category}", fg=colour)

        # Ideal weight
        lo, hi = ideal_weight_range(height_cm)
        if self.unit_system.get() == "imperial":
            lo_d, hi_d = kg_to_lbs(lo), kg_to_lbs(hi)
            self.ideal_lbl.config(text=f"Ideal: {lo_d:.1f}–{hi_d:.1f} lbs")
        else:
            self.ideal_lbl.config(text=f"Ideal weight: {lo}–{hi} kg")

        # Health tips
        tips = get_health_tips(category)
        self.tip_lbl.config(text="  •  " + "\n  •  ".join(tips))

        self._refresh_user_list(select=user)
        self._refresh_stats()
        self.status_var.set(
            f"Saved BMI {bmi:.2f} ({category}) for {user} at {record.date}.")

    def _clear(self):
        self.w_var.set("")
        self.h_var.set("")
        self.h_in_var.set("0")
        self.notes_entry.delete(0, tk.END)
        self.gauge.update_bmi(None)
        self.category_lbl.config(text="——", fg=THEME["text_muted"])
        self.ideal_lbl.config(text="")
        self.tip_lbl.config(text="Calculate your BMI to see personalised tips.")
        self.status_var.set("Fields cleared.")

    def _delete_user(self):
        user = self.user_var.get().strip()
        if not user:
            messagebox.showinfo("Delete User", "Select a user first.", parent=self)
            return
        if not messagebox.askyesno("Delete User",
                                   f"Delete ALL records for '{user}'?\nThis cannot be undone.",
                                   parent=self):
            return
        self.records = delete_user(self.records, user)
        save_records(self.records)
        self._refresh_user_list()
        self._clear()
        self.status_var.set(f"Deleted all records for {user}.")

    def _do_backup(self):
        path = create_backup()
        if path:
            messagebox.showinfo("Backup", f"Backup saved:\n{path}", parent=self)
        else:
            messagebox.showinfo("Backup", "No data to back up.", parent=self)

    def _do_export_csv(self):
        if not self.records:
            messagebox.showinfo("Export", "No data to export.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="bmi_export.csv",
            parent=self,
        )
        if path:
            export_csv(self.records, path)
            self.status_var.set(f"Exported {len(self.records)} records → {path}")

    # ── History window ───────────────────────────────────────────────────────

    def _show_history(self):
        user = self.user_var.get().strip()
        if not user:
            messagebox.showinfo("History", "Select a user first.", parent=self)
            return
        records = get_user_records(self.records, user)
        HistoryWindow(self, user, records, self._on_record_deleted)

    def _on_record_deleted(self, user: str, date: str):
        self.records = delete_record(self.records, user, date)
        save_records(self.records)
        self._refresh_stats()
        self.status_var.set(f"Deleted record for {user} at {date}.")

    # ── Trend window ─────────────────────────────────────────────────────────

    def _show_trend(self):
        user = self.user_var.get().strip()
        if not user:
            messagebox.showinfo("Trend", "Select a user first.", parent=self)
            return
        records = get_user_records(self.records, user)
        if len(records) < 2:
            messagebox.showinfo("Trend",
                                "Need at least 2 records to show a trend.", parent=self)
            return
        TrendWindow(self, user, records)

    # ── Refresh helpers ──────────────────────────────────────────────────────

    def _refresh_user_list(self, select: str | None = None):
        users = get_all_users(self.records)
        self.user_combo["values"] = users
        if select:
            self.user_var.set(select)
        elif users and not self.user_var.get():
            self.user_var.set(users[0])
        self._refresh_stats()

    def _refresh_stats(self):
        user = self.user_var.get().strip()
        if not user:
            self.stats_lbl.config(text="Select a user to see stats.")
            return
        recs = get_user_records(self.records, user)
        stats = compute_stats(recs)
        if not stats:
            self.stats_lbl.config(text="No data for this user yet.")
            return

        trend_txt = ""
        if stats["trend"] is not None:
            delta = stats["trend"]
            trend_txt = f"  │  Trend vs prev: {'▲' if delta > 0 else '▼'} {abs(delta):.2f}"

        cats = "  │  ".join(f"{k}: {v}" for k, v in stats["categories"].items())
        self.stats_lbl.config(
            text=(
                f"Records: {stats['count']}  │  "
                f"Avg BMI: {stats['average']:.2f}  │  "
                f"Low: {stats['lowest']:.2f}  │  "
                f"High: {stats['highest']:.2f}{trend_txt}\n"
                f"Categories — {cats}"
            )
        )


# ── History Popup ─────────────────────────────────────────────────────────────

class HistoryWindow(tk.Toplevel):
    def __init__(self, parent, user: str, records, delete_callback):
        super().__init__(parent)
        self.title(f"History — {user}")
        self.geometry("640x480")
        self.configure(bg=THEME["bg"])
        self.records = records
        self.delete_callback = delete_callback
        self.user = user
        self._build(user, records)

    def _build(self, user, records):
        T = THEME
        tk.Label(self, text=f"BMI History for {user}",
                 bg=T["bg"], fg=T["text"],
                 font=(FONT_FAMILY, 14, "bold")).pack(pady=(20, 10), padx=24, anchor="w")

        cols_frame = tk.Frame(self, bg=T["bg"])
        cols_frame.pack(fill="both", expand=True, padx=24)

        scrollbar = ttk.Scrollbar(cols_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            cols_frame,
            columns=("date", "bmi", "weight", "height", "category", "notes"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=16,
            style="History.Treeview",
        )
        scrollbar.config(command=self.tree.yview)

        # Style the treeview dark
        s = ttk.Style(self)
        s.configure("History.Treeview",
                     background=T["surface"], foreground=T["text"],
                     fieldbackground=T["surface"], rowheight=26,
                     font=(FONT_FAMILY, 9))
        s.configure("History.Treeview.Heading",
                     background=T["surface2"], foreground=T["accent"],
                     font=(FONT_FAMILY, 9, "bold"))
        s.map("History.Treeview",
              background=[("selected", T["accent"])],
              foreground=[("selected", "#ffffff")])

        headers = [("date","Date",140), ("bmi","BMI",60),
                   ("weight","Weight",70), ("height","Height",70),
                   ("category","Category",130), ("notes","Notes",120)]
        for col, label, w in headers:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=w, anchor="center")

        for r in reversed(records):
            self.tree.insert("", "end", values=(
                r.date, f"{r.bmi:.2f}",
                f"{r.weight_kg:.1f} kg", f"{r.height_cm:.1f} cm",
                r.category, r.notes or "—",
            ))
        self.tree.pack(fill="both", expand=True)

        btn_row = tk.Frame(self, bg=T["bg"])
        btn_row.pack(fill="x", padx=24, pady=14)

        del_sel_btn = GlowButton(btn_row, text="🗑  Delete Selected",
                                  command=self._delete_selected, style="danger",
                                  width=170, height=38)
        del_sel_btn.pack(side="left")

        close_btn = GlowButton(btn_row, text="✖  Close",
                               command=self.destroy, style="ghost",
                               width=110, height=38)
        close_btn.pack(side="right")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        date = item["values"][0]
        if messagebox.askyesno("Delete", f"Delete record dated {date}?", parent=self):
            self.tree.delete(sel[0])
            self.delete_callback(self.user, date)


# ── Trend Chart Popup ─────────────────────────────────────────────────────────

class TrendWindow(tk.Toplevel):
    def __init__(self, parent, user: str, records):
        super().__init__(parent)
        self.title(f"BMI Trend — {user}")
        self.geometry("720x500")
        self.configure(bg=THEME["bg"])
        self._build(user, records)

    def _build(self, user, records):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from datetime import datetime as dt
        except ImportError:
            tk.Label(self, text="matplotlib not installed.\nRun: pip install matplotlib",
                     bg=THEME["bg"], fg=THEME["danger"],
                     font=(FONT_FAMILY, 12)).pack(expand=True)
            return

        T = THEME
        dates = [dt.strptime(r.date, "%Y-%m-%d %H:%M") for r in records]
        bmis  = [r.bmi for r in records]

        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=T["surface"])
        ax.set_facecolor(T["surface"])

        # Colour bands
        for lo, hi, colour in [(0, 18.5, "#e74c3c33"), (18.5, 25, "#2ecc7133"),
                                (25, 30, "#f39c1233"), (30, 100, "#e74c3c33")]:
            ax.axhspan(lo, hi, facecolor=colour, linewidth=0)

        ax.plot(dates, bmis, color=T["accent"], linewidth=2.5,
                marker="o", markersize=7, markerfacecolor="#ffffff",
                markeredgecolor=T["accent"], markeredgewidth=2)

        # Annotations on each point
        for d, b in zip(dates, bmis):
            ax.annotate(f"{b:.1f}", (d, b),
                        textcoords="offset points", xytext=(0, 10),
                        ha="center", color=T["text"], fontsize=8)

        ax.set_title(f"BMI Trend for {user}", color=T["text"], fontsize=13, fontweight="bold")
        ax.set_xlabel("Date", color=T["text_muted"], fontsize=10)
        ax.set_ylabel("BMI", color=T["text_muted"], fontsize=10)
        ax.tick_params(colors=T["text_muted"], which="both")
        for spine in ax.spines.values():
            spine.set_edgecolor(T["border"])
        ax.grid(True, linestyle="--", alpha=0.25, color=T["border"])
        fig.autofmt_xdate(rotation=25)

        # Legend bands
        from matplotlib.patches import Patch
        legend_items = [
            Patch(color="#e74c3c66", label="Underweight / Obese"),
            Patch(color="#f39c1266", label="Overweight"),
            Patch(color="#2ecc7166", label="Normal"),
        ]
        ax.legend(handles=legend_items, facecolor=T["surface"],
                  edgecolor=T["border"], labelcolor=T["text"], fontsize=8,
                  loc="upper right")

        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        canvas.draw()