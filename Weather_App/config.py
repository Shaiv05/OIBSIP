"""Application configuration."""

from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"


load_dotenv(BASE_DIR / ".env")


class Config:
    """Centralized settings loaded from environment variables."""

    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    PORT = int(os.getenv("PORT", "5001"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG") == "1"
    WEATHER_CACHE_SECONDS = int(os.getenv("WEATHER_CACHE_SECONDS", "600"))
