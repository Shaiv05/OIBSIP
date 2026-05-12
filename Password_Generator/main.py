#!/usr/bin/env python3
"""
PassGen Pro — Entry point.
Run: python main.py
"""

import sys
import os

# Ensure the project root is on the path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from ui.app import PassGenApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = PassGenApp()
    app.mainloop()


if __name__ == "__main__":
    main()
