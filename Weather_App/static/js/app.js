const state = {
  unit: "c",
  payload: null,
  location: "",
};

const $ = (id) => document.getElementById(id);

const elements = {
  input: $("locationInput"),
  status: $("status"),
  clear: $("clearButton"),
  search: $("searchButton"),
  refresh: $("refreshButton"),
  unitButtons: document.querySelectorAll(".unit-toggle button"),
  place: $("placeName"),
  description: $("description"),
  temperature: $("temperature"),
  feelsLike: $("feelsLike"),
  bigIcon: $("bigIcon"),
  wind: $("wind"),
  windDir: $("windDir"),
  humidity: $("humidity"),
  highLow: $("highLow"),
  daily: $("dailyList"),
  hourly: $("hourlyList"),
  detailWind: $("detailWind"),
  detailDirection: $("detailDirection"),
  detailHumidity: $("detailHumidity"),
  pressure: $("pressure"),
  cloudCover: $("cloudCover"),
  visibility: $("visibility"),
  sunrise: $("sunrise"),
  sunset: $("sunset"),
  updated: $("updated"),
  cacheState: $("cacheState"),
};

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("error", isError);
}

function normalizeLocation(value) {
  return value.trim().replace(/\s+/g, " ");
}

function validateLocation(value) {
  const location = normalizeLocation(value);
  if (!location) return "Enter a location before searching.";
  if (location.length < 2) return "Location must be at least 2 characters.";
  if (location.length > 100) return "Location is too long.";
  if (/https?:\/\/|www\.|[@#$%^*_={}\[\]<>|~`]/i.test(location)) return "Enter a city, state, region, or country name only.";
  if (!/[a-zA-Z]/.test(location)) return "Location must contain at least one letter.";
  if (!/^[a-zA-Z0-9\s,.'-]+$/.test(location)) return "Location contains invalid characters.";
  return "";
}

async function loadWeather(forceRefresh = false) {
  const location = normalizeLocation(elements.input.value || state.location);
  const error = validateLocation(location);
  if (error) {
    setStatus(error, true);
    return;
  }

  setStatus(forceRefresh ? "Refreshing live weather..." : "Loading weather...");
  state.location = location;

  try {
    const params = new URLSearchParams({ location, refresh: String(forceRefresh) });
    const response = await fetch(`/api/weather?${params.toString()}`);
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.error || "Could not load weather.");
    }
    state.payload = result.data;
    render();
    setStatus(`${result.data.from_cache ? "Loaded from cache" : "Updated live"} at ${result.data.current.updated}. Refresh forces a new request.`);
  } catch (err) {
    setStatus(err.message || "Network error. Could not load weather.", true);
  }
}

function cToF(value) {
  return (value * 9) / 5 + 32;
}

function temp(value) {
  const converted = state.unit === "f" ? cToF(value) : value;
  return `${Math.round(converted)}°`;
}

function speed(value) {
  if (state.unit === "f") {
    return `${Math.round(value * 2.236936)} mph`;
  }
  return `${Math.round(value * 3.6)} km/h`;
}

function visibility(value) {
  if (!value) return "--";
  if (state.unit === "f") {
    return `${(value / 1609.344).toFixed(1)} mi`;
  }
  return `${(value / 1000).toFixed(1)} km`;
}

function iconFor(item) {
  const code = item.icon || "";
  const condition = (item.condition || "").toLowerCase();
  if (code.startsWith("01")) return code.endsWith("n") ? "☾" : "☀";
  if (code.startsWith("02")) return "◐";
  if (code.startsWith("03") || code.startsWith("04")) return "☁";
  if (code.startsWith("09") || code.startsWith("10")) return "☔";
  if (code.startsWith("11")) return "⚡";
  if (code.startsWith("13")) return "❄";
  if (code.startsWith("50")) return "≋";
  if (condition.includes("thunder")) return "⚡";
  if (condition.includes("snow")) return "❄";
  if (condition.includes("rain") || condition.includes("drizzle")) return "☔";
  if (condition.includes("fog") || condition.includes("mist") || condition.includes("haze")) return "≋";
  if (condition.includes("cloud")) return "☁";
  return "☀";
}

function render() {
  if (!state.payload) return;
  const { current, hourly, daily } = state.payload;
  const today = daily[0] || {};

  elements.place.textContent = current.location;
  elements.description.textContent = current.description;
  elements.temperature.textContent = temp(current.temperature);
  elements.feelsLike.textContent = temp(current.feels_like);
  elements.bigIcon.textContent = iconFor(current);
  elements.wind.textContent = speed(current.wind_speed);
  elements.windDir.textContent = current.wind_direction;
  elements.humidity.textContent = `${current.humidity}%`;
  elements.highLow.textContent = today.high == null ? "-- / --" : `${temp(today.high)} / ${temp(today.low)}`;

  elements.detailWind.textContent = speed(current.wind_speed);
  elements.detailDirection.textContent = `${current.wind_direction} · ${Math.round(current.wind_deg)}°`;
  elements.detailHumidity.textContent = `${current.humidity}%`;
  elements.pressure.textContent = `${current.pressure}`;
  elements.cloudCover.textContent = `${current.cloud_cover}%`;
  elements.visibility.textContent = visibility(current.visibility);
  elements.sunrise.textContent = current.sunrise;
  elements.sunset.textContent = current.sunset;
  elements.updated.textContent = current.updated;
  elements.cacheState.textContent = state.payload.from_cache ? "Cached" : "Live";

  elements.daily.innerHTML = daily.map((day) => `
    <div class="daily-item">
      <span>${day.label}</span>
      <span class="icon">${iconFor(day)}</span>
      <span><strong>${temp(day.high)}</strong> <small>${temp(day.low)}</small></span>
    </div>
  `).join("");

  elements.hourly.innerHTML = hourly.map((hour) => `
    <div class="hourly-item">
      <span>${hour.time}</span>
      <div class="icon">${iconFor(hour)}</div>
      <strong>${temp(hour.temperature)}</strong>
    </div>
  `).join("");
}

elements.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadWeather(false);
});

elements.clear.addEventListener("click", () => {
  elements.input.value = "";
  elements.input.focus();
});

elements.search.addEventListener("click", () => loadWeather(false));

elements.refresh.addEventListener("click", () => loadWeather(true));

elements.unitButtons.forEach((button) => {
  button.addEventListener("click", () => {
    state.unit = button.dataset.unit;
    elements.unitButtons.forEach((item) => item.classList.toggle("active", item === button));
    render();
    if (state.payload) setStatus("Unit changed locally. No API call was made.");
  });
});

elements.input.value = "Ahmedabad, Gujarat, India";
elements.input.focus();
