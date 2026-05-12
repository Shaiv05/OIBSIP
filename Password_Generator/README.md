# PassGen Pro

A professional, feature-rich password generator desktop application built with Python and CustomTkinter.

## Features

- **Secure generation** using Python's `secrets` module (not `random`)
- **Three modes**: Strong Password, Balanced Password, Memorable Passphrase
- **Character customization**: uppercase, lowercase, digits, symbols
- **Advanced filters**: exclude similar chars (O/0/I/l/1), ambiguous symbols, custom characters
- **Pattern controls**: no consecutive repeats, avoid sequential patterns
- **Security analysis**: strength level, entropy bits, estimated crack time, warnings
- **Clipboard**: one-click copy, optional auto-clear after configurable delay
- **Password history**: searchable, filterable, favorites, single-delete, bulk clear
- **Export**: history as TXT or JSON; settings as JSON
- **Import**: restore settings from JSON file
- **QR code**: generate a scannable QR for any password
- **Show/hide toggle** for the password field
- **Auto-copy** option after generation
- **Dark / Light theme** toggle
- **Keyboard shortcuts**: Enter = generate, Ctrl+C = copy, Ctrl+R = reset history, F5 = regenerate
- **Persistent settings** stored in `~/.passgen_pro/`

## Requirements

- Python 3.11+
- See `requirements.txt`

## Installation

```bash
cd password-generator
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Project Structure

```
password-generator/
├── main.py                  # Entry point
├── requirements.txt
├── core/
│   ├── generator.py         # Password / passphrase generation
│   ├── security.py          # Strength analysis & entropy
│   ├── clipboard.py         # Clipboard utilities
│   └── storage.py           # History & settings persistence
└── ui/
    ├── app.py               # Main application window
    ├── theme.py             # Color tokens for dark/light themes
    ├── widgets.py           # Reusable custom widgets
    ├── password_card.py     # Password display card
    ├── settings_card.py     # Generation settings card
    ├── security_card.py     # Security analysis card
    └── history_card.py      # Password history card
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter / F5 | Generate new password |
| Ctrl+C | Copy current password |
| Ctrl+R | Reset / clear history |

## Security Notes

- All passwords are generated using `secrets.SystemRandom` — cryptographically secure
- Entropy is calculated using Shannon entropy × password length
- Crack time estimates assume 10 billion guesses/second (high-end GPU cluster)
- Clipboard auto-clear is available to reduce exposure time
