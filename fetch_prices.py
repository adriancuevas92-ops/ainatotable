#!/usr/bin/env python3
"""Pull the USDA AMS Los Angeles Terminal Market vegetable report and match it to
the catalogue.

Keyless. No API credential is needed: the report PDFs are served directly from
www.ams.usda.gov/mnreports/. The marsapi.ams.usda.gov API does need a free key,
but it is not the route — that 403 sent us down the wrong path for a while.

Report codes were READ from the AMS index page, not guessed. Guessing cost nine
404s first:
    /market-news/fruit-and-vegetable-terminal-markets-standard-reports
    hc = Los Angeles · sx = San Francisco · hx = Chicago · nx = New York
    aj = Atlanta · bh = Boston · bp = Baltimore · du = Detroit
    mh = Miami · na = Philadelphia
    fr = Fresno SHIPPING POINT (fr_fv110 fruit, fr_fv120 vegetables)
    _fv010 fruit · _fv020 vegetables

⚠️ San Francisco (sx_fv020) exists but its latest report is dated 2025-05-01 —
eighteen months stale. That series appears to have stopped, so there is no
second live market to compare against. Re-check before relying on it.

Usage: python3 -I fetch_prices.py        (writes marts/usda_la_terminal_*.csv)
"""
import csv, io, os, re, subprocess, sys, datetime

LA   = "https://www.ams.usda.gov/mnreports/hc_fv020.pdf"
MART = "/home/adrian/data-engineering/marts"
CAT  = os.path.join(MART, "aina_to_table_crop_catalogue_v1_2026-11-03.csv")

# Where the report's commodity name differs from the catalogue's crop name.
# Each one checked by hand against the report text.
ALIAS = {"verdolaga":"Purslane", "chinese cabbage":"Napa cabbage",
         "jerusalem artichokes":"Sunchoke", "ginger root":"Ginger",
         "peas, snow":"Snow pea pods", "greens, mustard":"Chinese mustard greens",
         "squash, kabocha":"Kabocha", "tomatillos":"Tomatillo", "mushrooms":"Mushroom",
         "eggplant":"Eggplant, Chinese", "basil":"Basil (Thai, holy)",
         "chayote":"Chayote (fruit & tip)"}

def fetch(url, dest):
    r = subprocess.run(["curl","-s","--compressed","-m","40",url,"-o",dest,
                        "-w","%{http_code}"], capture_output=True, text=True)
    if r.stdout.strip() != "200":
        sys.exit(f"USDA returned HTTP {r.stdout.strip()} for {url}")
    return subprocess.run(["pdftotext","-layout",dest,"-"],
                          capture_output=True, text=True).stdout

def main():
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "hc_fv020.pdf")
    out = fetch(LA, tmp)
    d = re.search(r"((?:January|February|March|April|May|June|July|August|September|"
                  r"October|November|December) ?\d{1,2},? ?20\d\d)", out)
    report_date = d.group(1) if d else "unknown"

    crops = list(csv.DictReader(io.open(CAT, encoding="utf-8")))
    rows = []
    for b in re.split(r"\n-{2,}(?=[A-Z])", out):
        m = re.match(r"\s*([A-Z][A-Z &/,\-\.']{2,44}):", b)
        if not m: continue
        name = m.group(1).strip(); key = name.lower()
        crop = ALIAS.get(key) or next(
            (c["crop"] for c in crops
             if c["crop"].split("(")[0].strip().lower() == key), None)
        if not crop: continue
        body = re.sub(r"\s+", " ", b[m.end():])
        pr = re.findall(r"\b(\d{1,3}\.\d{2})(?:-(\d{1,3}\.\d{2}))?", body)
        if not pr: continue
        rows.append(dict(
            crop=crop, report_commodity=name,
            pack=(re.search(r"(\d+(?: \d/\d)? ?(?:lb|bushel)[a-z ]*cartons?|cartons?|"
                            r"bunches?|flats?)", body) or [""])[0],
            low=min(float(a) for a,_ in pr), high=max(float(b2 or a) for a,b2 in pr),
            origin_san_joaquin=("yes" if "SAN JOAQUIN VALLEY" in body else ""),
            origin_california=("yes" if re.search(r"\bCALIFORNIA\b", body) else ""),
            market="Los Angeles Terminal Market", report="HC_FV020",
            report_date=report_date, basis="wholesale, FOB basis, excludes freight",
            pulled=datetime.date.today().isoformat()))

    dest = os.path.join(MART, f"usda_la_terminal_specialty_prices_"
                              f"{datetime.date.today().isoformat()}.csv")
    with io.open(dest,"w",encoding="utf-8",newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in sorted(rows, key=lambda x: x["crop"]): w.writerow(r)
    print(f"{len(rows)} of {len(crops)} catalogue crops priced · report {report_date} · {dest}")
    print(f"  San Joaquin Valley origin: "
          f"{', '.join(r['crop'] for r in rows if r['origin_san_joaquin']) or 'none'}")
    # Snapshot discipline: a government series can stop. SF stopped in May 2025.
    # The CSV is dated and kept, so a published figure survives the source going away.
    return 0

if __name__ == "__main__":
    sys.exit(main())
