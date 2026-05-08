"""
src/data/storage.py — Persistent storage with JSON backend, auto-backup, and CSV export.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
from datetime import datetime
from typing import List

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import DATA_FILE, BACKUP_DIR, DATA_DIR
from src.core.calculator import BMIRecord


# ── Ensure directories exist ──────────────────────────────────────────────────

def _ensure_dirs() -> None:
    os.makedirs(DATA_DIR,   exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


# ── Load / Save ───────────────────────────────────────────────────────────────

def load_records() -> List[BMIRecord]:
    """Load all records from disk. Returns [] on missing/corrupt file."""
    _ensure_dirs()
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, list):
            raise ValueError("Root element is not a list.")
        return [BMIRecord.from_dict(item) for item in raw]
    except (json.JSONDecodeError, ValueError, KeyError):
        # Corrupt data → back it up and return empty
        _backup_corrupt()
        return []


def save_records(records: List[BMIRecord]) -> None:
    """Atomically write records to disk (write-then-rename)."""
    _ensure_dirs()
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump([r.to_dict() for r in records], fh, indent=2)
    os.replace(tmp_path, DATA_FILE)


def create_backup() -> str:
    """Copy the data file to the backups folder; return backup path."""
    _ensure_dirs()
    if not os.path.exists(DATA_FILE):
        return ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"bmi_data_{timestamp}.json")
    shutil.copy2(DATA_FILE, dest)
    _prune_backups(keep=10)
    return dest


def _backup_corrupt() -> None:
    if os.path.exists(DATA_FILE):
        dest = DATA_FILE + f".corrupt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.move(DATA_FILE, dest)


def _prune_backups(keep: int = 10) -> None:
    """Remove oldest backup files, keeping only `keep` most recent."""
    files = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")],
        reverse=True,
    )
    for old in files[keep:]:
        os.remove(os.path.join(BACKUP_DIR, old))


# ── Query helpers ─────────────────────────────────────────────────────────────

def get_all_users(records: List[BMIRecord]) -> List[str]:
    return sorted({r.user for r in records if r.user})


def get_user_records(records: List[BMIRecord], user: str) -> List[BMIRecord]:
    return sorted(
        [r for r in records if r.user == user],
        key=lambda r: r.date,
    )


def delete_record(records: List[BMIRecord], user: str, date: str) -> List[BMIRecord]:
    """Return a new list with the matching record removed."""
    return [r for r in records if not (r.user == user and r.date == date)]


def delete_user(records: List[BMIRecord], user: str) -> List[BMIRecord]:
    return [r for r in records if r.user != user]


# ── Export ────────────────────────────────────────────────────────────────────

def export_csv(records: List[BMIRecord], path: str) -> str:
    """Export records to CSV; return the file path."""
    fieldnames = ["date", "user", "weight_kg", "height_cm", "bmi", "category", "unit_system", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = r.to_dict()
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    return path
