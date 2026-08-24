(function () {
  "use strict";

  var container = document.getElementById("grantCalendar");
  if (!container) return;

  var DATE_TYPE_LABEL = {
    deadline: "deadline",
    contact_window: "contact first — no fixed deadline",
    closed: "closed for this cycle"
  };

  function daysUntil(dateStr) {
    if (!dateStr) return null;
    var target = new Date(dateStr + "T00:00:00");
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    return Math.round((target - today) / 86400000);
  }

  function urgencyClass(days) {
    if (days === null) return "grant-urgency-none";
    if (days < 0) return "grant-urgency-past";
    if (days <= 30) return "grant-urgency-soon";
    if (days <= 60) return "grant-urgency-medium";
    return "grant-urgency-far";
  }

  function daysLabel(days, dateType) {
    if (dateType === "contact_window") return "no fixed deadline";
    if (days === null) return "no date";
    if (days < 0) return "closed";
    if (days === 0) return "due today";
    if (days === 1) return "1 day left";
    return days + " days left";
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderCard(e) {
    var days = daysUntil(e.action_date);
    var badge = daysLabel(days, e.date_type);
    var dateLine = e.action_date
      ? new Date(e.action_date + "T00:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
      : DATE_TYPE_LABEL[e.date_type] || "";

    return (
      '<article class="grant-card ' + urgencyClass(days) + '">' +
      '<div class="grant-card-head">' +
        '<h3>' + escapeHtml(e.name) + '</h3>' +
        '<span class="grant-badge">' + escapeHtml(badge) + '</span>' +
      '</div>' +
      '<p class="grant-level">' + escapeHtml(e.level) + (dateLine ? " · " + escapeHtml(dateLine) : "") + '</p>' +
      '<p><strong>Why it\'s relevant:</strong> ' + escapeHtml(e.relevance) + '</p>' +
      '<p><strong>How it actually works:</strong> ' + escapeHtml(e.real_process) + '</p>' +
      '<p><strong>The deadline lesson:</strong> ' + escapeHtml(e.deadline_lesson) + '</p>' +
      (e.date_note ? '<p><strong>About this date:</strong> ' + escapeHtml(e.date_note) + '</p>' : '') +
      '<p><strong>Where to start:</strong> ' + escapeHtml(e.start_here) + '</p>' +
      '<p class="grant-verified">Checked ' + escapeHtml(e.last_verified) + '. Programs change — verify directly before relying on this.</p>' +
      '</article>'
    );
  }

  function render(entries) {
    var dated = entries.filter(function (e) { return e.date_type === "deadline"; });
    var undated = entries.filter(function (e) { return e.date_type !== "deadline"; });

    dated.sort(function (a, b) { return daysUntil(a.action_date) - daysUntil(b.action_date); });

    var html = "";
    if (dated.length) {
      html += '<h3 class="grant-calendar-group">Programs with a real posted deadline, soonest first</h3>';
      html += '<div class="grant-card-grid">' + dated.map(renderCard).join("") + "</div>";
    }
    if (undated.length) {
      html += '<h3 class="grant-calendar-group">Contact-first or closed right now</h3>';
      html += '<div class="grant-card-grid">' + undated.map(renderCard).join("") + "</div>";
    }
    container.innerHTML = html;
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
