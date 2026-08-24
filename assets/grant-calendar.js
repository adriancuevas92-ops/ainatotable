(function () {
  "use strict";

  var container = document.getElementById("grantCalendar");
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
        return '<a href="/grants/' + escapeHtml(e.slug) + '.html" class="grant-cal-link">' +
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
          '<a href="/grants/' + escapeHtml(e.slug) + '.html">' + escapeHtml(e.name) + '</a>' +
          ' <span class="grant-cal-undated-label">— ' + escapeHtml(label) + '</span>' +
        '</li>'
      );
    }).join("");
    return (
      '<h4 class="grant-calendar-group">Contact-first or closed right now</h4>' +
      '<ul class="grant-cal-undated-list">' + items + '</ul>'
    );
  }

  function render(entries) {
    var dated = entries.filter(function (e) {
      return e.date_type === "deadline" && e.action_date;
    });
    var undated = entries.filter(function (e) {
      return e.date_type !== "deadline" || !e.action_date;
    });

    if (!dated.length) {
      container.innerHTML = renderUndated(undated) || '<p>No tracked programs right now.</p>';
      return;
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

    container.innerHTML =
      '<div class="grant-cal-months">' + months + '</div>' +
      renderUndated(undated);
  }

  var src = container.getAttribute("data-src") || "/assets/data/grant-calendar.json";
  fetch(src)
    .then(function (r) {
      if (!r.ok) throw new Error("Failed to load grant calendar data");
      return r.json();
    })
    .then(render)
    .catch(function () {
      container.innerHTML = '<p class="grant-calendar-error">Couldn\'t load the live calendar right now — try refreshing, or email <a href="mailto:hello@ainatotable.com">hello@ainatotable.com</a> if it keeps happening.</p>';
    });
})();
