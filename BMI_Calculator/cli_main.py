import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FILE_NAME = "bmi_data.json"
FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

CATEGORY_RANGES = [
    (18.5, "Underweight"),
    (25.0, "Normal weight"),
    (30.0, "Overweight"),
    (float("inf"), "Obese"),
]


def calculate_bmi(weight_kg, height_cm):
    return weight_kg / ((height_cm / 100.0) ** 2)


def get_category(bmi):
    for limit, category in CATEGORY_RANGES:
        if bmi < limit:
            return category
    return "Unknown"


def load_data():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        messagebox.showerror("Storage Error", f"Unable to save BMI data:
{error}")


def get_user_names(data):
    return sorted({entry["user"] for entry in data if entry.get("user")})


def get_user_entries(data, user):
    return [entry for entry in data if entry.get("user") == user]


def get_stats(entries):
    if not entries:
        return None

    bmis = [entry["bmi"] for entry in entries]
    categories = {}
    for entry in entries:
        categories[entry["category"]] = categories.get(entry["category"], 0) + 1

    return {
        "count": len(entries),
        "average": sum(bmis) / len(bmis),
        "lowest": min(bmis),
        "highest": max(bmis),
        "categories": categories,
    }


class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Tracker")
        self.geometry("560x660")
        self.resizable(False, False)
        self.data = load_data()

        self.user_var = tk.StringVar(value="")
        self.weight_var = tk.StringVar(value="")
        self.height_var = tk.StringVar(value="")
        self.bmi_var = tk.StringVar(value="BMI: -")
        self.category_var = tk.StringVar(value="Category: -")
        self.status_var = tk.StringVar(value="Enter your details and press Calculate BMI.")
        self.stats_var = tk.StringVar(value="No historical data available.")

        self.create_widgets()
        self.update_user_list()

    def create_widgets(self):
        title_label = ttk.Label(self, text="BMI Calculator & Tracker", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(20, 10))

        user_frame = ttk.LabelFrame(self, text="User")
        user_frame.pack(fill="x", padx=20, pady=(0, 12))

        ttk.Label(user_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.user_combo = ttk.Combobox(user_frame, textvariable=self.user_var, values=[], width=30)
        self.user_combo.grid(row=0, column=1, padx=8, pady=8)
        self.user_combo.bind("<<ComboboxSelected>>", lambda event: self.update_stats())

        input_frame = ttk.LabelFrame(self, text="Measurements")
        input_frame.pack(fill="x", padx=20, pady=(0, 12))

        ttk.Label(input_frame, text="Weight (kg):").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.weight_entry = ttk.Entry(input_frame, textvariable=self.weight_var)
        self.weight_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(input_frame, text="Height (cm):").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.height_entry = ttk.Entry(input_frame, textvariable=self.height_var)
        self.height_entry.grid(row=1, column=1, padx=8, pady=8)

        result_frame = ttk.LabelFrame(self, text="Latest Result")
        result_frame.pack(fill="x", padx=20, pady=(0, 12))

        ttk.Label(result_frame, textvariable=self.bmi_var, font=("Segoe UI", 14)).pack(anchor="w", padx=12, pady=(10, 4))
        ttk.Label(result_frame, textvariable=self.category_var, font=("Segoe UI", 14)).pack(anchor="w", padx=12, pady=(0, 10))

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 12))

        calculate_button = ttk.Button(button_frame, text="Calculate BMI", command=self.on_calculate)
        calculate_button.grid(row=0, column=0, padx=8, pady=8)

        history_button = ttk.Button(button_frame, text="View History", command=self.show_history)
        history_button.grid(row=0, column=1, padx=8, pady=8)

        trend_button = ttk.Button(button_frame, text="BMI Trend", command=self.show_trend)
        trend_button.grid(row=0, column=2, padx=8, pady=8)

        clear_button = ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields)
        clear_button.grid(row=0, column=3, padx=8, pady=8)

        stats_frame = ttk.LabelFrame(self, text="User Statistics")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        ttk.Label(stats_frame, textvariable=self.stats_var, justify="left", wraplength=500).pack(fill="both", padx=12, pady=12)

        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=20, pady=(0, 10))
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

    def update_user_list(self):
        users = get_user_names(self.data)
        self.user_combo["values"] = users
        if users and not self.user_var.get():
            self.user_var.set(users[0])
        self.update_stats()

    def validate_inputs(self):
        user = self.user_var.get().strip()
        if not user:
            raise ValueError("Please enter a user name.")

        try:
            weight = float(self.weight_var.get())
        except ValueError:
            raise ValueError("Weight must be a number.")
        if weight <= 0 or weight > 600:
            raise ValueError("Weight must be between 1 and 600 kg.")

        try:
            height = float(self.height_var.get())
        except ValueError:
            raise ValueError("Height must be a number.")
        if height <= 0 or height > 300:
            raise ValueError("Height must be between 1 and 300 cm.")

        return user, weight, height

    def on_calculate(self):
        try:
            user, weight, height = self.validate_inputs()
        except ValueError as err:
            messagebox.showwarning("Input Error", str(err))
            return

        bmi = calculate_bmi(weight, height)
        category = get_category(bmi)

        self.bmi_var.set(f"BMI: {bmi:.2f}")
        self.category_var.set(f"Category: {category}")

        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "user": user,
            "weight_kg": weight,
            "height_cm": height,
            "bmi": round(bmi, 2),
            "category": category,
        }

        self.data.append(entry)
        save_data(self.data)
        self.update_user_list()
        self.update_stats()
        self.status_var.set(f"Saved BMI for {user} at {entry['date']}.")

    def show_history(self):
        user = self.user_var.get().strip()
        if not user:
            messagebox.showinfo("History", "Please enter or select a user name first.")
            return

        entries = get_user_entries(self.data, user)
        history_window = tk.Toplevel(self)
        history_window.title(f"BMI History - {user}")
        history_window.geometry("560x420")

        if not entries:
            ttk.Label(history_window, text="No history found for this user.", padding=12).pack()
            return

        text_widget = ScrolledText(history_window, wrap="word", state="normal", font=("Segoe UI", 11))
        text_widget.pack(fill="both", expand=True, padx=12, pady=12)

        entries_sorted = sorted(entries, key=lambda item: item["date"])
        for index, entry in enumerate(entries_sorted, start=1):
            text_widget.insert(
                "end",
                f"{index}. {entry['date']} | BMI: {entry['bmi']:.2f} | Category: {entry['category']}
"
                f"    Weight: {entry['weight_kg']} kg, Height: {entry['height_cm']} cm

"
            )

        text_widget.configure(state="disabled")

    def show_trend(self):
        user = self.user_var.get().strip()
        if not user:
            messagebox.showinfo("BMI Trend", "Please enter or select a user name first.")
            return

        entries = get_user_entries(self.data, user)
        if len(entries) < 2:
            messagebox.showinfo("BMI Trend", "At least two BMI records are needed to plot a trend.")
            return

        entries_sorted = sorted(entries, key=lambda item: item["date"])
        dates = [datetime.strptime(entry["date"], "%Y-%m-%d %H:%M") for entry in entries_sorted]
        bmis = [entry["bmi"] for entry in entries_sorted]

        plot_window = tk.Toplevel(self)
        plot_window.title(f"BMI Trend - {user}")
        plot_window.geometry("640x520")

        figure = plt.Figure(figsize=(7, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(dates, bmis, marker="o", linestyle="-", color="#1f77b4")
        ax.set_title(f"BMI Trend for {user}")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI")
        ax.grid(True, linestyle="--", alpha=0.4)
        figure.autofmt_xdate(rotation=35)

        canvas = FigureCanvasTkAgg(figure, plot_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def update_stats(self):
        user = self.user_var.get().strip()
        if not user:
            self.stats_var.set("Enter a user name to see statistics.")
            return

        entries = get_user_entries(self.data, user)
        stats = get_stats(entries)
        if not stats:
            self.stats_var.set("No historical data available for this user.")
            return

        category_lines = ", ".join(f"{name}: {count}" for name, count in stats["categories"].items())
        self.stats_var.set(
            f"Records: {stats['count']}
"
            f"Average BMI: {stats['average']:.2f}
"
            f"Lowest BMI: {stats['lowest']:.2f}
"
            f"Highest BMI: {stats['highest']:.2f}
"
            f"Category counts: {category_lines}"
        )

    def clear_fields(self):
        self.weight_var.set("")
        self.height_var.set("")
        self.bmi_var.set("BMI: -")
        self.category_var.set("Category: -")
        self.status_var.set("Fields cleared. Enter new values to calculate BMI.")


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
