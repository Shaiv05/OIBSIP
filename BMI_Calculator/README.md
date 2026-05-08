# ⚕ BMI Tracker Pro

> A polished, feature-rich BMI calculator and history tracker built with Python and Tkinter — dark-themed, multi-user, and GitHub-ready.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-pytest-orange)

---

## ✨ Features

| Feature | Details |
|---|---|
| **BMI Gauge** | Animated semi-circular gauge with colour-coded zones |
| **Multi-user** | Track unlimited users, each with independent history |
| **Metric & Imperial** | Toggle between kg/cm and lbs/ft·in at any time |
| **7-tier categories** | From Severely Underweight to Obese Class III |
| **Health tips** | Personalised advice per BMI category |
| **Ideal weight** | Calculated target range displayed instantly |
| **History viewer** | Scrollable table with per-record delete |
| **Trend chart** | matplotlib line chart with BMI zone bands |
| **CSV export** | One-click export of all records |
| **Auto-backup** | JSON snapshot saved to `data_store/backups/` |
| **Atomic writes** | Write-then-rename prevents corrupt data files |
| **Notes field** | Optional free-text annotation per entry |
| **Dark theme** | Cohesive dark UI throughout all windows |

---

## 🖥 Screenshots

> *Run the app to see the live dark-themed interface with the BMI gauge, statistics panel, and trend charts.*

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or newer
- `tkinter` (bundled with most Python distributions)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/bmi-tracker.git
cd bmi-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_calculator.py -v
```

---

## 📁 Project Structure

```
bmi-tracker/
├── main.py                     # Entry point
├── config.py                   # App-wide constants & theme colours
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── core/
│   │   ├── calculator.py       # BMI logic, stats, unit conversion
│   │   └── validators.py       # Input validation (raises ValidationError)
│   ├── data/
│   │   └── storage.py          # JSON persistence, backup, CSV export
│   └── ui/
│       ├── main_window.py      # Main app window + History + Trend popups
│       └── theme.py            # All ttk styles in one place
│
├── tests/
│   ├── test_calculator.py      # 25+ tests for calculation logic
│   ├── test_validators.py      # Validator edge cases
│   └── test_storage.py         # Storage round-trips, CSV, delete helpers
│
└── data_store/
    ├── bmi_data.json           # Auto-created; gitignored
    └── backups/                # Auto-created; gitignored
```

---

## 🏗 Architecture

The project follows an **MVC-inspired layered architecture**:

```
UI Layer (src/ui/)
    ↓  calls
Core Layer (src/core/)   ←  no UI imports
    ↓  uses
Data Layer (src/data/)   ←  no UI or core imports
    ↓  reads/writes
data_store/bmi_data.json
```

- **config.py** — single source of truth for colours, paths, categories
- **Atomic writes** — `save_records()` writes to a `.tmp` file then renames, preventing partial writes
- **Corrupt-file recovery** — bad JSON is moved aside; the app continues with an empty dataset
- **Backup pruning** — only the 10 most recent backups are kept automatically

---

## 🔧 Configuration

Edit `config.py` to customise:

- `BMI_CATEGORIES` — adjust thresholds or add new bands
- `HEALTH_TIPS` — personalise the advice shown per category
- `THEME` — change any colour in the dark palette
- `BACKUP_DIR` / `DATA_FILE` — relocate data storage

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `tkinter` | GUI (stdlib) |
| `matplotlib` | Trend chart rendering |
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📜 License

MIT — see [LICENSE](LICENSE) for details.

---

*Built with Python • Tkinter • matplotlib*
