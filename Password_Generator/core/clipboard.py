"""Clipboard utilities with auto-clear support."""

import threading
import pyperclip


_clear_timer: threading.Timer | None = None


def copy_to_clipboard(text: str) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


from typing import Callable

def schedule_clear(delay_seconds: int, on_cleared: Callable | None = None) -> None:
    global _clear_timer
    cancel_clear()
    _clear_timer = threading.Timer(delay_seconds, _do_clear, args=[on_cleared])
    _clear_timer.daemon = True
    _clear_timer.start()


def cancel_clear() -> None:
    global _clear_timer
    if _clear_timer is not None:
        _clear_timer.cancel()
        _clear_timer = None


from typing import Callable, Optional

def _do_clear(on_cleared: Optional[Callable]) -> None:
    try:
        pyperclip.copy("")
    except Exception:
        pass
    if on_cleared:
        on_cleared()
