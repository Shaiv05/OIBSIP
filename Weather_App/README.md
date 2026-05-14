# Atmos Weather Dashboard

A Flask-based weather dashboard with a polished dark glass UI, live weather search, forecast cards, unit switching, server-side validation, and cache-aware API calls. The app is organized with separate route, service, utility, configuration, static, template, data, and log folders so it is easier to maintain and present in an internship or GitHub portfolio.

## Features

- Search weather by city, state, region, or country.
- Current weather, hourly forecast, and multi-day forecast.
- Wind, humidity, pressure, cloud cover, visibility, sunrise, sunset, and update time.
- Celsius/Fahrenheit toggle without extra API calls.
- In-memory weather cache to reduce repeated requests.
- User-friendly handling for empty input, invalid locations, bad API keys, rate limits, timeouts, API failures, and network errors.
- OpenWeatherMap support with secure environment variables.
- Open-Meteo fallback when no OpenWeatherMap API key is configured.

## Tech Stack

- Python
- Flask
- python-dotenv
- Requests
- HTML
- CSS
- JavaScript

## Folder Structure

```text
Weather_App/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── services/
│   ├── __init__.py
│   └── weather_service.py
├── utils/
│   ├── __init__.py
│   └── validators.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── data/
└── logs/
```

## Setup

```bash
cd Weather_App
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Optional `.env` values:

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
PORT=5001
FLASK_DEBUG=0
WEATHER_CACHE_SECONDS=600
```

`OPENWEATHER_API_KEY` is optional. If it is missing, the app automatically uses Open-Meteo, which does not require an API key.

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

If port `5001` is busy:

```bash
PORT=5050 python app.py
```

## API Information

- OpenWeatherMap is used when `OPENWEATHER_API_KEY` is present.
- Open-Meteo is used as a no-key fallback.
- API keys are loaded from `.env` using `python-dotenv`.
- `.env` is ignored by Git and should not be committed.

Main app endpoints:

```text
GET /
GET /api/weather?location=Ahmedabad,%20Gujarat,%20India
```

## Screenshots

Add screenshots here before submitting the project:

```text
screenshots/home.png
screenshots/weather-result.png
```
