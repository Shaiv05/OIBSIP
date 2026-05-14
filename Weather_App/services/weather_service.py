"""OpenWeatherMap API handling, parsing, and caching."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os
import time
from typing import Any

import requests

from config import Config


class WeatherServiceError(Exception):
    """Weather service error with a user-safe message."""


class WeatherService:
    """Fetches live weather efficiently and caches successful metric responses."""

    CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, api_key: str | None = None, ttl_seconds: int = 600):
        self.api_key = (api_key or Config.OPENWEATHER_API_KEY).strip()
        self.ttl_seconds = ttl_seconds
        self.timeout = 10
        self._cache: dict[str, dict[str, Any]] = {}

    def get_weather(self, location: str, force_refresh: bool = False) -> dict[str, Any]:
        """Return parsed current and forecast weather in metric units."""
        self._load_key()
        cache_key = location.strip().lower()
        cached = self._cache.get(cache_key)
        if cached and not force_refresh and time.time() - cached["created_at"] < self.ttl_seconds:
            data = cached["data"].copy()
            data["from_cache"] = True
            return data

        if not self.api_key:
            return self._get_open_meteo_weather(location, cache_key)

        current = self._request(self.CURRENT_URL, {"q": location, "units": "metric"}, use_api_key=True)
        coords = current.get("coord") or {}
        lat, lon = coords.get("lat"), coords.get("lon")
        if lat is None or lon is None:
            raise WeatherServiceError("Weather response did not include coordinates.")

        forecast = self._request(
            self.FORECAST_URL,
            {"lat": lat, "lon": lon, "units": "metric", "cnt": 40},
            use_api_key=True,
        )
        parsed = {
            "current": self._parse_current(current),
            "hourly": self._parse_hourly(forecast),
            "daily": self._parse_daily(forecast),
            "from_cache": False,
        }

        self._cache[cache_key] = {"created_at": time.time(), "data": parsed}
        canonical = parsed["current"]["location"].lower()
        self._cache[canonical] = {"created_at": time.time(), "data": parsed}
        return parsed

    def _load_key(self) -> None:
        self.api_key = (os.getenv("OPENWEATHER_API_KEY") or Config.OPENWEATHER_API_KEY or self.api_key).strip()

    def _request(self, url: str, params: dict[str, Any], use_api_key: bool = False) -> dict[str, Any]:
        if use_api_key:
            params = {**params, "appid": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            payload = response.json()
        except requests.exceptions.Timeout as exc:
            raise WeatherServiceError("Request timed out. Check your internet connection.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise WeatherServiceError("Network error. Check your internet connection.") from exc
        except requests.exceptions.RequestException as exc:
            raise WeatherServiceError(f"Weather request failed: {exc}") from exc
        except ValueError as exc:
            raise WeatherServiceError("Weather API returned invalid JSON.") from exc

        if response.status_code != 200:
            raise self._api_error(response.status_code, payload)
        return payload

    def _get_open_meteo_weather(self, location: str, cache_key: str) -> dict[str, Any]:
        place = self._open_meteo_geocode(location)
        weather = self._request(
            self.OPEN_METEO_URL,
            {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "timezone": "auto",
                "forecast_days": 7,
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "is_day",
                        "weather_code",
                        "cloud_cover",
                        "pressure_msl",
                        "wind_speed_10m",
                        "wind_direction_10m",
                    ]
                ),
                "hourly": "temperature_2m,precipitation_probability,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset",
            },
        )
        parsed = self._parse_open_meteo(place, weather)
        self._cache[cache_key] = {"created_at": time.time(), "data": parsed}
        self._cache[parsed["current"]["location"].lower()] = {"created_at": time.time(), "data": parsed}
        return parsed

    def _open_meteo_geocode(self, location: str) -> dict[str, Any]:
        queries = [location]
        city = location.split(",", 1)[0].strip()
        if city and city.casefold() != location.casefold():
            queries.append(city)

        for query in queries:
            payload = self._request(self.GEOCODE_URL, {"name": query, "count": 10, "language": "en", "format": "json"})
            results = payload.get("results") or []
            match = self._best_open_meteo_place(location, results)
            if match:
                return match

        raise WeatherServiceError("Location not found. Check spelling or add country/state.")

    @staticmethod
    def _best_open_meteo_place(location: str, results: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not results:
            return None

        for result in results:
            haystack = " ".join(
                str(result.get(key, ""))
                for key in ("name", "admin1", "admin2", "country", "country_code")
            ).casefold()
            if all(part.strip().casefold() in haystack for part in location.split(",") if part.strip()):
                return result
        return results[0]

    def _parse_open_meteo(self, place: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        try:
            current = payload["current"]
            daily = payload["daily"]
            hourly = payload["hourly"]
            location = self._open_meteo_location(place)
            current_code = int(current.get("weather_code", 0))
            wind_speed_ms = float(current.get("wind_speed_10m", 0)) / 3.6
            return {
                "current": {
                    "location": location,
                    "description": self._weather_code_text(current_code),
                    "condition": self._weather_code_condition(current_code),
                    "icon": self._weather_code_icon(current_code, current.get("is_day", 1)),
                    "temperature": current["temperature_2m"],
                    "feels_like": current["apparent_temperature"],
                    "humidity": current["relative_humidity_2m"],
                    "pressure": round(current.get("pressure_msl", 0)),
                    "wind_speed": wind_speed_ms,
                    "wind_deg": current.get("wind_direction_10m", 0),
                    "wind_direction": self._wind_direction(current.get("wind_direction_10m", 0)),
                    "visibility": 0,
                    "cloud_cover": current.get("cloud_cover", 0),
                    "sunrise": self._format_iso_time(daily["sunrise"][0]),
                    "sunset": self._format_iso_time(daily["sunset"][0]),
                    "updated": self._format_iso_time(current["time"]),
                },
                "hourly": self._parse_open_meteo_hourly(hourly),
                "daily": self._parse_open_meteo_daily(daily),
                "from_cache": False,
            }
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise WeatherServiceError("Weather API response changed or is incomplete.") from exc

    @staticmethod
    def _open_meteo_location(place: dict[str, Any]) -> str:
        parts = [place.get("name"), place.get("admin1"), place.get("country")]
        return ", ".join(dict.fromkeys(part for part in parts if part))

    def _parse_open_meteo_hourly(self, hourly: dict[str, Any]) -> list[dict[str, Any]]:
        hours = []
        for index, timestamp in enumerate(hourly["time"][:9]):
            code = int(hourly["weather_code"][index])
            hours.append({
                "time": "Now" if index == 0 else self._format_iso_time(timestamp, "%-I %p"),
                "temperature": hourly["temperature_2m"][index],
                "description": self._weather_code_text(code),
                "condition": self._weather_code_condition(code),
                "icon": self._weather_code_icon(code),
                "pop": hourly.get("precipitation_probability", [0])[index] or 0,
            })
        return hours

    def _parse_open_meteo_daily(self, daily: dict[str, Any]) -> list[dict[str, Any]]:
        days = []
        today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for index, day_key in enumerate(daily["time"][:7]):
            code = int(daily["weather_code"][index])
            label = "Today" if day_key == today_key else datetime.strptime(day_key, "%Y-%m-%d").strftime("%a, %d %b")
            days.append({
                "label": label,
                "high": daily["temperature_2m_max"][index],
                "low": daily["temperature_2m_min"][index],
                "description": self._weather_code_text(code),
                "condition": self._weather_code_condition(code),
                "icon": self._weather_code_icon(code),
            })
        return days

    @staticmethod
    def _format_iso_time(value: str, fmt: str = "%H:%M") -> str:
        return datetime.fromisoformat(value).strftime(fmt)

    @staticmethod
    def _weather_code_text(code: int) -> str:
        descriptions = {
            0: "Clear Sky",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing Rime Fog",
            51: "Light Drizzle",
            53: "Moderate Drizzle",
            55: "Dense Drizzle",
            61: "Slight Rain",
            63: "Moderate Rain",
            65: "Heavy Rain",
            71: "Slight Snow",
            73: "Moderate Snow",
            75: "Heavy Snow",
            80: "Slight Rain Showers",
            81: "Moderate Rain Showers",
            82: "Violent Rain Showers",
            95: "Thunderstorm",
            96: "Thunderstorm With Hail",
            99: "Thunderstorm With Heavy Hail",
        }
        return descriptions.get(code, "Unknown")

    @staticmethod
    def _weather_code_condition(code: int) -> str:
        if code in {0, 1}:
            return "Clear"
        if code in {2, 3}:
            return "Clouds"
        if code in {45, 48}:
            return "Mist"
        if code in {51, 53, 55, 56, 57}:
            return "Drizzle"
        if code in {61, 63, 65, 66, 67, 80, 81, 82}:
            return "Rain"
        if code in {71, 73, 75, 77, 85, 86}:
            return "Snow"
        if code in {95, 96, 99}:
            return "Thunderstorm"
        return "Clear"

    @staticmethod
    def _weather_code_icon(code: int, is_day: int = 1) -> str:
        if code in {0, 1}:
            return "01d" if is_day else "01n"
        if code == 2:
            return "02d" if is_day else "02n"
        if code == 3:
            return "04d"
        if code in {45, 48}:
            return "50d"
        if code in {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}:
            return "10d"
        if code in {71, 73, 75, 77, 85, 86}:
            return "13d"
        if code in {95, 96, 99}:
            return "11d"
        return "01d"

    @staticmethod
    def _api_error(status_code: int, payload: dict[str, Any]) -> WeatherServiceError:
        message = str(payload.get("message", "")).strip()
        if status_code == 401:
            return WeatherServiceError("Invalid API key. Check OPENWEATHER_API_KEY.")
        if status_code == 404:
            return WeatherServiceError("Location not found. Check spelling or add country/state.")
        if status_code == 429:
            return WeatherServiceError("Rate limit reached. Wait before trying again.")
        return WeatherServiceError(message or "Weather service returned an error.")

    def _parse_current(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            weather = payload["weather"][0]
            main = payload["main"]
            sys_data = payload.get("sys", {})
            wind = payload.get("wind", {})
            clouds = payload.get("clouds", {})
            timezone_offset = payload.get("timezone", 0)
            location_parts = [payload.get("name", "Unknown"), sys_data.get("country", "")]
            return {
                "location": ", ".join(part for part in location_parts if part),
                "description": weather.get("description", "Unknown").title(),
                "condition": weather.get("main", "Unknown"),
                "icon": weather.get("icon", ""),
                "temperature": main["temp"],
                "feels_like": main["feels_like"],
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "wind_speed": wind.get("speed", 0),
                "wind_deg": wind.get("deg", 0),
                "wind_direction": self._wind_direction(wind.get("deg", 0)),
                "visibility": payload.get("visibility", 0),
                "cloud_cover": clouds.get("all", 0),
                "sunrise": self._format_time(sys_data.get("sunrise"), timezone_offset),
                "sunset": self._format_time(sys_data.get("sunset"), timezone_offset),
                "updated": self._format_time(payload.get("dt"), timezone_offset),
            }
        except (KeyError, IndexError, TypeError) as exc:
            raise WeatherServiceError("Weather API response changed or is incomplete.") from exc

    def _parse_hourly(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            timezone_offset = payload.get("city", {}).get("timezone", 0)
            hours = []
            for item in payload["list"][:9]:
                weather = item["weather"][0]
                hours.append({
                    "time": "Now" if not hours else self._format_time(item["dt"], timezone_offset, "%-I %p"),
                    "temperature": item["main"]["temp"],
                    "description": weather.get("description", "").title(),
                    "condition": weather.get("main", "Unknown"),
                    "icon": weather.get("icon", ""),
                    "pop": round(item.get("pop", 0) * 100),
                })
            return hours
        except (KeyError, IndexError, TypeError) as exc:
            raise WeatherServiceError("Forecast API response changed or is incomplete.") from exc

    def _parse_daily(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            timezone_offset = payload.get("city", {}).get("timezone", 0)
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for item in payload["list"]:
                local = datetime.fromtimestamp(item["dt"], tz=timezone.utc) + timedelta(seconds=timezone_offset)
                grouped[local.strftime("%Y-%m-%d")].append(item)

            days = []
            today_key = (datetime.now(timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%Y-%m-%d")
            for day_key, items in list(grouped.items())[:7]:
                representative = min(
                    items,
                    key=lambda item: abs(
                        (datetime.fromtimestamp(item["dt"], tz=timezone.utc) + timedelta(seconds=timezone_offset)).hour - 12
                    ),
                )
                weather = representative["weather"][0]
                label = "Today" if day_key == today_key else datetime.strptime(day_key, "%Y-%m-%d").strftime("%a, %d %b")
                days.append({
                    "label": label,
                    "high": max(item["main"].get("temp_max", item["main"]["temp"]) for item in items),
                    "low": min(item["main"].get("temp_min", item["main"]["temp"]) for item in items),
                    "description": weather.get("description", "").title(),
                    "condition": weather.get("main", "Unknown"),
                    "icon": weather.get("icon", ""),
                })
            return days
        except (KeyError, IndexError, TypeError) as exc:
            raise WeatherServiceError("Daily forecast response changed or is incomplete.") from exc

    @staticmethod
    def _format_time(timestamp: int | None, offset_seconds: int = 0, fmt: str = "%H:%M") -> str:
        if not timestamp:
            return "Unavailable"
        return (datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(seconds=offset_seconds)).strftime(fmt)

    @staticmethod
    def _wind_direction(degrees: float) -> str:
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return directions[round(degrees / 22.5) % 16]
