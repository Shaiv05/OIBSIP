"""
main.py — Entry point for BMI Tracker Pro.

Run:
    python main.py
"""
import sys
import os

# Ensure project root is on the path when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow


def main() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
