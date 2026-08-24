(function () {
  "use strict";

  var form = document.getElementById("proximityForm");
  if (!form) return;

  // Verified, real nonprofits with a stated mission of increasing access to
  // fresh/clean/local food on Hawai'i Island. A seed list, not exhaustive —
  // each entry was geocoded from a real street address (US Census Bureau
  // geocoder), not approximated. Add more here as they're verified the same
  // way; don't guess at a coordinate to pad the list.
  var NONPROFITS = [
    {
      name: "The Food Basket — Hawaiʻi Island’s Food Bank",
      lat: 19.689654,
      lon: -156.011278,
      location: "Kailua-Kona",
      mission: "Equitable access to healthy, locally produced food across Hawaiʻi Island — including DA BOX, a CSA-style program making fresh, Hawaiʻi-grown produce affordable for SNAP/EBT and retail customers alike.",
      url: "https://www.hawaiifoodbasket.org/"
    },
    {
      name: "Family Support Hawaiʻi",
      lat: 19.626364,
      lon: -155.986355,
      location: "Kailua-Kona",
      mission: "Runs a farm-to-early-childhood program (with Ola Mahina Gardens) connecting local farms directly to low-income families across West Hawaiʻi.",
      url: "https://familysupporthawaii.org/"
    },
    {
      name: "Kohala Food Hub",
      lat: 20.244887,
      lon: -155.833216,
      location: "Hawi",
      mission: "Mission-driven nonprofit growing a sustainable regional food system — support for local farmers and increasing community access to fresh, healthy food.",
      url: "https://www.kohalafoodhub.com/"
    }
  ];

  function $(id) { return document.getElementById(id); }

  function haversineMiles(lat1, lon1, lat2, lon2) {
    var R = 3958.8; // Earth radius in miles
    var toRad = function (d) { return (d * Math.PI) / 180; };
    var dLat = toRad(lat2 - lat1);
    var dLon = toRad(lon2 - lon1);
    var a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function renderResults(originLabel, lat, lon) {
    var ranked = NONPROFITS.map(function (n) {
      return {
        n: n,
        miles: haversineMiles(lat, lon, n.lat, n.lon)
      };
    }).sort(function (a, b) { return a.miles - b.miles; });

    var html = '<p class="proximity-origin">Distances from <strong>' + originLabel + "</strong>:</p>";
    html += '<div class="proximity-results">';
    ranked.forEach(function (r) {
      html +=
        '<div class="proximity-card">' +
        '<div class="proximity-card-head">' +
        '<span class="proximity-miles">' + r.miles.toFixed(1) + " mi</span>" +
        '<span class="proximity-loc">' + r.n.location + "</span>" +
        "</div>" +
        '<h4><a href="' + r.n.url + '" target="_blank" rel="noopener">' + r.n.name + "</a></h4>" +
        "<p>" + r.n.mission + "</p>" +
        "</div>";
    });
    html += "</div>";
    $("proximityResults").innerHTML = html;
    $("proximityResults").hidden = false;
  }

  function geocode(address) {
    var url =
      "https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&q=" +
      encodeURIComponent(address);
    return fetch(url, { headers: { Accept: "application/json" } }).then(function (r) {
      if (!r.ok) throw new Error("geocode failed: " + r.status);
      return r.json();
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var input = $("proximityAddress");
    var address = (input.value || "").trim();
    var status = $("proximityStatus");
    var results = $("proximityResults");

    results.hidden = true;
    if (!address) {
      status.textContent = "Enter an address first — include the city so it can be found.";
      status.hidden = false;
      return;
    }

    status.textContent = "Looking that up…";
    status.hidden = false;

    geocode(address)
      .then(function (matches) {
        if (!matches || matches.length === 0) {
          status.textContent =
            "Couldn't find that address — try adding the city and “HI”, e.g. “123 Main St, Kailua-Kona, HI”.";
          return;
        }
        var match = matches[0];
        status.hidden = true;
        renderResults(address, parseFloat(match.lat), parseFloat(match.lon));
      })
      .catch(function () {
        status.textContent = "Something went wrong looking that up — try again in a moment.";
      });
  });
})();
