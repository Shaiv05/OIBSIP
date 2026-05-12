"""Persistent storage for password history and settings."""

import json
import os
from datetime import datetime
from pathlib import Path


APP_DIR = Path.home() / ".passgen_pro"
HISTORY_FILE = APP_DIR / "history.json"
SETTINGS_FILE = APP_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "length": 16,
    "use_upper": True,
    "use_lower": True,
    "use_digits": True,
    "use_symbols": True,
    "exclude_similar": False,
    "exclude_ambiguous": False,
    "exclude_custom": "",
    "no_consecutive_repeats": False,
    "avoid_patterns": False,
    "auto_copy": False,
    "auto_clear_clipboard": False,
    "auto_clear_delay": 30,
    "show_password": True,
    "mode": "strong",
    "passphrase_words": 4,
    "passphrase_separator": "-",
    "passphrase_capitalize": True,
    "passphrase_number": True,
    "passphrase_symbol": False,
    "theme": "dark",
}


def _ensure_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    _ensure_dir()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            result = dict(DEFAULT_SETTINGS)
            result.update(saved)
            return result
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    _ensure_dir()
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def load_history() -> list:
    _ensure_dir()
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(history: list) -> None:
    _ensure_dir()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def add_to_history(password: str, strength: str, entropy: float) -> dict:
    entry = {
        "id": datetime.now().isoformat(),
        "password": password,
        "strength": strength,
        "entropy": entropy,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "favorite": False,
    }
    history = load_history()
    history.insert(0, entry)
    if len(history) > 500:
        history = history[:500]
    save_history(history)
    return entry


def toggle_favorite(entry_id: str) -> list:
    history = load_history()
    for entry in history:
        if entry["id"] == entry_id:
            entry["favorite"] = not entry.get("favorite", False)
            break
    save_history(history)
    return history


def delete_entry(entry_id: str) -> list:
    history = load_history()
    history = [e for e in history if e["id"] != entry_id]
    save_history(history)
    return history


def clear_history() -> None:
    save_history([])


def export_history_txt(path: str, history: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("PassGen Pro - Password History Export\n")
        f.write("=" * 50 + "\n\n")
        for e in history:
            fav = " ★" if e.get("favorite") else ""
            f.write(f"[{e['timestamp']}]{fav}\n")
            f.write(f"  Password : {e['password']}\n")
            f.write(f"  Strength : {e['strength']}\n")
            f.write(f"  Entropy  : {e['entropy']} bits\n\n")


def export_history_json(path: str, history: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def import_settings_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = dict(DEFAULT_SETTINGS)
    result.update(data)
    return result


def export_settings_to_file(path: str, settings: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
