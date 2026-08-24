(function () {
  "use strict";

  var form = document.getElementById("proximityForm");
  if (!form) return;

  // Verified, real entries only — each geocoded from a real street address
  // (US Census Bureau geocoder, with OpenStreetMap/Nominatim as fallback
  // when Census had no match) rather than approximated. A seed list, not
  // exhaustive. Add more here as they're verified the same way.
  var PLACES = [
    // Nonprofits — stated mission of increasing access to fresh/clean food
    {
      type: "nonprofit",
      name: "The Food Basket — Hawaiʻi Island’s Food Bank",
      lat: 19.689654,
      lon: -156.011278,
      location: "Kailua-Kona",
      note: "Equitable access to healthy, locally produced food across Hawaiʻi Island — including DA BOX, a CSA-style program making fresh, Hawaiʻi-grown produce affordable for SNAP/EBT and retail customers alike.",
      url: "https://www.hawaiifoodbasket.org/"
    },
    {
      type: "nonprofit",
      name: "Family Support Hawaiʻi",
      lat: 19.626364,
      lon: -155.986355,
      location: "Kailua-Kona",
      note: "Runs a farm-to-early-childhood program (with Ola Mahina Gardens) connecting local farms directly to low-income families across West Hawaiʻi.",
      url: "https://familysupporthawaii.org/"
    },
    {
      type: "nonprofit",
      name: "Kohala Food Hub",
      lat: 20.244887,
      lon: -155.833216,
      location: "Hawi",
      note: "Mission-driven nonprofit growing a sustainable regional food system — support for local farmers and increasing community access to fresh, healthy food.",
      url: "https://www.kohalafoodhub.com/"
    },
    // Farms — small, independent growers
    {
      type: "farm",
      category: "Produce & greens",
      name: "Ola Mahina Gardens at Kealaola Farm",
      lat: 19.519507,
      lon: -155.925479,
      location: "Kealakekua",
      note: "Family-run certified organic farm — leafy greens, tropical fruit, medicinal herbs, and estate coffee. Also runs internships and educational programming.",
      url: "https://www.kealaolafarm.com/"
    },
    {
      type: "farm",
      category: "Gourmet mushrooms",
      name: "Mermaid Mushrooms",
      lat: 19.519049,
      lon: -155.924229,
      location: "Kealakekua",
      note: "Gourmet mushroom farm using vertical indoor growing — a genuinely different product than a food forest or produce farm, more complement than competitor.",
      url: "https://www.bigislandlocavorestore.com/suppliers/mermaid-mushrooms"
    },
    {
      type: "farm",
      category: "Coffee (not produce)",
      name: "Greenwell Farms",
      lat: 19.512375,
      lon: -155.920390,
      location: "Kealakekua",
      note: "South Kona Kona-coffee farm and processing operation running public tours since 1850. Coffee-focused — relevant to a café or coffee program, not produce sourcing.",
      url: "https://www.greenwellfarms.com/"
    },
    {
      type: "farm",
      category: "Coffee (not produce)",
      name: "Rooster Farms",
      lat: 19.433108,
      lon: -155.872178,
      location: "Captain Cook",
      note: "The oldest certified organic Kona coffee farm on the island — farms, mills, and roasts on site. Coffee-focused — relevant to a café or coffee program, not produce sourcing.",
      url: "https://www.roosterfarmshop.com/"
    },
    // Farmers markets
    {
      type: "market",
      name: "South Kona Green Market",
      lat: 19.490730,
      lon: -155.912883,
      location: "Captain Cook",
      note: "Sundays, 9am–2pm, at Amy Greenwell Ethnobotanical Garden. Vendor contact: info@skgm.org.",
      url: "https://skgm.org/"
    },
    {
      type: "market",
      name: "South Kona Fruit Stand",
      lat: 19.443878,
      lon: -155.879773,
      location: "Captain Cook",
      note: "Mon, Wed–Fri 10am–5pm; Sat–Sun 10am–4pm. A stand, not a vendor market — worth a direct conversation about wholesale/consignment.",
      url: ""
    },
    {
      type: "market",
      name: "Keauhou Farmers Market",
      lat: 19.573326,
      lon: -155.966075,
      location: "Kailua-Kona",
      note: "Saturdays, 8am–12pm, at Keauhou Shopping Center. Run by Kona County Farm Bureau. Vendor contact: keauhoumarket@gmail.com.",
      url: "https://keauhoufarmersmarket.com/"
    }
  ];

  var GROUP_LABELS = {
    farm: "Farms",
    market: "Farmers Markets",
    nonprofit: "Food-Access Nonprofits"
  };
  var GROUP_ORDER = ["farm", "market", "nonprofit"];

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

  function $(id) { return document.getElementById(id); }

  function placeCard(p, miles) {
    var badge = p.category ? '<span class="proximity-loc">' + p.category + "</span>" : '<span class="proximity-loc">' + p.location + "</span>";
    var title = p.url
      ? '<h4><a href="' + p.url + '" target="_blank" rel="noopener">' + p.name + "</a></h4>"
      : "<h4>" + p.name + "</h4>";
    return (
      '<div class="proximity-card">' +
      '<div class="proximity-card-head">' +
      '<span class="proximity-miles">' + miles.toFixed(1) + " mi</span>" +
      badge +
      "</div>" +
      title +
      "<p>" + p.note + "</p>" +
      "</div>"
    );
  }

  function renderResults(originLabel, lat, lon) {
    var ranked = PLACES.map(function (p) {
      return { p: p, miles: haversineMiles(lat, lon, p.lat, p.lon) };
    }).sort(function (a, b) { return a.miles - b.miles; });

    var html = '<p class="proximity-origin">Distances from <strong>' + originLabel + "</strong>:</p>";

    GROUP_ORDER.forEach(function (type) {
      var group = ranked.filter(function (r) { return r.p.type === type; });
      if (group.length === 0) return;
      html += "<h4 class='proximity-group-title'>" + GROUP_LABELS[type] + "</h4>";
      html += '<div class="proximity-results">';
      group.forEach(function (r) { html += placeCard(r.p, r.miles); });
      html += "</div>";
    });

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
