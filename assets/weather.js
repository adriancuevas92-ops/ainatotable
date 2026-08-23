(function () {
  "use strict";

  var el = document.getElementById("konaWeather");
  if (!el) return;

  var LAT = el.getAttribute("data-lat");
  var LON = el.getAttribute("data-lon");
  var TZ = "Pacific/Honolulu";

  // WMO weather code -> [condition text, icon key]
  var CODES = {
    0: ["Clear sky", "sun"],
    1: ["Mainly clear", "sun"],
    2: ["Partly cloudy", "cloud-sun"],
    3: ["Overcast", "cloud"],
    45: ["Foggy", "fog"],
    48: ["Foggy", "fog"],
    51: ["Light drizzle", "drizzle"],
    53: ["Drizzle", "drizzle"],
    55: ["Heavy drizzle", "drizzle"],
    56: ["Freezing drizzle", "drizzle"],
    57: ["Freezing drizzle", "drizzle"],
    61: ["Light rain", "rain"],
    63: ["Rain", "rain"],
    65: ["Heavy rain", "rain"],
    66: ["Freezing rain", "rain"],
    67: ["Freezing rain", "rain"],
    71: ["Light snow", "snow"],
    73: ["Snow", "snow"],
    75: ["Heavy snow", "snow"],
    77: ["Snow grains", "snow"],
    80: ["Rain showers", "rain"],
    81: ["Rain showers", "rain"],
    82: ["Heavy showers", "rain"],
    85: ["Snow showers", "snow"],
    86: ["Snow showers", "snow"],
    95: ["Thunderstorm", "storm"],
    96: ["Thunderstorm", "storm"],
    99: ["Thunderstorm", "storm"]
  };

  var ICONS = {
    sun: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="24" cy="24" r="9"/><path d="M24 4v6M24 38v6M4 24h6M38 24h6M9 9l4.2 4.2M34.8 34.8L39 39M39 9l-4.2 4.2M13.2 34.8L9 39"/></svg>',
    cloud: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 34H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 34z"/></svg>',
    "cloud-sun": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="14" r="6"/><path d="M16 4v3M8 14H5M9.5 6.5l2 2"/><path d="M36 38H19a8 8 0 0 1-1-16 11.5 11.5 0 0 1 21.8 3.6A6.7 6.7 0 0 1 36 38z"/></svg>',
    fog: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 26H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 26z"/><path d="M8 34h32M6 40h32"/></svg>',
    drizzle: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 24H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 24z"/><path d="M16 32v4M24 32v4M32 32v4"/></svg>',
    rain: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 22H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 22z"/><path d="M15 30l-3 8M24 30l-3 8M33 30l-3 8"/></svg>',
    snow: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 22H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 22z"/><path d="M16 30v8M12 34h8M24 30v8M20 34h8M32 30v8M28 34h8"/></svg>',
    storm: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M34 20H15a9 9 0 0 1-1-17.9 13 13 0 0 1 24.6 4A7.5 7.5 0 0 1 34 20z"/><path d="M26 26l-6 10h6l-4 8"/></svg>'
  };

  function codeInfo(code) {
    return CODES[code] || ["Conditions", "cloud"];
  }

  function iconSvg(code) {
    return ICONS[codeInfo(code)[1]] || ICONS.cloud;
  }

  function fmtClockTime(iso) {
    var d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: TZ });
  }

  function $(id) { return document.getElementById(id); }

  function updateClock() {
    var clockEl = $("weatherClock");
    if (!clockEl) return;
    var now = new Date();
    var time = now.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", second: "2-digit", timeZone: TZ });
    clockEl.textContent = "Right now at the site: " + time + " HST";
  }

  function render(data) {
    var cur = data.current;
    var daily = data.daily;
    var info = codeInfo(cur.weather_code);

    $("weatherIcon").innerHTML = iconSvg(cur.weather_code);
    $("weatherTemp").textContent = Math.round(cur.temperature_2m);
    $("weatherCond").textContent = info[0];
    $("weatherFeels").textContent = Math.round(cur.apparent_temperature);
    $("weatherWind").textContent = Math.round(cur.wind_speed_10m) + " mph";
    $("weatherHumidity").textContent = Math.round(cur.relative_humidity_2m) + "%";
    $("weatherUv").textContent = Math.round(daily.uv_index_max[0]);
    $("weatherRain").textContent = Math.round(daily.precipitation_probability_max[0]) + "%";
    $("weatherSunrise").textContent = fmtClockTime(daily.sunrise[0]);
    $("weatherSunset").textContent = fmtClockTime(daily.sunset[0]);

    var dayLabels = ["Today", "Tomorrow"];
    var html = "";
    for (var i = 0; i < daily.time.length; i++) {
      var label = i < 2
        ? dayLabels[i]
        : new Date(daily.time[i] + "T12:00:00").toLocaleDateString("en-US", { weekday: "short", timeZone: TZ });
      html += '<div class="weather-day">'
        + '<span class="weather-day-name">' + label + "</span>"
        + iconSvg(daily.weather_code[i])
        + '<span class="weather-day-temps"><strong>' + Math.round(daily.temperature_2m_max[i]) + "&deg;</strong> "
        + Math.round(daily.temperature_2m_min[i]) + "&deg;</span>"
        + "</div>";
    }
    $("weatherForecast").innerHTML = html;

    $("weatherLoading").hidden = true;
    $("weatherError").hidden = true;
    $("weatherContent").hidden = false;
  }

  function load() {
    $("weatherLoading").hidden = false;
    $("weatherError").hidden = true;
    $("weatherContent").hidden = true;

    var url = "https://api.open-meteo.com/v1/forecast?latitude=" + LAT + "&longitude=" + LON
      + "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m"
      + "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,sunrise,sunset"
      + "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=" + encodeURIComponent(TZ) + "&forecast_days=4";

    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("weather fetch failed: " + r.status);
        return r.json();
      })
      .then(render)
      .catch(function () {
        $("weatherLoading").hidden = true;
        $("weatherContent").hidden = true;
        $("weatherError").hidden = false;
      });
  }

  var retryBtn = $("weatherRetry");
  if (retryBtn) retryBtn.addEventListener("click", load);

  updateClock();
  setInterval(updateClock, 1000);

  load();
  setInterval(load, 10 * 60 * 1000);
})();
