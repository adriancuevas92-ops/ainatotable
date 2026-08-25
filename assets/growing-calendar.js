(function () {
  "use strict";

  var container = document.getElementById("growingCalendar");
  if (!container) return;

  var MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  var seasonData = null;
  var todayMonth, todayDay;

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Compares a given (month, day) against a start/end (month, day) range,
  // wrapping across the New Year when start > end (e.g. dry season Sep 16 - Apr 14).
  function isDateInRange(month, day, start, end) {
    var m = month * 100 + day;
    var s = start.month * 100 + start.day;
    var e = end.month * 100 + end.day;
    if (s <= e) return m >= s && m <= e;
    return m >= s || m <= e;
  }

  function seasonFor(month, day) {
    return isDateInRange(month, day, seasonData.seasons.wet.start, seasonData.seasons.wet.end)
      ? "wet"
      : "dry";
  }

  function eventsFor(month, day) {
    return (seasonData.events || []).filter(function (e) {
      return isDateInRange(month, day, e.start, e.end);
    });
  }

  function renderBand(month, day) {
    var seasonKey = seasonFor(month, day);
    var season = seasonData.seasons[seasonKey];
    var activeEvents = eventsFor(month, day);
    var isToday = month === todayMonth && day === todayDay;

    var tipsHtml = season.tips.map(function (t) {
      return "<li>" + escapeHtml(t) + "</li>";
    }).join("");

    var eventsHtml = activeEvents.length
      ? '<div class="season-events">' +
        activeEvents.map(function (e) {
          return '<p class="season-event"><strong>Happening now:</strong> ' +
            escapeHtml(e.label) + " — " + escapeHtml(e.note) + "</p>";
        }).join("") +
        "</div>"
      : "";

    var whenLabel = isToday
      ? "Today"
      : MONTH_NAMES[month - 1] + " " + day;

    return (
      '<div class="season-band season-band-' + seasonKey + '">' +
        '<span class="season-label">' + escapeHtml(season.label) + "</span>" +
        '<span class="season-when">' + escapeHtml(whenLabel) +
          (isToday ? "" : ' — <button type="button" class="season-reset">back to today</button>') +
        "</span>" +
        "<p class=\"season-summary\">" + escapeHtml(season.summary) + "</p>" +
        eventsHtml +
        '<ul class="season-tips">' + tipsHtml + "</ul>" +
      "</div>"
    );
  }

  function renderMonth(year, monthIndex) {
    var first = new Date(year, monthIndex, 1);
    var startWeekday = first.getDay();
    var daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
    var month = monthIndex + 1;

    var cells = "";
    for (var i = 0; i < startWeekday; i++) {
      cells += '<div class="season-cal-cell season-cal-empty"></div>';
    }
    for (var day = 1; day <= daysInMonth; day++) {
      var seasonKey = seasonFor(month, day);
      var hasEvent = eventsFor(month, day).length > 0;
      var isToday = month === todayMonth && day === todayDay;

      var cellClass = "season-cal-cell season-cal-" + seasonKey +
        (hasEvent ? " season-cal-event" : "") +
        (isToday ? " season-cal-today" : "");

      cells +=
        '<button type="button" class="' + cellClass + '" data-month="' + month + '" data-day="' + day + '">' +
          day +
        "</button>";
    }

    return (
      '<div class="season-cal-month">' +
        '<h4 class="season-cal-month-title">' + MONTH_NAMES[monthIndex] + '</h4>' +
        '<div class="season-cal-weekdays">' +
          WEEKDAYS.map(function (w) { return '<div class="season-cal-weekday">' + w + '</div>'; }).join("") +
        '</div>' +
        '<div class="season-cal-grid">' + cells + '</div>' +
      '</div>'
    );
  }

  function renderYearGrid(year) {
    var months = "";
    for (var m = 0; m < 12; m++) {
      months += renderMonth(year, m);
    }
    return '<div class="season-cal-months">' + months + '</div>';
  }

  function render(month, day) {
    var year = new Date().getFullYear();
    container.innerHTML =
      renderBand(month, day) +
      '<p class="season-cal-hint">Click any day to see what South Kona\'s growing calendar says for that date.</p>' +
      renderYearGrid(year);

    container.querySelectorAll(".season-cal-cell:not(.season-cal-empty)").forEach(function (cell) {
      cell.addEventListener("click", function () {
        render(parseInt(cell.getAttribute("data-month"), 10), parseInt(cell.getAttribute("data-day"), 10));
      });
    });
    var resetBtn = container.querySelector(".season-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        render(todayMonth, todayDay);
      });
    }
  }

  var seasonSrc = container.getAttribute("data-season-src") || "/assets/data/season-tips.json";

  fetch(seasonSrc)
    .then(function (r) {
      if (!r.ok) throw new Error("Failed to load season data");
      return r.json();
    })
    .then(function (data) {
      seasonData = data;
      var today = new Date();
      todayMonth = today.getMonth() + 1;
      todayDay = today.getDate();
      render(todayMonth, todayDay);
    })
    .catch(function () {
      container.innerHTML = '<p class="growing-calendar-error">Couldn\'t load the growing calendar right now — try refreshing, or email <a href="mailto:hello@ainatotable.com">hello@ainatotable.com</a> if it keeps happening.</p>';
    });
})();
