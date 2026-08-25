(function () {
  "use strict";

  var container = document.getElementById("growingCalendar");
  if (!container) return;

  var MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  function parseDate(dateStr) {
    return new Date(dateStr + "T00:00:00");
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function daysUntil(target) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    return Math.round((target - today) / 86400000);
  }

  // Compares today's (month, day) against a start/end (month, day) range,
  // wrapping across the New Year when start > end (e.g. dry season Sep 16 - Apr 14).
  function isDateInRange(month, day, start, end) {
    var m = month * 100 + day;
    var s = start.month * 100 + start.day;
    var e = end.month * 100 + end.day;
    if (s <= e) return m >= s && m <= e;
    return m >= s || m <= e;
  }

  function renderSeasonBand(seasonData) {
    var today = new Date();
    var month = today.getMonth() + 1;
    var day = today.getDate();

    var current = isDateInRange(month, day, seasonData.seasons.wet.start, seasonData.seasons.wet.end)
      ? seasonData.seasons.wet
      : seasonData.seasons.dry;

    var activeEvents = (seasonData.events || []).filter(function (e) {
      return isDateInRange(month, day, e.start, e.end);
    });

    var tipsHtml = current.tips.map(function (t) {
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

    return (
      '<div class="season-band season-band-' + (current === seasonData.seasons.wet ? "wet" : "dry") + '">' +
        '<span class="season-label">' + escapeHtml(current.label) + "</span>" +
        "<p class=\"season-summary\">" + escapeHtml(current.summary) + "</p>" +
        eventsHtml +
        '<ul class="season-tips">' + tipsHtml + "</ul>" +
      "</div>"
    );
  }

  // Builds one month's grid (Sun-first) as HTML. entriesByDay maps "YYYY-M-D" -> [entries].
  function renderMonth(year, month, entriesByDay) {
    var first = new Date(year, month, 1);
    var startWeekday = first.getDay();
    var daysInMonth = new Date(year, month + 1, 0).getDate();

    var cells = "";
    for (var i = 0; i < startWeekday; i++) {
      cells += '<div class="grant-cal-cell grant-cal-empty"></div>';
    }
    for (var day = 1; day <= daysInMonth; day++) {
      var key = year + "-" + month + "-" + day;
      var dayEntries = entriesByDay[key] || [];
      var cellDate = new Date(year, month, day);
      var isPast = daysUntil(cellDate) < 0;
      var hasDeadline = dayEntries.length > 0;

      var links = dayEntries.map(function (e) {
        return '<a href="' + escapeHtml(e.learn_more_url) + '" class="grant-cal-link" target="_blank" rel="noopener">' +
          escapeHtml(e.name.length > 28 ? e.name.slice(0, 26) + "…" : e.name) + '</a>';
      }).join("");

      var cellClass = "grant-cal-cell" +
        (hasDeadline ? " grant-cal-has-deadline" : "") +
        (isPast ? " grant-cal-past" : "");

      cells +=
        '<div class="' + cellClass + '">' +
          '<span class="grant-cal-daynum">' + day + '</span>' +
          links +
        '</div>';
    }

    return (
      '<div class="grant-cal-month">' +
        '<h4 class="grant-cal-month-title">' + MONTH_NAMES[month] + " " + year + '</h4>' +
        '<div class="grant-cal-weekdays">' +
          WEEKDAYS.map(function (w) { return '<div class="grant-cal-weekday">' + w + '</div>'; }).join("") +
        '</div>' +
        '<div class="grant-cal-grid">' + cells + '</div>' +
      '</div>'
    );
  }

  function renderUndated(entries) {
    if (!entries.length) return "";
    var items = entries.map(function (e) {
      var label = e.date_type === "contact_window" ? "no fixed deadline — contact first" : "closed, no open window";
      return (
        '<li class="grant-cal-undated-item">' +
          '<a href="' + escapeHtml(e.learn_more_url) + '" target="_blank" rel="noopener">' + escapeHtml(e.name) + '</a>' +
          ' <span class="grant-cal-undated-label">— ' + escapeHtml(label) + '</span>' +
        '</li>'
      );
    }).join("");
    return (
      '<h4 class="grant-calendar-group">Contact-first or closed right now</h4>' +
      '<ul class="grant-cal-undated-list">' + items + '</ul>'
    );
  }

  function renderGrantCalendar(entries) {
    var dated = entries.filter(function (e) {
      return e.date_type === "deadline" && e.action_date;
    });
    var undated = entries.filter(function (e) {
      return e.date_type !== "deadline" || !e.action_date;
    });

    if (!dated.length) {
      return renderUndated(undated) || "";
    }

    var entriesByDay = {};
    var dates = dated.map(function (e) {
      var d = parseDate(e.action_date);
      var key = d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate();
      (entriesByDay[key] = entriesByDay[key] || []).push(e);
      return d;
    });

    var today = new Date();
    var startYear = today.getFullYear(), startMonth = today.getMonth();
    var maxDate = dates.reduce(function (a, b) { return b > a ? b : a; });
    var endYear = maxDate.getFullYear(), endMonth = maxDate.getMonth();

    var months = "";
    var y = startYear, m = startMonth;
    while (y < endYear || (y === endYear && m <= endMonth)) {
      months += renderMonth(y, m, entriesByDay);
      m++;
      if (m > 11) { m = 0; y++; }
    }

    return '<div class="grant-cal-months">' + months + '</div>' + renderUndated(undated);
  }

  var seasonSrc = container.getAttribute("data-season-src") || "/assets/data/season-tips.json";
  var grantsSrc = container.getAttribute("data-grants-src") || "/assets/data/grant-calendar.json";

  Promise.all([
    fetch(seasonSrc).then(function (r) {
      if (!r.ok) throw new Error("Failed to load season data");
      return r.json();
    }),
    fetch(grantsSrc).then(function (r) {
      if (!r.ok) throw new Error("Failed to load grant calendar data");
      return r.json();
    })
  ]).then(function (results) {
    var seasonData = results[0];
    var grantEntries = results[1];
    container.innerHTML =
      renderSeasonBand(seasonData) +
      '<h4 class="grant-calendar-group">Grant deadlines this year</h4>' +
      renderGrantCalendar(grantEntries);
  }).catch(function () {
    container.innerHTML = '<p class="grant-calendar-error">Couldn\'t load the growing calendar right now — try refreshing, or email <a href="mailto:hello@ainatotable.com">hello@ainatotable.com</a> if it keeps happening.</p>';
  });
})();
