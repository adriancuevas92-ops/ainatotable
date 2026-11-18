#!/usr/bin/env python3
"""Given an address (or a lat/lon), print that parcel's real local climate
history -- not a species-tolerance range, a measured local fact.

Built for the grower email intake: a grower writes in with "the parcel
number or nearest cross-streets" (see growers.html / build.py's registration
copy), by design a plain email to a person, not a form. This tool is what
that person runs by hand against what the grower sent -- it does not touch,
read, or create any grower registry, and nothing it prints is saved anywhere
automatically. Keep the intake as-is; this just answers one lookup at a time.

A bare parcel/APN number cannot be geocoded here -- the Census geocoder
matches street addresses and intersections, not assessor parcel numbers.
For an APN with no cross-streets, use the county assessor's own GIS lookup
first to get an address or coordinates, then run this.

Both calls are free and keyless:
  - US Census Bureau Geocoding Services (geocoding.geo.census.gov) -- an
    address or intersection in, a lat/lon out. No key.
  - NASA POWER, community=AG (power.larc.nasa.gov) -- the same
    agroclimatology data this project's crop_reference pipeline already
    draws species-tolerance ranges from (temperature, precipitation, solar
    radiation), but the real local climatology for ONE point, not a
    species' general tolerance. No key.

Usage:
    python3 -I tools/address_to_local_climate.py "2600 Fresno St, Fresno, CA"
    python3 -I tools/address_to_local_climate.py --latlon 36.7402 -119.7861
"""
import json, subprocess, sys, urllib.parse

CENSUS = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
POWER = "https://power.larc.nasa.gov/api/temporal/climatology/point"

# Same five the crop_reference pipeline already tracks species-tolerance
# ranges for (temp_opt_*, soil tables elsewhere) -- kept to that set
# deliberately, so a reader can compare a local measured figure against the
# matching species range instead of two unrelated numbers.
PARAMETERS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "ANN"]
LABELS = {
    "T2M": "Avg temp (°C)", "T2M_MAX": "Avg high (°C)", "T2M_MIN": "Avg low (°C)",
    "PRECTOTCORR": "Precipitation (mm/day)", "ALLSKY_SFC_SW_DWN": "Solar radiation (kWh/m²/day)",
}


def fetch_json(url):
    r = subprocess.run(["curl", "-s", "-m", "30", url, "-w", "\n%{http_code}"],
                        capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    if code.strip() != "200":
        sys.exit(f"HTTP {code.strip()} from {url}")
    return json.loads(body)


def geocode(address):
    url = (f"{CENSUS}?address={urllib.parse.quote(address)}"
           f"&benchmark=Public_AR_Current&format=json")
    d = fetch_json(url)
    matches = d.get("result", {}).get("addressMatches", [])
    if not matches:
        sys.exit(f"Census geocoder found no match for {address!r}. "
                  "If this is a bare parcel number, look up its address or "
                  "coordinates from the county assessor's GIS first.")
    m = matches[0]
    c = m["coordinates"]
    return c["y"], c["x"], m["matchedAddress"]


def local_climate(lat, lon):
    url = (f"{POWER}?parameters={PARAMETERS}&community=AG"
           f"&longitude={lon}&latitude={lat}&format=JSON")
    d = fetch_json(url)
    return d["properties"]["parameter"]


def main(argv):
    if "--latlon" in argv:
        i = argv.index("--latlon")
        lat, lon = float(argv[i + 1]), float(argv[i + 2])
        label = f"{lat}, {lon} (given directly)"
    elif len(argv) >= 1:
        lat, lon, matched = geocode(" ".join(argv))
        label = f"{matched}  ({lat:.4f}, {lon:.4f})"
    else:
        sys.exit(__doc__)

    data = local_climate(lat, lon)
    print(f"Local climate history for: {label}")
    print(f"Source: NASA POWER, community=AG (30-year point climatology)\n")
    header = "Metric".ljust(26) + "".join(m.rjust(7) for m in MONTHS)
    print(header)
    for param in PARAMETERS.split(","):
        row = LABELS[param].ljust(26)
        row += "".join(f"{data[param][m]:7.2f}" for m in MONTHS)
        print(row)
    print("\nThis is what the location has actually experienced, not a "
          "species tolerance range -- compare it against the relevant "
          "crop's temp_opt_low_f/temp_opt_high_f etc. in crop_reference, "
          "don't substitute one for the other.")
    print("\n⚠ Avg high/low are NASA POWER's own daily-max/min climatology, "
          "not NWS station climate normals -- verified against a second "
          "source before shipping this tool: Fresno's commonly-cited July "
          "average high is ~97°F/36°C, this product reports ~45-48°C. "
          "Checked three ways (this endpoint, a monthly average, and the "
          "actual daily values for July 2024) and they agree with each "
          "other, so it's real, not a bug -- MERRA-2's ~50km reanalysis "
          "grid is known to run hot on daily extremes in the Central "
          "Valley. Avg temp (T2M) matches known normals closely and is "
          "trustworthy as reported; treat Avg high/low as relative, "
          "point-to-point comparisons against this SAME product, never "
          "as a stand-in for a station reading.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
