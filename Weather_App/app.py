"""Flask entry point for the Atmos weather dashboard."""

from flask import Flask, jsonify, render_template, request

from config import Config
from services.weather_service import WeatherService, WeatherServiceError
from utils.validators import validate_location


app = Flask(__name__)
app.config.from_object(Config)
weather = WeatherService(
    api_key=app.config["OPENWEATHER_API_KEY"],
    ttl_seconds=app.config["WEATHER_CACHE_SECONDS"],
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/weather")
def api_weather():
    location = request.args.get("location", "")
    force_refresh = request.args.get("refresh", "false").lower() == "true"

    valid, error = validate_location(location)
    if not valid:
        return jsonify({"ok": False, "error": error}), 400

    try:
        data = weather.get_weather(location, force_refresh=force_refresh)
        return jsonify({"ok": True, "data": data})
    except WeatherServiceError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=app.config["PORT"],
        debug=app.config["FLASK_DEBUG"],
        use_reloader=False,
    )
