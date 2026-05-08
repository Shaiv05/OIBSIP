"""
tests/test_storage.py — Unit tests for the storage layer.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.core.calculator import BMIRecord
from src.data import storage as st


def _make_record(user="Alice", bmi=22.5, date="2024-01-01 10:00") -> BMIRecord:
    return BMIRecord(user=user, weight_kg=70, height_cm=175,
                     bmi=bmi, category="Normal Weight", date=date)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def patch_paths(tmp_path, monkeypatch):
    """Redirect all file I/O to a temp directory for each test."""
    data_dir   = str(tmp_path / "data")
    backup_dir = str(tmp_path / "backups")
    data_file  = str(tmp_path / "data" / "bmi_data.json")

    monkeypatch.setattr(st, "DATA_DIR",   data_dir)
    monkeypatch.setattr(st, "BACKUP_DIR", backup_dir)
    monkeypatch.setattr(st, "DATA_FILE",  data_file)
    yield


# ── load_records ──────────────────────────────────────────────────────────────

class TestLoadRecords:
    def test_missing_file_returns_empty(self):
        assert st.load_records() == []

    def test_valid_file(self):
        records = [_make_record()]
        st.save_records(records)
        loaded = st.load_records()
        assert len(loaded) == 1
        assert loaded[0].user == "Alice"

    def test_corrupt_file_returns_empty(self, monkeypatch):
        os.makedirs(os.path.dirname(st.DATA_FILE), exist_ok=True)
        with open(st.DATA_FILE, "w") as f:
            f.write("{{not json}}")
        result = st.load_records()
        assert result == []


# ── save_records ──────────────────────────────────────────────────────────────

class TestSaveRecords:
    def test_saves_and_reloads(self):
        records = [_make_record("Bob", 27.1)]
        st.save_records(records)
        loaded = st.load_records()
        assert loaded[0].user == "Bob"
        assert loaded[0].bmi == 27.1

    def test_empty_list(self):
        st.save_records([])
        assert st.load_records() == []

    def test_multiple_records(self):
        records = [_make_record("A"), _make_record("B")]
        st.save_records(records)
        assert len(st.load_records()) == 2


# ── Query helpers ─────────────────────────────────────────────────────────────

class TestQueryHelpers:
    def setup_method(self):
        self.records = [
            _make_record("Alice", date="2024-01-01 09:00"),
            _make_record("Alice", date="2024-01-02 10:00"),
            _make_record("Bob",   date="2024-01-01 08:00"),
        ]

    def test_get_all_users(self):
        users = st.get_all_users(self.records)
        assert users == ["Alice", "Bob"]

    def test_get_user_records(self):
        alice_recs = st.get_user_records(self.records, "Alice")
        assert len(alice_recs) == 2

    def test_get_user_records_sorted(self):
        alice_recs = st.get_user_records(self.records, "Alice")
        assert alice_recs[0].date < alice_recs[1].date

    def test_delete_record(self):
        updated = st.delete_record(self.records, "Bob", "2024-01-01 08:00")
        assert all(r.user != "Bob" for r in updated)
        assert len(updated) == 2

    def test_delete_user(self):
        updated = st.delete_user(self.records, "Alice")
        assert len(updated) == 1
        assert updated[0].user == "Bob"


# ── CSV export ────────────────────────────────────────────────────────────────

class TestExportCSV:
    def test_creates_file(self, tmp_path):
        records = [_make_record("Alice")]
        path = str(tmp_path / "export.csv")
        st.export_csv(records, path)
        assert os.path.exists(path)

    def test_csv_header(self, tmp_path):
        import csv
        records = [_make_record()]
        path = str(tmp_path / "export.csv")
        st.export_csv(records, path)
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            assert "bmi" in reader.fieldnames
            assert "user" in reader.fieldnames

    def test_csv_row_count(self, tmp_path):
        import csv
        records = [_make_record("A"), _make_record("B")]
        path = str(tmp_path / "export.csv")
        st.export_csv(records, path)
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
