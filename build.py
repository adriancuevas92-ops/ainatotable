#!/usr/bin/env python3
"""Build the ʻĀina to Table public surface.

Six surfaces plus one generated product page per crop. Static output; no CMS.
The product pages come from aina_to_table_crop_catalogue_v2 — one template
decided once, as Gate C1 approved.

Copy is the approved decks C2a–C2f. Every factual line traces to a ledger claim
in Message Strategy v1 §6 (27 verified / 3 computed / 7 forbidden / rule 0).

The three Gate C conditions are ASSERTIONS here, not comments:
  1. relief.tlc and relief.boundary are emitted as one block and checked adjacent
  2. no price anywhere; the About page carries no currency at all
  3. no acres-per-grower figure ships without its denominator
A violation fails the build.

Usage: python3 -I build.py
"""
import csv, datetime, io, os, re, shutil, sys, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
# ── data, vendored into the repo 2026-11-04 ───────────────────────────
# These three CSVs are BUILT in /home/adrian/data-engineering/marts and COPIED
# here by tools/refresh_data.py. The build reads the repo copy and never the
# mart, deliberately:
#   • a GitHub Actions runner cannot see that directory at all, so a CI build
#     is impossible while the path is absolute;
#   • and if local and CI read different files they produce different sites
#     from the same commit. The committed copy is what the commit means.
# The marts keep dated filenames; these copies take STABLE names so this
# file never has to be edited to follow a date. data/PROVENANCE.txt records
# which dated mart each copy came from.
# Refresh with:  python3 -I tools/refresh_data.py
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MART = os.path.join(DATA, "crop_catalogue_v2.csv")
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ── the mark, from the locked masters (viewBox and geometry unchanged) ─────────
MARK = ('<svg viewBox="-1.2199 -1.2859 2.484 2.484" aria-hidden="true">'
 '<defs><mask id="mk{u}" maskUnits="userSpaceOnUse" x="-1.2199" y="-1.2859" width="2.484" height="2.484">'
 '<rect x="-1.2199" y="-1.2859" width="2.484" height="2.484" fill="#fff"/>'
 '<path d="M-0.0047,-0.0246 0.4131,-1.1892 0.6828,-1.0577 0.0222,-0.0114Z" fill="#000"/>'
 '<path d="M0.0219,-0.0121 1.2587,0.0254 1.217,0.3225 0.0177,0.0176Z" fill="#000"/>'
 '<path d="M0.0182,0.0171 0.3648,1.205 0.0693,1.2571 -0.0113,0.0223Z" fill="#000"/>'
 '<path d="M-0.0106,0.0226 -1.0333,0.7193 -1.1741,0.4544 -0.0247,-0.0039Z" fill="#000"/>'
 '<path d="M-0.0248,-0.0031 -1.0034,-0.7604 -0.795,-0.9762 -0.004,-0.0247Z" fill="#000"/></mask></defs>'
 '<g fill="currentColor"><g mask="url(#mk{u})">'
 '<path d="M0,0C-0.1817,-0.2787 -0.4728,-0.6002 -0.3227,-0.9063C-0.2124,-1.1329 0.1666,-1.1998 0.3478,-1.0246C0.4163,-0.757 0.1463,-0.3365 0,0Z"/>'
 '<path d="M0,0C0.2089,-0.2589 0.4247,-0.6351 0.7623,-0.587C1.0119,-0.5521 1.1925,-0.2123 1.0819,0.0141C0.8486,0.162 0.3652,0.0351 0,0Z"/>'
 '<path d="M-0,0C0.3108,0.1187 0.7353,0.2077 0.7938,0.5436C0.8377,0.7917 0.5704,1.0685 0.3209,1.0333C0.1082,0.8571 0.0794,0.3582 -0,0Z"/>'
 '<path d="M0,-0C-0.0168,0.3322 0.0297,0.7635 -0.2717,0.9229C-0.4941,1.0414 -0.84,0.8727 -0.8836,0.6245C-0.7817,0.3677 -0.3161,0.1863 0,-0Z"/>'
 '<path d="M0,0C-0.3212,0.0866 -0.7169,0.2642 -0.9617,0.0268C-1.1431,-0.1481 -1.0896,-0.5292 -0.8669,-0.6474C-0.5913,-0.6298 -0.2748,-0.2431 0,0Z"/></g>'
 '<path d="M-0.0507,-0.0342 0.4378,-0.7585 0.5392,-0.69 0.0507,0.0342Z"/>'
 '<ellipse cx="0.5386" cy="-0.7985" rx="0.135" ry="0.1242"/></g></svg>')

NAV = [("index.html","Home"),("catalogue.html","Catalogue"),("inspect.html","Inspect"),
       ("market.html","Market"),
       ("buyers.html","For Buyers"),("growers.html","For Growers"),
       ("growing.html","Growing"), ("qualify.html","Qualify")]

# ⭐ The one contact route, and it is shown as TEXT as well as linked. A mailto
# is unreliable for many readers and the page cannot tell whether it worked, so
# the address must be readable and selectable on its own.
EMAIL = "hello@ainatotable.com"

def contact_block(subject, line):
    """The ask, rendered the same way everywhere. Until 2026-11-04 the only
    contact route on the site sat on the 167 product pages and on none of the
    five entry surfaces — the pages least likely to be an entry point carried
    the only way to reach anyone."""
    href = f"mailto:{EMAIL}?subject={subject.replace(' ', '%20')}"
    return (f'<div class="note"><p><strong>{line}</strong></p>'
            f'<p style="font-size:1.0625rem"><a class="btn" href="{href}">'
            f'Email us &rarr;</a></p>'
            f'<p class="src">The address is <strong>{EMAIL}</strong> &mdash; copy it if the '
            f'button does nothing in your browser. It reaches a person, not a form, and nobody '
            f'is added to a list for writing to it.</p></div>')

def how_it_moves():
    """⭐ The logistics reader, as a SECTION rather than a page — decided
    2026-11-04. At one to two acres over roughly twenty miles, truckload
    carriers, brokers and terminal receivers are structurally out of reach:
    USDA AMS quotes produce truck rates per load to a single destination and
    states multi-pickup and multi-drop are not included, and there is no
    Fresno terminal market. So this says what actually moves, to whoever is
    moving it.

    🔴 It never leads with acreage. "One to two acres" reads to this reader as
    "there is no load here"."""
    return """
  <h3 id="how-it-moves" style="margin-top:12px">How it actually moves, and who is responsible for
      what</h3>
  <p>A load out of this network is a route, not a truckload. Several stops, a few pallets at each,
     on a fixed day of the week, inside one county. That is a different shape from the
     single-destination truckload the national rate reports describe, and we would rather say so
     than describe a lane that does not exist.</p>
  <p class="src">USDA AMS quotes produce truck rates per load for shipments in truckload volume to a
     single destination, and states that multi-pickup and multi-drop shipments are not included.
     There is no Fresno terminal market &mdash; Los Angeles is the only one in California.</p>
  <div class="note">
    <p><strong>Four things get settled in writing before anything is picked up</strong>, because each
       one is somebody&rsquo;s cost and all four are commonly left unassigned.</p>
    <ul style="padding-left:20px;display:flex;flex-direction:column;gap:8px">
      <li><strong>Who holds the temperature, and who pre-cools.</strong> Named per crop, not left to
          the vehicle that turns up.</li>
      <li><strong>Who contracts the carrier and who pays.</strong> Separately stated, because under
          the produce trade&rsquo;s own f.o.b. term the buyer carries transit risk
          <em>irrespective of how the shipment is billed</em> &mdash; so paying the freight and
          carrying the risk are two different questions.
          <span class="src">7 CFR &sect;46.43(i).</span></li>
      <li><strong>Who unloads.</strong> Federal law makes whoever requires the driver to help
          responsible for providing that help or compensating its cost, and bars coercion. A network
          that says nothing has left that unassigned.
          <span class="src">49 U.S.C. &sect;14103.</span></li>
      <li><strong>What condition on arrival means.</strong> See the contract section on this page.</li>
    </ul>
  </div>"""

META_DESC = ("Ingredients you can trace to the ground they came out of. The crops this region "
             "season, its scale and its source. Free, and sourced.")

# ── Gate C condition 1: these two are ONE block and are never separated ───────
RELIEF_TLC = ("Under the rule as written, the party that assigns a traceability lot code is "
  "never the retail food establishment and never the restaurant. That assignment happens "
  "upstream of you.")
RELIEF_BOUNDARY = ("That is what the rule says. It is not advice about your business, because "
  "we do not know your sales, your suppliers or your product list — and all three change the answer.")

def esc(t):
    return (t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii","ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+","-",s).strip("-").lower()
    return s or "crop"

def page(title, body, depth=0, desc=META_DESC, current=None):
    up = "../"*depth
    nav = "".join(
        f'<li><a href="{up}{h}"{" aria-current=\"page\"" if h==current else ""}>{esc(l)}</a></li>'
        for h,l in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{up}tokens.css"><link rel="stylesheet" href="{up}site.css">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<nav><div class="wrap wide">
  <a class="lockup" href="{up}index.html">{MARK.format(u="n")}<span>ʻĀina to Table</span></a>
  <ul>{nav}</ul>
</div></nav>
<main id="main">
{body}
</main>
<footer><div class="wrap wide">
  <p><strong>ʻĀina to Table</strong> — a network for ingredients you can trace to the ground they
     came out of, operating in the Fresno region. It qualifies land, publishes what is known about
     each crop, and settles the terms of the transaction. It never buys the food.</p>
  <p><strong>Contact</strong> &mdash; <a href="mailto:hello@ainatotable.com">hello@ainatotable.com</a><br>
     <span class="src">That address reaches a person, not a form. If you are a Fresno market or a
     grower and something here is wrong, that is the most useful mail we can get.</span></p>
  <p><a href="{up}about.html">About</a></p>
  <p class="src">Crops and scale: UC Cooperative Extension Fresno County, 2000–2001.
     Season: UCCE Fresno retail survey, 2010 — typical availability, not a live feed.
     County reporting: Fresno County Agricultural Crop and Livestock Reports, 2019–2024.
     Establishment counts: US Bureau of Labor Statistics, QCEW, Fresno County, 2024.</p>
  <p class="src">We do not inspect food and we do not certify it. We do not grow anything in
     Fresno County. We never buy it, sell it, take possession of it, negotiate its price or appear
     in the purchase path.</p>
</div></footer>
</body></html>
"""

# ⭐ The six crops checked for extension trial data, as DATA rather than as
# six words inside a paragraph. They were called "the six gap crops" — true
# when every one of them was absent from the county's reports. A4 then found
# the county NAMES negi, mitsuba and ube in its footnotes, so the sentence
# called three crops gaps that the county names. That is defect F4 from the
# Gate C3 audit returning by a different door: absence from a county report is
# not absence of production, and our own headline had made that mistake once
# already. Condition 6 below now fails the build on it.
# 🔴 PROVENANCE, corrected 2026-11-04. The recorded search covered SEVEN
# crops, not six, and not these six. Research/03 - Findings/"UCCE Specialty
# Crop Evidence Base and the v0 Catalogue" §2:
#
#   "Of the seven category-A crops I named yesterday — shiso, edamame, gobo,
#    negi, kabocha, shishito, mitsuba — UCCE has produced a yield trial for
#    exactly none."
#
# The site had shipped "shiso, edamame, negi, mitsuba, shishito and ube":
# gobo and kabocha dropped out, and UBE was added although no record anywhere
# shows ube was searched. A crop was named as checked that was not checked.
# The list is now the seven from the finding, held as data so the copy cannot
# drift from it again.
#
# "Category A" is from the Cuisine-to-Crop Demand Mapping skill: demand
# documented, no local production record. The skill marks A/B/C assignment
# from climate zone alone as [E] and routes category A to extension trial
# results before anything is contracted — which is the search that found
# nothing, and the reason this paragraph exists.
CHECKED_NO_TRIAL = ["Shiso", "Edamame", "Gobo", "Negi", "Kabocha",
                    "Shishito", "Mitsuba"]

def rows():
    with io.open(MART, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ⭐ C1. Every catalogue-size figure is computed here and nowhere else. Eight
# of them were hand-written into the copy as English words — "Seventy-four
# crops", "Sixteen of them" — and a hand-written count is a claim that goes
# stale silently the moment the mart changes. It did: the catalogue is now
# 167 rows.
WORDS = {1:"One",2:"Two",3:"Three",4:"Four",5:"Five",6:"Six",7:"Seven",
         8:"Eight",9:"Nine",10:"Ten",11:"Eleven",12:"Twelve",13:"Thirteen",
         14:"Fourteen",15:"Fifteen",16:"Sixteen",17:"Seventeen",
         18:"Eighteen",19:"Nineteen",20:"Twenty"}

def word(n):
    return WORDS.get(n, f"{n}")

def stats(rs=None):
    rs = rs if rs is not None else rows()
    cls = [r["crop_class"] for r in rs]
    meas = [r["county_measurement"] for r in rs]
    return {
        "total": len(rs),
        "commodity": cls.count("commodity"),
        "specialty": cls.count("specialty"),
        "gap": cls.count("gap"),
        "line_item": meas.count("line_item"),
        # 🔴 TWO different absences, and the copy must not swap them.
        # `absent` is the state in the LATEST report. `absent_all` is the crop
        # the county named in none of the five. A sentence that says "in any
        # report from 2020 to 2024" needs the second; it was built with the
        # first, which overstated it by ten crops.
        "absent": meas.count("absent"),
        "absent_all": sum(
            1 for r in rs
            if all(p.split(":")[1] == "absent"
                   for p in r["county_measurement_history"].split())),
        "footnote": sum(1 for m in meas if m.startswith("footnote")),
        # ⭐ generated, not written. The Home page quoted "eleven crops" as a
        # word — the same class of hand-written count C1 removed twelve of.
        "sjv": sum(1 for r in rs if r.get("la_origin_sjv") == "yes"),
        "priced": sum(1 for r in rs if r.get("la_price_low")),
    }

# ── absence strings (C2a §3) — the source that is silent, and the year ────────
# ⭐ SIX states, resolved by A4 from the 2020–2024 reports themselves rather
# than inherited from v1's label. The distinction that matters on every page is
# GRANULARITY: a line item carries its own acreage and value, and every
# footnote state carries none. Being NAMED in a footnote is not being measured
# — the footnote names the crop, the line above it holds the only figure.
MEASURE = {
 "line_item": ("named", "Its own line",
   "Fresno County reports this crop on its own line, with its own harvested "
   "acreage and its own gross value."),
 "footnote_oriental": ("named", "Named under “Oriental Vegetables”",
   "Fresno County names this crop — in the footnote to a single “Oriental "
   "Vegetables” line. The line carries the acreage and the value for all of "
   "them together; this crop has neither of its own."),
 "footnote_other": ("residual", "Named under “Other”",
   "Fresno County names this crop — in the footnote to a single “Other” "
   "vegetable line. That line carries one acreage and one value for every "
   "crop in it; this crop has neither of its own."),
 "footnote_fruit_other": ("residual", "Named under “Other” fruit",
   "Fresno County names this crop in the footnote to the “Other” line of the "
   "fruit and nut section. That line carries one value for all of them; this "
   "crop has none of its own."),
 "footnote_citrus_other": ("residual", "Named under “Other” citrus",
   "Fresno County names this crop in the footnote to the other-citrus line. "
   "That line carries one value for all of them; this crop has none of its own."),
 "absent": ("absent", "Not reported at all",
   "Fresno County does not report this crop, in any line and in any footnote, "
   "in any report from 2020 to 2024."),
}

# ── what kind of trade this is (D4, 2026-11-04) ─────────────────────────
# 🔴 crop_class is the right field and "Production gap" was a meaningless
# label on a trading tool. It names an EPISTEMIC category — how well we know the
# crop — when the reader is deciding what kind of trade they are entering.
# ⭐ Same data, same honesty, restated as a trading fact. The short label goes
# in the cell; the full reading goes in the filter and the legend, because five
# words cannot carry it and a truncated version would overclaim.
TRADE = {
 "commodity": ("Traded openly",
   "Traded openly — this county reports it on its own line and the terminal "
   "market quotes it. Price is most of the conversation."),
 "specialty": ("Few suppliers",
   "Few suppliers — this county measures it only inside an aggregate line, so "
   "no published local acreage or value exists for it on its own."),
 "gap": ("Commission only",
   "Nobody here reports growing it — this county names it in no line and no "
   "footnote, so a buyer would be commissioning it rather than sourcing it."),
}

def trade_chip(r):
    short, _ = TRADE[r["crop_class"]]
    return f'<span class="chip {esc(r["crop_class"])}">{esc(short)}</span>'

def price_cell(r):
    """🔴 The blank is the risk here, not the figure.

    On a record of what is known, an empty cell reads as "the record is thin
    here", which IS this site's thesis. On a trading tool the same cell reads
    as "nothing is available", which is false and is exactly the FTC
    net-impression failure. So the blank is LABELLED, and the label says which
    of the two it is — not quoted is not unavailable.
    """
    if not r["la_price_low"]:
        return '<span class="src">Not quoted</span>'
    lo, hi = float(r["la_price_low"]), float(r["la_price_high"])
    amt = f'${lo:.2f}' + (f'&ndash;${hi:.2f}' if hi != lo else "")
    pack = f'<span class="aka">{esc(r["la_pack"])}</span>' if r["la_pack"] else ""
    return amt + pack

def origin_cell(r):
    """⭐ The argument of the whole site in one cell: grown here, priced there.

    ⚠ We flag San Joaquin Valley and California and NOTHING else, so a dash
    means the report's block did not name either — not that the crop came from
    abroad. The legend says so; the cell must not imply more than was checked.
    """
    if r["la_origin_sjv"] == "yes":
        return '<span class="chip gap">San Joaquin Valley</span>'
    if r.get("la_origin_ca") == "yes":
        return "California"
    return '<span class="src">&mdash;</span>'

def months_attr(r):
    """The 12-month strip as one attribute, so "in season now" is resolved in
    the BROWSER against the reader's own date. 🔴 Resolving it at build time
    would bake November into a static page and quietly lie every other month."""
    return "".join((r[m] or "-")[:1] for m in MONTHS)

def county_chip(r):
    cls, label, _ = MEASURE[r["county_measurement"]]
    return (cls, label)

def county_sentence(r):
    return MEASURE[r["county_measurement"]][2]

def window_label(r):
    w = r["window"] or ""
    return {"Jan-Dec":"Year-round","NOT IN 2010 MATRIX":"No data",
            "special orders only":"Special order only"}.get(w, w or "No data")

def season_cell(r):
    marks = [r[m] for m in MONTHS]
    if not any(marks):
        return f'<span class="win show">{esc(window_label(r))}</span>'
    strip = "".join('<i class="dk"></i>' if v=="S" else ('<i class="lt"></i>' if v=="P" else '<i></i>')
                    for v in marks)
    return f'<span class="strip">{strip}</span><span class="win">{esc(window_label(r))}</span>'

def season_sentence(r):
    if not r["window"]:
        # 🔴 This branch was missing and the fall-through built the string
        # "Typically available  —  months. Source: UCCE Fresno retail survey,
        # 2010." for every crop the 2010 survey never covered: an empty claim
        # with a real citation bolted to it. A citation for nothing is worse
        # than no citation.
        return ('No Fresno availability data exists for this crop. The 2010 '
                'retail survey covered Asian specialty vegetables and did not '
                'reach it, and we have found no other published Fresno source.')
    if r["window"] == "NOT IN 2010 MATRIX":
        return ('No season data exists for this crop. The 2010 retail survey did not cover it. '
                'Not “unknown” — no published Fresno source has measured it.')
    if r["special_orders_only"] == "yes":
        return 'Fresno specialty markets carried this on special order only, 2010.'
    if r["window"] == "Jan-Dec":
        return 'Typically available all twelve months. Source: UCCE Fresno retail survey, 2010.'
    return (f'Typically available {r["window"]} — {r["months_available"]} months. '
            f'Source: UCCE Fresno retail survey, 2010.')

def is_gap(r):
    # 🔴 B3. The gap chip renders from crop_class and nothing else. Keyed to
    # the raw county status it fired on commodity crops the county reports on
    # their own line — a "contractable gap" chip on garlic, onions or table
    # grapes, each a crop this county grows at scale.
    return r["crop_class"] == "gap"

def is_specialty(r):
    return r["crop_class"] == "specialty"

# ── product page ──────────────────────────────────────────────────────────────
def product_page(r):
    name = r["crop"]
    blocks = []
    def blk(lbl, val, cav=None):
        c = f'<p class="cav">{cav}</p>' if cav else ""
        blocks.append(f'<div class="blk"><p class="lbl">{esc(lbl)}</p>'
                      f'<p class="val">{val}</p>{c}</div>')

    # 7 season · 8 county · 9 local — always present, absence included
    blk("Typically available", esc(window_label(r)), esc(season_sentence(r)))
    # 🔴 A variety matched to a line item does NOT have its own line. Rendered
    # from county_measurement alone, the page said "reports this crop on its
    # own line, with its own harvested acreage and its own gross value" and
    # then, in the very next block, "the line carries a figure, the variety
    # does not". Both blocks were generated, so both shipped, contradicting
    # each other three inches apart.
    # A variety sits INSIDE a county line. The line is published supply — its
    # own acreage and its own value — which is why these crops are classed
    # commodity. But the line is reported for the crop, not for the variety,
    # and "reports THIS CROP on its own line" would overstate it by one step.
    if r["crop_class_basis"].startswith("inside the county's"):
        line = r["crop_class_basis"].split("county's ", 1)[-1].split(" line")[0]
        blk("County reporting", f"Inside the &ldquo;{esc(line)}&rdquo; line",
            esc(f"Fresno County reports {line.lower()} on its own line, with its "
                f"own harvested acreage and its own gross value. It does not "
                f"break this variety out separately — but unlike the crops "
                f"it files under an aggregate, the supply here is published."))
    else:
        blk("County reporting", esc(MEASURE[r["county_measurement"]][1]),
            esc(county_sentence(r)))
    blk("How this crop is classed", esc(r["crop_class"].capitalize()),
        esc(r["crop_class_basis"].capitalize() + "."))
    local = r["local_status"]
    if not local:
        # The 2000 survey was a survey of Asian specialty vegetables. For a
        # crop outside that frame, "no local production record" would be a
        # claim about Fresno; the truth is a claim about the survey.
        blk("Grown in Fresno County", "Not established here",
            "The 2000 grower survey covered Asian specialty vegetables and did "
            "not cover this crop, so we have no grower-level local record "
            "either way. What the county reports about it is above.")
    else:
        blk("Grown in Fresno County",
            "No local production record of any kind" if local.startswith("A ") else esc(local.capitalize()),
            None if not local.startswith("A ") else "No acreage was recorded for this crop in 2000."
                  if not r["ucce_acres_2000"] else None)
    # 10 scale — Gate C condition 3: never without its denominator
    if r["ucce_acres_2000"] and r["ucce_farmers_2000"]:
        blk("Scale, 2000", f'{r["ucce_acres_2000"]} acres across {r["ucce_farmers_2000"]} growers',
            f'{r["acres_per_farmer_2000"]} acres each, on average, across the 26 catalogue crops that '
            f'carry both an acreage and a grower count. UCCE, 2000 — twenty-six years old. Read it as '
            f'the shape of this crop’s production, not its current size.')
    elif r["ucce_acres_2000"]:
        blk("Scale, 2000", f'{r["ucce_acres_2000"]} acres county-wide',
            "Growers not recorded for this crop. UCCE, 2000.")
    elif r["source_set"].startswith("v1"):
        blk("Scale, 2000", "No acreage recorded",
            "The 2000 survey covered this crop and recorded no acreage for it.")
    else:
        # 🔴 "No acreage was recorded in the 2000 survey" implies the survey
        # looked. For a crop outside its frame it never did, and the two
        # statements carry opposite weight for a grower reading the page.
        blk("Scale, 2000", "Not surveyed",
            "The 2000 survey covered Asian specialty vegetables. It did not "
            "cover this crop, so there is no 2000 figure to report — which is "
            "not the same as a figure of zero.")
    # 10b what the alternative cost — the figure ships as REPORTED, attributed
    # and dated, never converted into a target.
    #
    # ⭐ Three build patterns fired on the first draft of this block and all
    # three were right. The label read "Reported wholesale price"
    # (\bwholesale price); the value read "$26.00 per 30 lb cartons"
    # ($N per X); the caveat read "not a figure we suggest anyone trade at"
    # (we suggest — negated, and a negation does not defeat a substring
    # match). The COPY was rewritten to pass the check and the patterns were
    # not touched. Fourth time that has been the right call.
    if r["la_price_low"]:
        lo, hi = r["la_price_low"], r["la_price_high"]
        amt = f"${lo}" if lo == hi else f"${lo}&ndash;${hi}"
        origin = ("San Joaquin Valley" if r["la_origin_sjv"] == "yes"
                  else "California" if r.get("la_origin_ca") == "yes" else "")
        bits = ['Los Angeles Terminal Market, reported as '
                '\u201c' + r["la_report_commodity"] + '\u201d. '
                + r["la_report"] + '.']
        if r["la_pack"]:
            bits.append('Pack as quoted: ' + r["la_pack"] + '.')
        bits.append('Wholesale, f.o.b. shipping point as USDA reports it '
                    '(7 CFR \u00a746.43(i)) \u2014 the figure excludes freight.')
        if origin:
            bits.append('Origin quoted: ' + origin + '.')
        blk("What Los Angeles paid", amt,
            esc(" ".join(bits)) + ' <strong>This is what the alternative to '
            'buying locally cost in that market on that day. It is not a local '
            'figure, it is not what a grower here receives, and it is not a '
            'figure we are suggesting anyone trade at.</strong>')
    elif r["crop_class"] != "gap":
        blk("What Los Angeles paid", "Nothing published",
            "No terminal market report and no shipping-point report carries a "
            "figure for this crop. Not a low one \u2014 none published at all.")
    # 11 cuisines
    if r["cuisines"]:
        chips = " ".join(f'<span class="chip">{esc(c)}</span>' for c in r["cuisines"].split(";"))
        blk("Cuisine", chips)
    # 12 vegan role / protein
    if r["vegan_role"] or r["protein_g_per_100g_est"]:
        v = esc(r["vegan_role"]) if r["vegan_role"] else "—"
        p = (f'About {r["protein_g_per_100g_est"]} g protein per 100 g. Estimated from UCCE’s own '
             f'nutrition table, normalised to 100 g. Approximate.') if r["protein_g_per_100g_est"] else None
        blk("Plant-forward role", v, p)
    # economics — the restraint, rendered only where a study exists
    econ = ""
    if r["ucce_cost_study"] == "yes":
        econ = ('<div class="note"><p><strong>A UCCE cost study exists for this crop (2005).</strong> '
                'We do not publish its figures until they have been re-verified and adjusted.</p></div>')
    # 6 practice — only where the 2001 guide covers it
    practice = ""
    if r["ucce_guide_2001"] == "yes":
        practice = ('<div class="spec"><p class="lbl">How it generally grows</p>'
          '<p>UC Cooperative Extension covers this crop in <em>Guide to Asian Specialty Vegetables in '
          'the Central Valley, CA</em>, September 2001 — identification and general culture.</p>'
          '<p class="src">That guide is not an agronomic manual. It says almost nothing about soil or '
          'climate per crop, and we will not pad it out with figures it does not contain. '
          'This is how the plant generally grows. It is not guidance for growing it here.</p></div>')
    # 13 gap — grower view, with the mandatory caveat
    gap = ""
    if is_gap(r):
        why = " ".join([county_sentence(r),
                        "No local production record of any kind." if r["local_status"].startswith("A ") else "",
                        season_sentence(r)]).strip()
        gap = ('<div class="absent-note"><p><span class="chip gap">Contractable</span></p>'
          '<p class="cav"><strong>Agronomic viability not established for this region — see '
          'extension trial data.</strong></p>'
          f'<p>Why this is a gap: {esc(why)}</p>'
          '<p class="src">We show a gap and the source for each part of it. We do not tell anyone '
          'what to plant.</p></div>')

    aka = f'<p class="aka">Also called {esc(r["also_known_as"])}</p>' if r["also_known_as"] else ""
    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow"><a href="../catalogue.html">Catalogue</a></p>
  <div class="crop-head"><h1>{esc(name)}</h1>{aka}</div>
  <div class="blocks">{''.join(blocks)}</div>
  {practice}
  {econ}
  {gap}
  <div class="note"><p><strong>{"Want this crop?" if r["crop_class"] != "gap" else "Thinking of growing this?"}</strong>
     {'<a href="../buyers.html">For Buyers</a> says what the contract settles before price comes up. If you farm, <a href="../growers.html">For Growers</a> is the page for it.' if r["crop_class"] != "gap" else '<a href="../growers.html">For Growers</a> is the page for it \u2014 but read the caveat above first: nobody has published a trial for this crop in this valley.'}</p></div>
  <p class="src">Four things are deliberately not on this page yet, and it is worth saying which.
     <strong>Botanical name and native range:</strong> not published for this crop &mdash; the
     structured native-distribution source refuses automated access, and an occurrence record is not
     a native range. <strong>Climate preference:</strong> the 2001 guide is a crop-identification
     leaflet, not an agronomic manual, and it carries almost nothing on soil or climate per crop; we
     will not invent one. <strong>A photograph:</strong> none, by decision &mdash; a page with no
     photograph is a gap you will forgive, and a page with the wrong plant on it is not.</p>
</div></section>"""
    return page(f"{name} — ʻĀina to Table", body, depth=1,
                desc=f"{name}: season, county reporting, scale and sources.")

# ── catalogue index ───────────────────────────────────────────────────────────
def catalogue_page(rs):
    """The index, restructured 2026-11-04 on Adrian's decisions D2–D4.

    ⭐ Adrian, on what the catalogue is FOR: "something that a buyer and grower
    could come and see the price in which a commodity is trading at and look to
    enter in a contract or plan their next crop cycle even."

    🔴 What it had been doing instead: five columns of which FOUR were one
    fact. County reporting, Class and Production gap are all derived from
    county reporting — 167 rows displaying one piece of metadata three times,
    beside two surveys (2000 acreage, 2010 availability) covering a fifth and a
    half of the rows. And the metadata is about the quality of OUR KNOWLEDGE,
    not about the crop. Right to publish while establishing that local supply
    is invisible; wrong to lead a trading tool with.

    D2 the cuisine filter is gone — it covered 74 of {n} rows, so using it was
       the fastest way to see LESS of what is here. Cuisine stays on the
       product page, where it is a fact about the crop and not a lens on the
       whole catalogue.
    D3 price and origin lead. County reporting and Scale 2000 move to the
       product page, which already carries both — checked, nothing is lost.
    D4 the class is relabelled in trading terms. See TRADE.
    """
    S = stats(rs)
    trs = []
    for r in rs:
        trs.append(f"""    <tr data-class="{esc(r['crop_class'])}"
        data-priced="{'yes' if r['la_price_low'] else 'no'}"
        data-origin="{'sjv' if r['la_origin_sjv']=='yes' else ('ca' if r.get('la_origin_ca')=='yes' else 'other')}"
        data-months="{esc(months_attr(r))}">
      <td><a href="crops/{slug(r['crop'])}.html">{esc(r['crop'])}</a>
          {f'<span class="aka">{esc(r["also_known_as"])}</span>' if r["also_known_as"] else ''}</td>
      <td>{price_cell(r)}</td>
      <td>{origin_cell(r)}</td>
      <td>{season_cell(r)}</td>
      <td>{trade_chip(r)}</td>
    </tr>""")

    kopts = "".join(
        f'<option value="{esc(k)}">{esc(full)}</option>'
        for k, (short, full) in TRADE.items())

    body = f"""<section class="band"><div class="wrap wide stack">
  <p class="eyebrow">Catalogue</p>
  <h1>{S["total"]} crops, the reference price where one exists, and the origin the report named</h1>
  <p>A reference price, the pack it is quoted in, the origin the report named, and the
     season where one has ever been measured. Where the record is silent, this says so.</p>
  <div class="note">
    <p><strong>This is a reference-price and record view. It is not a list of what is available
       this week, and no price here is an offer.</strong> {S["priced"]} of these
       {S["total"]} crops were quoted in the terminal-market reports behind this page;
       the other {S["total"] - S["priced"]} say <em>not quoted</em>, which means no report named
       them — not that nobody is growing or selling them.</p>
    <p class="src">Said at the top because a table of {S["total"]} crops with a price column reads
       as {S["total"]} things for sale however carefully each cell is worded, and that impression
       would be the one thing on this site we had got wrong. Availability is not something this
       page can tell you; it needs members, and that is
       <a href="growers.html">For Growers</a> and <a href="buyers.html">For Buyers</a>.</p>
  </div>
  <div class="tools">
    <label for="fk">Kind of trade</label>
    <select id="fk"><option value="">Any kind</option>{kopts}</select>
    <label for="fq">Price</label>
    <select id="fq"><option value="">Quoted or not</option>
      <option value="yes">Quoted in the latest report</option>
      <option value="no">Not quoted</option></select>
    <label for="fo">Origin quoted</label>
    <select id="fo"><option value="">Any origin</option>
      <option value="sjv">San Joaquin Valley</option>
      <option value="ca">California</option></select>
    <label for="fs" class="chk"><input type="checkbox" id="fs"> In season now</label>
    <span class="src" id="count">{len(rs)} of {len(rs)} crops</span>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Crop</th><th>Trading at</th><th>Origin quoted</th>
      <th>In season here</th><th>What kind of trade this is</th></tr></thead>
    <tbody id="tb">
{chr(10).join(trs)}
    </tbody>
  </table></div>
  <div class="note">
    <p><strong>What kind of trade this is</strong>, in full:</p>
    <p class="src">{" ".join(f"<strong>{esc(short)}.</strong> {esc(full.split(chr(8212),1)[-1].strip())}" for short, full in TRADE.values())}</p>
  </div>
  <div class="note">
    <p><strong>Where the prices come from, and what they are not.</strong> They are the USDA
       Agricultural Marketing Service terminal-market reports — wholesale, f.o.b. shipping point
       as USDA reports it (7 CFR &sect;46.43(i)), so the figure <em>excludes freight</em>. A
       terminal market is not Fresno: it is where this valley&rsquo;s produce is trucked to and
       priced. <strong>Read it as the price of the alternative channel, not as a local price and
       not as a target.</strong> Every figure here comes from the reports of
       {esc(price_report_date().strftime("%-d %B %Y")) if price_report_date() else "an undated day"},
       and the build refuses to publish prices more than {MAX_PRICE_AGE_DAYS} days old.</p>
    <p class="src">Origin is flagged for the San Joaquin Valley and for California and for nothing
       else, so a dash in that column means the report&rsquo;s block for that crop named neither
       — not that it came from abroad. {S["sjv"]} of these crops were quoted with a San Joaquin
       Valley origin: grown here, trucked away, priced there.</p>
  </div>
  <div class="note">
    <p><strong>The two season marks are deliberately not named.</strong> The 2010 survey marked two
       kinds of availability and defined neither. In the six crops carrying both marks the lighter one
       always precedes the darker — but two crops are light throughout, which that reading does not
       explain. So both are shown and neither is labelled. <strong>In season now</strong> filters on
       either mark for the current month, and a crop the survey never reached cannot match it.</p>
    <p>{S["absent_all"]} of these crops are named by this county in no line and no footnote of
       any report from 2020 to 2024, and {S["absent"] - S["absent_all"]} more have dropped out of
       the latest one. {S["footnote"]} are named only in a footnote
       to an aggregate line, with no acreage and no value of their own &mdash; being named is not
       being measured. Only {S["line_item"]} have a line of their own. <span class="src">That
       record now sits on each crop&rsquo;s own page, where it is provenance rather than
       headline.</span></p>
  </div>
  <div class="note">
    <p><strong>Found something you want, or something you grow?</strong> The two pages that do
       something about it are
       <a href="buyers.html">For Buyers</a> and <a href="growers.html">For Growers</a>.</p>
  </div>
</div></section>
<script>
(function(){{
  var tb=document.getElementById('tb'), cnt=document.getElementById('count'),
      kse=document.getElementById('fk'), qse=document.getElementById('fq'),
      ose=document.getElementById('fo'), sch=document.getElementById('fs');
  var rows=[].slice.call(tb.rows), total=rows.length;
  // The reader's month, not the build's: a static page built in November and
  // read in March must not claim March's seasons are November's.
  var mi=new Date().getMonth();
  function apply(){{
    var k=kse.value, q=qse.value, o=ose.value, s=sch.checked, n=0;
    rows.forEach(function(tr){{
      var m=(tr.getAttribute('data-months')||'')[mi]||'-';
      var ok=(!k||tr.getAttribute('data-class')===k)
          && (!q||tr.getAttribute('data-priced')===q)
          && (!o||tr.getAttribute('data-origin')===o)
          && (!s||m==='S'||m==='P');
      tr.hidden=!ok; if(ok)n++;
    }});
    cnt.textContent=n+' of '+total+' crops';
  }}
  [kse,qse,ose,sch].forEach(function(el){{el.addEventListener('change',apply);}});
  apply();
}})();
</script>"""
    return page("Catalogue — ʻĀina to Table", body, current="catalogue.html")

def qualify_page():
    """⭐ The join path, rewritten 2026-11-04 after Adrian corrected it.

    The first version had NINE dimensions, including soil testing and an
    irrigation survey. Qualification is TWO things: the party has the land, and
    the party has the capacity to enter into the contract. Everything else is a
    service, offered where wanted.

    🔴 The over-build contradicted a finding already on record: half the
    production value of fruit, nut and berry farms is already under contract,
    94% on the farms that use them, and most smaller farms are registered and
    know their own practices. A nine-point audit with soil testing is built for
    a grower who needs teaching — and would have read as condescending to the
    reader it was aimed at. This version assumes competence."""
    S = stats()
    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow">Qualify</p>
  <h1>Two questions. Do you have the land, and can you enter into the contract?</h1>
  <p>That is the whole of it. <strong>Qualification is not a test of how you farm</strong> &mdash; it
     establishes that the ground is real and committable, and that there is a party on your side who
     can sign and be paid.</p>
  <p class="src">We are assuming you know your own operation. Most farms this size are already
     registered and already know their practices, and a network that opened by auditing your
     competence would deserve the answer it got.</p>

  <div class="cards">
    <div class="card"><h3>You have the land</h3>
      <p>A parcel, and ownership or a lease that lets you commit the ground for a season. If the
         acreage is idle, that it is yours to put back into production.</p></div>
    <div class="card"><h3>You can enter into the contract</h3>
      <p>A party that can sign a commercial agreement, and a route to be paid. Sole proprietor or
         entity &mdash; it does not matter which.</p></div>
  </div>
  <p class="src">Nothing else gates it. There is no minimum acreage, no certification requirement,
     and no judgement about your methods.</p>

  <h3 style="margin-top:12px">What you get, and it is yours to keep</h3>
  <p>A dated record of what was verified and when, with the sources attached. <strong>You hold it.
     You can show it to any buyer, including one who has never heard of us</strong> &mdash; which is
     the point. A record about your operation belongs to you, and it is worth more to you if it
     travels.</p>
  <p class="src">It states its own limits too: what was checked, what you told us rather than showed
     us, and when. A record that does not say what it left out is not worth much to the person
     reading it.</p>

  <h3 style="margin-top:12px">Available if you want it. Not required, and not a condition.</h3>
  <p>Some growers want these and some have no use for them. <strong>Neither answer affects whether
     you qualify.</strong></p>
  <ul style="padding-left:20px;display:flex;flex-direction:column;gap:10px">
    <li><strong>Where you stand in the federal thresholds.</strong> Read against your own three-year
        average. Two different rules both say &ldquo;$25,000&rdquo; in their text and adjust from
        different base years &mdash; a farm at $32,000 is under one and over the other.
        <span class="src">The traceability figure lands near <strong>$29,800</strong>
        (21 CFR &sect;1.1305(a), base year 2020; FDA has not published the adjusted figure, so we
        computed it by FDA&rsquo;s own method and reproduced two figures FDA <em>has</em> published to
        within 0.033%). The Produce Safety figure, which FDA does publish, is <strong>$34,324</strong>
        (&sect;112.4(a), base year 2011). This reading is free and it is on this site whether you
        join or not.</span></li>
    <li><strong>A soil test for a specific field.</strong> A dated laboratory result, if you want one
        for ground you have not cropped recently.</li>
    <li><strong>An irrigation assessment.</strong> Whether water reaches the ground and at what rate,
        by a partner who has worked in irrigation in this industry for over a decade. Useful mostly
        where acreage has been idle long enough that nobody is certain any more.</li>
  </ul>
  <div class="note">
    <p><strong>A soil test tells you what your soil is. It does not tell you what a crop will do in
       it.</strong></p>
    <p>For the crops this county does not count, <strong>nobody has published a trial in this valley
       at all</strong>. Yield, quality and timing would need that trial data and there is none, so a
       measured soil result is an answer to &ldquo;what have I got?&rdquo; rather than &ldquo;will
       this work?&rdquo;</p>
  </div>

  <h3 style="margin-top:12px">What this is not</h3>
  <div class="note">
    <p><strong>Not a food-safety certification.</strong> We are not a certifying body. If you hold a
       certification we can record it; we cannot grant one.</p>
    <p><strong>Not a guarantee of supply, volume or condition.</strong> That is the contract&rsquo;s
       job, in the produce trade&rsquo;s own terms.</p>
    <p><strong>Not advice about your own position.</strong> The threshold reading comes with its
       citation attached. The arithmetic about your farm stays yours.</p>
    <p><strong>Not a judgement that anyone ought to buy from you.</strong> The record says what is
       true of your operation. What a buyer does with it is the buyer&rsquo;s decision.</p>
  </div>

  {contact_block("Registering interest", "Two things to send, and we will tell you where that leaves you.")}
  <p class="src">The parcel number or nearest cross-streets, and roughly how much ground is sitting
     idle. <strong>That is enough.</strong> Dues and terms are published once the network&rsquo;s
     structure is settled, so there is nothing to buy today &mdash; and the {S["total"]} crop pages,
     the market conditions and the threshold reading are free to read either way.</p>
</div></section>"""
    return page("Qualify — ʻĀina to Table", body, current="qualify.html",
                desc="Qualification is two things: you have the land, and you can enter into the contract. Everything else is a service, not a gate.")

def growing_page():
    """⭐ The free outward-facing material, 2026-11-04. Adrian: the soil-health
    and growing information is the public portion of the site.

    🔴 The line this page walks: the valley's conditions are a matter of record
    and they are extraordinary. They still do not establish that a particular
    uncounted crop performs here — that needs trial data and there is none.
    Both are true and the page holds both, because holding only the first is a
    suitability claim with nothing behind it."""
    S = stats()
    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow">Growing</p>
  <h1>Why this valley, what a soil test actually tells you, and what neither of those settles</h1>
  <p>All of this is free and none of it sits behind anything. It is the part of the record we can
     publish without asking you for a thing.</p>

  <h2 style="margin-top:28px">Why produce from here reaches the rest of the world</h2>
  <p>This is not a local boast. It is a published share of national output.</p>
  <div class="cards">
    <div class="card"><h3>Nearly half the country&rsquo;s vegetables</h3>
      <p>And <strong>over three-quarters of the country&rsquo;s fruits and nuts</strong>, grown in
         California.</p>
      <p class="src">California Department of Food and Agriculture, California Agricultural
         Production Statistics.</p></div>
    <div class="card"><h3>$64.7 billion in cash receipts</h3>
      <p>Received by California&rsquo;s farms and ranches in 2025, across more than 400
         commodities.</p>
      <p class="src">CDFA, as above. Agricultural exports totalled $23.8&nbsp;billion in 2024.</p></div>
    <div class="card"><h3>$9.03 billion from this county alone</h3>
      <p>Fresno County&rsquo;s total gross production value for 2024, across <strong>over 300
         different commodities</strong>, shipped to <strong>more than 91 countries</strong>.</p>
      <p class="src">Fresno County Agricultural Crop and Livestock Report, 2024.</p></div>
  </div>

  <h3 style="margin-top:12px">What the conditions actually are</h3>
  <p>The valley has a <strong>Mediterranean climate</strong>: hot dry summers, mild wet winters, and
     almost no summer rain. Three things follow from that, and together they are most of the
     explanation.</p>
  <ul style="padding-left:20px;display:flex;flex-direction:column;gap:10px">
    <li><strong>A long frost-free season.</strong> Enough of one that two plantings of a short-cycle
        crop are ordinary rather than ambitious.</li>
    <li><strong>Dry harvest weather.</strong> Rain at the wrong moment splits fruit, spreads field
        disease and stops a crew getting in. Here the summer is reliably dry, so a risk the rest of
        the country carries is mostly absent.</li>
    <li><strong>Deep alluvial valley floor, and water that is delivered rather than waited for.</strong>
        The ground was built by rivers coming off the Sierra, and the water arrives through
        infrastructure on a schedule. <span class="src">Which is also why an irrigation question is a
        real question here rather than a formality.</span></li>
  </ul>
  <div class="note">
    <p><strong>And here is the part that matters for this network.</strong> Wherever the growing is
       good and ground is <em>still</em> sitting idle, whatever is keeping it idle is
       <strong>not agronomic</strong>.</p>
    <p>It is market access, or scale, or labour, or water allocation, or the simple fact that no buyer
       ever asked. <strong>Those are structural, and a structural problem is the kind a contract and a
       network can actually move.</strong></p>
    <p class="src">That is the thesis in one sentence, and it does not depend on this valley being
       exceptional &mdash; it holds anywhere produce is priced by volume while somebody nearby holds
       ground that is earning nothing. It is also why this venture is about terms and counterparties
       rather than agronomy: we are not proposing to teach anyone to farm.</p>
  </div>

  <h2 style="margin-top:28px">How to read a soil test</h2>
  <p>A laboratory report is a list of measurements with no narrative attached. Here is what the common
     lines mean. <strong>None of it is specific to your ground and none of it is advice</strong>
     &mdash; it is how to read the page you were handed.</p>
  <div class="tbl"><table>
    <thead><tr><th>What is measured</th><th>What it is telling you</th></tr></thead>
    <tbody>
    <tr><td><span class="crop">pH</span></td><td>Acidity or alkalinity. It governs whether nutrients
        already present are available to a plant at all &mdash; a nutrient can be in the soil and
        chemically out of reach. Valley soils commonly run neutral to alkaline.</td></tr>
    <tr><td><span class="crop">Texture</span><span class="aka">sand, silt, clay</span></td>
        <td>How fast water moves through and how much the soil holds. It sets an irrigation interval
        more than almost anything else, and it is the one property you cannot change.</td></tr>
    <tr><td><span class="crop">Organic matter</span></td><td>Structure, water-holding, and the
        reservoir that slowly releases nitrogen. Usually low in long-cultivated valley ground, and
        the figure most responsive to what is done next.</td></tr>
    <tr><td><span class="crop">Nitrogen, phosphorus, potassium</span></td><td>The three removed in
        quantity by a crop. Nitrogen moves with water and reads as a current snapshot; phosphorus and
        potassium read as a reserve.</td></tr>
    <tr><td><span class="crop">Salinity</span><span class="aka">EC &mdash; electrical conductivity</span></td>
        <td>Total dissolved salts, and the line to read first on this valley floor: irrigation water
        carries salt in, dry summers concentrate it, and crops differ widely in what they
        tolerate.</td></tr>
    <tr><td><span class="crop">Sodium</span><span class="aka">SAR, exchangeable sodium</span></td>
        <td>Distinct from salinity. Sodium degrades soil <em>structure</em> &mdash; it disperses clay,
        seals the surface and stops water infiltrating. Ground can be low in total salt and still have
        a sodium problem.</td></tr>
    <tr><td><span class="crop">Micronutrients</span></td><td>Zinc, boron, iron and others. Needed in
        small amounts; boron in particular has a narrow band between deficient and toxic.</td></tr>
    <tr><td><span class="crop">Lead and heavy metals</span></td><td>Not on a standard agricultural
        panel &mdash; it has to be asked for. It matters where ground has a non-farm history, and
        uptake differs sharply by crop, with leafy and root crops highest.</td></tr>
    </tbody>
  </table></div>

  <h3 style="margin-top:12px">What the test does not tell you, and this is the important part</h3>
  <div class="note">
    <p><strong>A soil test tells you what your soil is. It does not tell you what a crop will do in
       it.</strong> Those are different questions and only the first has an answer on paper.</p>
    <p><strong>The same goes for everything above about the valley.</strong> A region producing
       three-quarters of the nation&rsquo;s fruit tells you the question is worth asking. It does not
       tell you a particular crop performs on a particular field &mdash; and for {S["gap"]} of the
       crops in this catalogue the county reports production in no line and no footnote, while
       <strong>no extension trial has been published in this valley at all</strong> for the ones we
       went looking for.</p>
    <p class="src">We would rather give you the measurements, the published shares and the gaps and
       let you weigh them, than convert any of it into a claim about your ground that nobody has
       established. Anyone who tells you otherwise about an uncounted crop is guessing.</p>
  </div>

  <p class="src">Next: <a href="catalogue.html">the catalogue</a> records what is known about
     {S["total"]} crops, including where the record is silent.
     <a href="growers.html">For Growers</a> is the page about contracting ground you already hold.</p>
</div></section>"""
    return page("Growing — ʻĀina to Table", body, current="growing.html",
                desc="Why this valley grows what it does, how to read a soil test, and what neither of those establishes about a particular crop on a particular field.")


# ── Home (C2c) ────────────────────────────────────────────────────────────────
def home_page():
    S = stats()
    body = f"""<section class="hero"><div class="wrap stack">
  <span class="mk">{MARK.format(u="h")}</span>
  <p class="eyebrow">A network, not a middleman. Free information, and no product to buy first.</p>
  <h1>A quality ingredient is one you can trace to the ground it came out of.</h1>
  <p>ʻĀina to Table exists to make that ordinary rather than exceptional &mdash; to put ingredients
     grown nearby into the kitchens and pantries that want them, on terms both sides can hold each
     other to. <strong>Not as a premium category. As what quality ought to mean.</strong></p>
  <p><strong>Fresh ingredients taste different, and if you cook for a living you already know it.</strong>
     A tomato picked three days ago is not the same ingredient as one picked three weeks ago and held
     in the channel &mdash; sugars convert, moisture goes, texture changes, and the aromatics that
     made it worth buying are the first thing to leave. <strong>Nobody who has stood over a pan
     needs that argued.</strong></p>
  <div class="note">
    <p><strong>The problem was never the knowing. It is that knowing does not help you buy.</strong></p>
    <p>You can taste the difference and still have no way to <em>order</em> it, because the channel
       does not sell on it. <strong>It sells a grade, and a grade says nothing about how many days
       ago the thing was cut.</strong> Ask for a variety, a size and a harvest window and you are
       asking a question the wholesale channel has no field for.</p>
  </div>
  <p><strong>So the network is built to carry what a grade cannot.</strong></p>
  <ul style="padding-left:20px;display:flex;flex-direction:column;gap:8px">
    <li><strong>A specification instead of a grade.</strong> A grower can be asked for a variety, a
        size and a harvest window. <strong>A grade is the floor, not the thing you asked for.</strong></li>
    <li><strong>Less time and less handling, as a term rather than a hope.</strong> Condition on
        arrival is written into the contract in the produce trade&rsquo;s own language, with an agreed
        destination to measure it against.</li>
    <li><strong>Provenance you can actually name.</strong> Not a region or a brand. A field, and the
        person who farms it.</li>
  </ul>
  <div class="note">
    <p><strong>Here is how far the current arrangement is from that.</strong> On the day this page
     was last built, <strong>{S["sjv"]} crops in the Los Angeles wholesale report were quoted from
     the San Joaquin Valley</strong> &mdash; grown here, trucked to Los Angeles, and priced there. A
     Fresno kitchen buying those is buying local produce that has made a round trip first.</p>
    <p class="src">Los Angeles Terminal Market reports (HC_FV020, HC_FV010), USDA Agricultural
     Marketing Service. The origin column on <a href="inspect.html">Inspect</a> names them.</p>
  </div>
  <div class="note">
    <p><strong>And the premium is real, measured, and leaving.</strong>
     The crops inside the county&rsquo;s &ldquo;Oriental Vegetables&rdquo; line earned between
     <strong>1.56&times; and 3.12&times;</strong> the value per acre of the average Fresno County
     vegetable acre, in every one of the six years 2019&ndash;2024. Over those same six years that
     acreage fell <strong>36.4%</strong>, while all county vegetable acreage fell
     <strong>15.2%</strong>.</p>
    <p class="src">That figure is about one line of the
     county&rsquo;s report, not about this whole catalogue &mdash; the crops it names and measures
     only in aggregate. It says nothing about the commodity crops this county reports on their own
     lines, and we do not extend it to them. Fresno County Agricultural Crop and Livestock Reports,
     2019&ndash;2024.</p>
  </div>
  <h3 style="margin-top:20px">Why it is not already the standard</h3>
  <p>Not for want of ground. California grows <strong>nearly half the country&rsquo;s vegetables and
     over three-quarters of its fruits and nuts</strong>, and Fresno County alone turned out
     <strong>$9.03 billion</strong> across more than 300 commodities last year. <strong>The scale is
     the achievement and it is also the obstacle:</strong> a market built to move volume prices
     everything as volume, so the land that made it valuable has no quote for three good acres or a
     field corner out of production.</p>
  <p class="src">California Department of Food and Agriculture, California Agricultural Production
     Statistics &middot; Fresno County Agricultural Crop and Livestock Report, 2024. Those figures
     are California and this county, and <strong>the argument does not rest on them.</strong> It
     rests on three things true almost everywhere: <strong>produce degrades between the ground and
     the plate, commodity channels price volume rather than specification, and somebody nearby is
     always holding ground that is earning nothing.</strong> We are starting here because this is
     where we can show our work.</p>
  <p><strong>So this is an invitation, and it is open on both sides.</strong> If you want ingredients
     you can trace, or you hold ground that is earning nothing, the network is what makes the two of
     you contractable to each other. <strong>We never buy the food. We qualify the land, publish what
     is known, and settle the terms before anyone discusses price.</strong></p>
  <div class="cards">
    <div class="card"><h3>If you want the ingredients</h3>
      <p>Restaurants, markets, and anyone filling a pantry on purpose. <strong>Ask for a variety and
         a week rather than a grade</strong>, and have condition on arrival settled in writing before
         price comes up.</p>
      <p><a class="btn" href="buyers.html">Join as a buyer &rarr;</a></p></div>
    <div class="card"><h3>If you have the ground</h3>
      <p>A working farm with a block out of rotation, a few acres, a field corner. <strong>Qualifying
         asks two questions</strong> &mdash; do you have the land, and can you enter into the
         contract. Not a test of how you farm.</p>
      <p><a class="btn" href="qualify.html">Join as a grower &rarr;</a></p></div>
    <div class="card"><h3>Getting it there</h3>
      <p>Several stops, a few pallets each, one fixed day, inside one county. Who pre-cools, who
         pays and who unloads are settled in writing first.</p>
      <p><a class="btn" href="buyers.html#how-it-moves">How a load is shaped &rarr;</a></p></div>
  </div>
  <p style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px">
    <a class="btn" href="catalogue.html">Open the catalogue &rarr;</a>
    <a class="btn ghost" href="inspect.html">See what the market is doing &rarr;</a>
  </p>
  <p class="src" style="color:var(--on-dark-soft)">Growing already? The ground you are farming earns
     more per acre than almost anything else in this county. <a href="growers.html">For Growers &rarr;</a></p>
</div></section>

<section class="band"><div class="wrap stack">
  <p class="eyebrow">The problem</p>
  <h2>Local sourcing does not fail for one reason. It fails three ways, and any one of them stops
      the same order.</h2>
  <div class="cards">
    <div class="card"><h3>Nobody can see what is here</h3>
      <p>Fresno County reports thirty-two Asian specialty crops as a single line, and every Mexican
         specialty crop inside an undifferentiated residual with no acreage and no value at all.</p></div>
    <div class="card"><h3>Neither side knows which rule applies</h3>
      <p>Under the rule as written, a retail food establishment or restaurant is never the party that
         assigns a traceability lot code. And if you buy direct from the farm that grew it, the record
         asked of you is a name and address, kept 180 days.</p></div>
    <div class="card"><h3>No single grower can underwrite a commitment</h3>
      <p>Chinese long bean was grown on 128 acres in this county by 66 separate growers &mdash; just
         under two acres each, in UCCE&rsquo;s 2000 survey of that one crop. A weekly case commitment
         is not something a two-acre grower can make alone.</p></div>
  </div>
  <p class="src">The catalogue, the standard contract and the qualified network are those three fixes,
     in that order.</p>
</div></section>

<section class="band"><div class="wrap stack">
  <p class="eyebrow">What you cannot get anywhere else</p>
  <h2>The season does not taper. It falls off a cliff.</h2>
  <div class="note">
    <p><strong>Thirty-seven of the surveyed crops were available in November. Thirteen were available
       in December</strong> &mdash; a sixty-five percent collapse in one month. If you plan on a
       tapering season you will be short in December, not in February.</p>
    <p class="src">UC Cooperative Extension Fresno County retail survey, 2010. Typical availability,
       not a live feed, and sixteen years old. Counted from the matrix, not read from any
       report&rsquo;s prose.</p>
  </div>
</div></section>

<section class="band"><div class="wrap stack">
  <p class="eyebrow">The catalogue</p>
  <h2>What is actually known about each crop</h2>
  <p>{S["total"]} crops &mdash; {S["commodity"]} commodity, {S["specialty"]} specialty,
     {S["gap"]} unreported &mdash; each with its season, its scale in growers rather than acres,
     and how this county reports it. Where the record is silent, the catalogue
     says so.</p>
  <p><a class="btn" href="catalogue.html">Open the catalogue &rarr;</a></p>
  <h2 style="margin-top:28px">What we are, and what we are not</h2>
  <p>Dues, not a commission. We never buy the food and we are never in the purchase path &mdash; which
     is also what keeps a buyer&rsquo;s own record relief intact. We qualify a grower&rsquo;s capacity
     to contract. We do not inspect food and we do not certify it.</p>
</div></section>"""
    return page("ʻĀina to Table — ingredients you can trace", body,
                current="index.html")

# ── Inspect (C2d) ─────────────────────────────────────────────────────────────
def inspect_page():
    S = stats()
    body = f"""<section class="band wide"><div class="wrap wide stack">
  <p class="eyebrow">Inspect</p>
  <h1>What this market is actually doing</h1>
  <p>Every figure here is public, sourced and dated. Nothing on this page is ours except the
     arithmetic, and where the arithmetic is ours we say so.</p>
  <div class="cards">
    <div class="card"><h3>The specialty crops are worth more per acre</h3>
      <p>Between <strong>1.56&times; and 3.12&times;</strong> the value per acre of the average Fresno
         County vegetable acre, in every one of the six years 2019&ndash;2024. The weakest of the six
         was still 1.56&times;.</p>
      <p class="src">The county&rsquo;s &ldquo;Oriental Vegetables&rdquo; line.</p></div>
    <div class="card"><h3>And that acreage is going away</h3>
      <p>Over the same six years it fell <strong>36.4%</strong>, while all county vegetable acreage fell
         <strong>15.2%</strong>. Nearly two and a half times faster than the sector around it.</p>
      <p class="src">The same line.</p></div>
    <div class="card"><h3>The buying universe is small</h3>
      <p><strong>287</strong> food-retail establishments and <strong>508</strong> full-service
         restaurants, with <strong>48</strong> produce wholesalers between them and the farms. Thirteen
         of the 287 are fruit-and-vegetable markets, employing twenty-five people in total.</p></div>
  </div>
  <p class="src">Fresno County Agricultural Crop and Livestock Reports, 2019&ndash;2024, each year
     cross-checked against the next year&rsquo;s comparative table; the 2019 row is single-sourced.
     Establishment counts: US Bureau of Labor Statistics, QCEW, Fresno County, 2024.</p>
  <p class="src"><strong>Both of the first two figures are about one line of the county&rsquo;s
     report, not about this whole catalogue.</strong> They are computed from
     &ldquo;Oriental Vegetables&rdquo; &mdash; the {S["footnote"]} crops the county names only inside
     an aggregate. They say nothing about the {S["commodity"]} commodity crops in this catalogue,
     which the county reports on their own lines, and we do not extend them to those crops.</p>

  <h2 style="margin-top:28px">Thirty-eight crops in October. Eight in January.</h2>
  <p>Of the 45 crops surveyed in Fresno specialty markets, 38 were available in October and 8 in
     January. Only daikon and lemongrass ran all twelve months. And the fall is abrupt: 37 crops in
     November, 13 in December. Sixty-five percent in one month.</p>
  <p class="src">UC Cooperative Extension Fresno County, specialty Asian retail market survey, 2010.
     Typical availability, not a live feed, and sixteen years old. The survey marked two kinds of
     availability and defined neither; no season data exists for any Mexican specialty crop, because
     the 2010 survey covered Hmong and Southeast Asian retail only.</p>

  <h2 style="margin-top:28px">The county does not break out a single herb</h2>
  <p>Thirty-two Asian specialty crops appear in the county&rsquo;s reports as one line.
     {S["absent_all"]} of the crops Fresno markets buy are named in no line and no footnote of any
     report from 2020 to 2024. {S["footnote"] - 32} more sit inside an
     undifferentiated &ldquo;other&rdquo; line with no acreage and no value of their own.</p>
  <div class="spec"><p class="lbl">The clearest case</p>
    <p><strong>Gobo.</strong> Eight acres county-wide in 2000, a published growing guide in 2001, and in
       2010 carried by Fresno specialty markets on special order only. Demand recorded, supply trivial,
       agronomy already published &mdash; each with a date and an author on it.</p></div>
  <p class="src">Two retail categories are too small for the federal government to publish without
     identifying the businesses in them. We recovered roughly thirty-five establishments by subtraction.
     A segment too small to be measured is a segment too small for anyone else to bother serving.</p>

  {price_section()}
  {market_section()}

  <div class="note">
    <p><strong>One next step from here, depending on which side of the table you are on:</strong>
       <a href="buyers.html">For Buyers</a> if you are sourcing,
       <a href="growers.html">For Growers</a> if you farm.</p>
  </div>

  <h2 style="margin-top:28px">What we cannot tell you, and why</h2>
  <div class="note">
    <p><strong>No dollar market size.</strong> The federal data that counts these establishments carries
       no sales figures, and the only published sales ratios for this sector are from 1997 and 2002. We
       would rather refuse the number than estimate it and have you plan against it.</p>
    <p><strong>No prices of our own, and no yields or returns.</strong> The wholesale figures above
       are USDA&rsquo;s, republished. What we do not have is what a crop costs to grow here or returns
       here: the only published economics for that are UC cost studies from 2005, and they have not
       been re-verified or adjusted.</p>
    <p><strong>No agronomic promises.</strong> We do not know whether the crops this county does not
       measure can be grown here. For the {word(len(CHECKED_NO_TRIAL)).lower()} crops we checked &mdash;
       {esc(", ".join(c.split(" /")[0].lower() for c in CHECKED_NO_TRIAL))} &mdash; we found no
       extension trial data in this valley at all, so anyone who tells you otherwise is guessing.</p>
    <p class="src">{checked_class_note()}</p>
    <p><strong>No causal story.</strong> We do not know whether the acreage decline is a supply story or
       a demand story. A premium argues against demand collapse. It does not prove a supply
       constraint.</p>
    <p><strong>And the two sources this page leans on hardest are old</strong> &mdash; the grower survey
       is from 2000, the availability survey from 2010. They describe the shape of this production, not
       its current size.</p>
  </div>
</div></section>"""
    return page("Inspect — ʻĀina to Table", body, current="inspect.html",
                desc="What this market is actually doing, with every figure sourced, dated, and its gaps stated.")

# ── Market (price per acre) ───────────────────────────────────────────────────
PRICE_CHART = os.path.join(DATA, "price_per_acre_chart.csv")

def price_chart_rows():
    try:
        with io.open(PRICE_CHART, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def money(v):
    return f"${float(v):,.0f}"

def market_page():
    rs = price_chart_rows()
    if not rs:
        body = """<section class="band"><div class="wrap stack"><h1>Market</h1>
  <p>Not built yet.</p></div></section>"""
        return page("Market — ʻĀina to Table", body, current="market.html")

    def term_cell(r):
        lo_t, hi_t = r.get("terminal_low") or "", r.get("terminal_high") or ""
        if r.get("terminal_date") and (lo_t or hi_t):
            price = (f"{money(lo_t)}&ndash;{money(hi_t)}" if lo_t and hi_t and lo_t != hi_t
                     else money(hi_t or lo_t))
            return (f'{price}, {esc(r["terminal_pack"])} &middot; '
                    f'{esc(r["terminal_market"])} terminal, California origin, '
                    f'{esc(r["terminal_date"])}')
        return '<span class="src">no California terminal quote found</span>'

    def openly_row(r):
        lo, hi, latest = float(r["range_low"]), float(r["range_high"]), float(r["latest_value_per_acre"])
        return f"""<tr><td><span class="crop">{esc(r["crop"])}</span></td>
  <td><span class="data">{money(lo)}&ndash;{money(hi)}, latest {money(latest)}
      ({esc(r["latest_data_year"])})</span></td>
  <td>{term_cell(r)}</td></tr>"""

    def few_row(r):
        return f"""<tr><td><span class="crop">{esc(r["crop"])}</span></td>
  <td><span class="src">no county figure of its own &mdash;
      {esc(r["aggregate_context"])}</span></td>
  <td>{term_cell(r)}</td></tr>"""

    openly = sorted((r for r in rs if r["status"] == "Traded openly"),
                    key=lambda r: -float(r["latest_value_per_acre"]))
    few = sorted((r for r in rs if r["status"] == "Few suppliers"),
                 key=lambda r: r["crop"])
    few_priced = [r for r in few if r.get("terminal_date")]
    few_unpriced = [r for r in few if not r.get("terminal_date")]

    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow">Market</p>
  <h1>What an acre has commanded, and what the market still does not say</h1>
  <p>{word(len(openly))} crops the county prices on their own line. {word(len(few))} more
     it names &mdash; in the Vegetable Crops or Fruit &amp; Nut Crops footnote &mdash;
     but has never given an acreage or value of their own. <strong>Every one of them
     gets a row here.</strong> A crop the county folds into a blended total is still
     a crop; the fold is the county's limitation, not a reason to leave it off this
     page.</p>
  <p class="src"><strong>Gross returns to the producers, and do not reflect actual
     net profit</strong> &mdash; the county's own words, Fresno County Agricultural
     Crop and Livestock Reports, 2019&ndash;2024. A single year moves a great deal,
     so every priced row shows the full range next to the latest year, never a
     single number alone.</p>
</div></section>

<section class="band wide"><div class="wrap wide stack">
  <h2>Traded openly &mdash; the county prices these on their own line</h2>
  <table class="data">
    <thead><tr><th>Crop</th><th>County value per acre (range, latest)</th>
      <th>Terminal reference, separately</th></tr></thead>
    <tbody>{"".join(openly_row(r) for r in openly)}</tbody>
  </table>
  <p class="src">⛔ The two columns are never the same number and are never combined.
     The county figure is <strong>farm gate</strong> &mdash; what this acre returned
     here. The terminal figure is <strong>delivered wholesale</strong>, hundreds of
     miles away, after freight, cooling and a jobber's margin. Multiplying county
     yield by a terminal price overstates what a Fresno acre earns by that whole
     gap, which is why they stay in separate columns rather than one.</p>
</div></section>

<section class="band wide"><div class="wrap wide stack">
  <h2>Few suppliers &mdash; named by the county, never priced on its own line</h2>
  <p>{word(len(few_priced))} of these have no county figure at all but DO have a real,
     dated terminal market price &mdash; the clearest evidence on this page that
     <strong>unreported is not unproduced.</strong> {word(len(few_unpriced))} have
     neither, yet, anywhere this venture has looked.</p>
  <table class="data">
    <thead><tr><th>Crop</th><th>County figure</th>
      <th>Terminal reference, separately</th></tr></thead>
    <tbody>{"".join(few_row(r) for r in few_priced + few_unpriced)}</tbody>
  </table>
  <p class="src">Each blended total is a real, reconciled county figure &mdash; it
     says what the WHOLE category earned, not what any one crop inside it is worth.
     Reading it as one crop's price would be fabricating a precision the county
     never published. That is why every row above states the blend as context,
     never as that crop's own number, and why a county cell with nothing in it is
     left that way rather than filled in from the blend.</p>
  <p class="src"><a href="catalogue.html">The catalogue</a> carries what else is
     known about each of these crops &mdash; season, origin, cuisine &mdash; beyond
     what fits on this page.</p>
</div></section>"""
    return page("Market — ʻĀina to Table", body, current="market.html",
                desc="What an acre has commanded by crop, and what the market still does not say — every crop the county prices individually or only in aggregate, never confused with a terminal-market price.")

# ── For Buyers (C2b). Gate C condition 1 lives here. ──────────────────────────
def buyers_page():
    S = stats()
    # ONE block. relief.tlc and relief.boundary are emitted together, and the
    # assertion below verifies the boundary immediately follows the statement.
    relief = f"""  <h3 style="margin-top:12px">Most of the paperwork you are worried about is not yours.</h3>
  <p>{RELIEF_TLC} <span class="src">21 CFR &sect;1.1345(b)(1)</span></p>
  <p>If you buy a listed food directly from the farm that grew it, the record the rule asks of you is
     the farm&rsquo;s name and address, kept for 180 days. Not a lot code, not a key data element, not
     a system. <span class="src">21 CFR &sect;1.1305(j)</span></p>
  <p>If you also take cut flowers, the rule does not reach them at all: <em>flower</em>,
     <em>ornamental</em> and <em>nursery</em> appear nowhere in its 178 pages.</p>
  <div class="note">
    <p><strong>{RELIEF_BOUNDARY}</strong></p>
    <p>The compliance date in the Code of Federal Regulations is still 20 January 2026. A proposed rule
       would extend it and an appropriations restriction limits enforcement. Neither has changed the
       date in the CFR, and we will not say otherwise.</p>
  </div>"""
    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow">For Buyers</p>
  <h1>Order a variety and a week, not a grade.</h1>
  <p>A grade is the floor. It says nothing about which variety, or how many days ago the thing was
     cut &mdash; and those are the two facts that decide what arrives in your kitchen. <strong>This
     network exists so you can ask for them and have the answer written down.</strong></p>
  <p>We publish which crops this county reports growing, which ones it reports only inside an
     aggregate, and which ones it does not report at all &mdash; with the sources, before you tell us
     anything about your business.</p>
  <p class="src">Fresno County&rsquo;s food-retail universe is 287 establishments &mdash; of which
     thirteen are fruit-and-vegetable markets, employing twenty-five people between them &mdash;
     alongside 508 full-service restaurants and 48 fresh-produce wholesalers. Two retail categories are
     too small for the federal government to publish without identifying the businesses in them; we
     recovered roughly thirty-five establishments by subtraction. A segment too small to be measured is
     a segment too small for anyone else to bother serving.
     <br>US Bureau of Labor Statistics, QCEW, Fresno County, 2024.</p>

{relief}

  <h3 style="margin-top:12px">One number decides most of this for you.</h3>
  <p>Your three-year average annual food sales. Below one threshold, the rule&rsquo;s small-retailer
     accommodation can apply; above another, a request from FDA has to be answerable as an electronic
     sortable spreadsheet within 24 hours. <span class="src">21 CFR &sect;1.1455(c)(3)(iii)(C)</span></p>
  <p class="src">Those figures are inflation-adjusted annually and FDA has not published the current
     ones for these two provisions. We computed them by FDA&rsquo;s own published method and validated
     the method against the two figures FDA <em>has</em> published, reproducing them to within 0.033%.
     They are our computation, not FDA&rsquo;s publication, and we label them that way everywhere.</p>

  <h3 style="margin-top:12px">Here is what grows here.</h3>
  <p>{S["total"]} crops, with each one&rsquo;s season, its scale in growers rather
     than acres, and how Fresno County reports it. {S["gap"]} of them the county does not
     report in any form &mdash; which is the first thing worth knowing about them.</p>
  <p><a class="btn" href="catalogue.html">Open the catalogue &rarr;</a></p>

  <h3 style="margin-top:12px">Seasonality is the real constraint, and we are not going to pretend
      otherwise.</h3>
  <p>Of the 45 crops surveyed in Fresno specialty markets, 38 were available in October and 8 in
     January. Only two &mdash; daikon and lemongrass &mdash; ran all twelve months. And the fall is not
     gradual: availability holds through November at 37 crops, then drops to 13 in December &mdash; a
     65% collapse in a single month. If you plan on a tapering season you will be short in December,
     not in February.</p>
  <p class="src">UC Cooperative Extension Fresno County, specialty Asian retail market survey, 2010.
     Typical availability, not a live feed, and sixteen years old. No season data exists for any Mexican
     specialty crop &mdash; the 2010 survey covered Hmong and Southeast Asian retail only, so cactus
     leaf, tomatillo, epazote, chipil&iacute;n, pepicha and purslane have no published season anywhere.
     We would rather tell you that than guess.</p>

  <h3 style="margin-top:12px">How to plan against a season like this</h3>
  <ul style="padding-left:20px;display:flex;flex-direction:column;gap:8px">
    <li>Build your specification before your calendar. What a crop has to be &mdash; variety, size,
        grade, pack &mdash; is contingent on the product itself and on the intended use at your
        facility. Settle that once and it survives every season.</li>
    <li>Treat November as the end of the season, not December.</li>
    <li>For the eight crops that carry January, name your substitution in the contract rather than at
        the loading dock.</li>
    <li>Ask how many growers are behind a crop, not how many acres. A crop grown on 86 acres by 58
        growers is a different supply risk from one grown on 86 acres by three.</li>
    <li>For anything the county does not report, expect to contract it rather than buy it on the spot
        market.</li>
  </ul>
  <p class="src">None of this is a recommendation about what to buy or what to pay. It is how the
     published record behaves.</p>

  <h3 style="margin-top:12px">We settle the terms before anyone talks about price.</h3>
  <p>One standard contract, the same for every member, covering five things and deliberately not a
     sixth: the delivery term, named against Incoterms&reg; 2020 &mdash; who contracts carriage, which
     is not the same as who arranges it &mdash; where risk of loss passes, who keeps which record and
     for how long, and the specification with what happens when a delivery misses it.</p>
  <p><strong>Not price.</strong> We standardise how a transaction works, never what it costs. What you
     pay is between you and the grower, every time.</p>
  <div class="cards">
    <div class="card"><h3>If you resell it</h3>
      <p>Your problem is shelf continuity: the crops your customers ask for that you cannot reliably
         get. Thirteen fruit-and-vegetable markets exist in this county, so &ldquo;the market&rdquo; for
         these crops is a room, not a sector.</p></div>
    <div class="card"><h3>If you cook it</h3>
      <p>Your problem is a menu written against availability. 508 full-service restaurants operate here,
         and a dish that needs a crop with an eight-month window is a dish with a four-month hole in
         it.</p></div>
  </div>
  <p class="src">The regulatory position is identical for both &mdash; &sect;1.1305(j) and
     &sect;1.1345(b)(1) treat a retail food establishment and a restaurant alike.</p>

  <h3 style="margin-top:12px">What membership is</h3>
  <p>Dues, not a commission. We take no percentage of what you buy and we never appear in the purchase
     path. That is not modesty, it is the point: if a broker or a parent company buys the food, the
     direct-from-farm record relief stops applying to you &mdash; FDA has said so expressly,
     <em>&ldquo;even if no third party ever takes physical possession of the food.&rdquo;</em> We never
     buy the food, so your position does not change by working with us.</p>
  <p>We qualify a grower&rsquo;s capacity to take on a commercial contract &mdash; their scale, their
     terms, their records. We do not inspect food and we do not certify it. Nothing we do is a
     food-safety judgment.</p>
  <p class="src">Dues and terms are published once the network&rsquo;s structure is settled.</p>

  <h3 style="margin-top:12px">What the contract settles, in the terms this trade already uses</h3>
  <p>The produce trade has its own delivery terms, written into federal regulation, so that is the
     language the contract uses rather than general commercial wording.
     <strong>F.o.b.</strong> means the crop is placed free on board at the shipping point
     <strong>in suitable shipping condition</strong>, and the buyer carries the risk of damage and
     delay in transit not caused by the seller &mdash; <em>irrespective of how the shipment is
     billed.</em> <span class="src">7 CFR &sect;46.43(i).</span></p>
  <p><strong>Suitable shipping condition</strong> is the clause that matters most and the one most
     often left out: the crop, at the time of billing, is in a condition which &mdash; handled under
     normal transportation service &mdash; will assure delivery without abnormal deterioration at the
     contract destination the two parties agreed.
     <span class="src">7 CFR &sect;46.43(j); good-delivery tolerances at &sect;46.44.</span></p>
  <div class="note">
    <p><strong>Two consequences worth knowing before agreeing anything.</strong></p>
    <p>Paying the freight and carrying the risk are different questions. The regulation settles
       transit risk <em>irrespective of how the shipment is billed</em>, so an agreement about who
       books the truck has not settled who bears a loss.</p>
    <p>And <strong>there has to be an agreed contract destination</strong> for suitable shipping
       condition to measure anything at all. Leave it out and the clause has nothing to work against.</p>
  </div>

  {how_it_moves()}

  {contact_block("Crop enquiry", "Name a crop and a week, and we will tell you what is behind it.")}
  <p class="src">What helps: the crop, the pack you need, how much and how often, and the week you
     would want to start. <strong>If the answer is that nobody here is growing it at that volume yet,
     that is the answer you will get.</strong> We have nothing to sell yet &mdash; dues and terms are
     published once the network&rsquo;s structure is settled &mdash; so the useful conversation now is
     about what this county actually grows, and whether anything on these pages is wrong.</p>
</div></section>"""
    return page("For Buyers — ʻĀina to Table", body, current="buyers.html",
                desc="For kitchens and markets that want a specification rather than a grade: what local supply, the records and the terms actually look like.")

# ── For Growers (C2e) ─────────────────────────────────────────────────────────
def growers_page():
    S = stats()
    body = f"""<section class="band"><div class="wrap stack">
  <p class="eyebrow">For Growers</p>
  <h1>Ground that is earning nothing is still ground.</h1>
  <p class="src">And the crops this county measures only in aggregate &mdash; the specialty line, not
     its commodity rows &mdash; have earned a premium per acre in every one of the last six years,
     while that same acreage has been going out of production faster than the sector around it. Both
     figures, and what they do and do not cover, are below.</p>
  <p>That is not encouragement. It is what six years of the county&rsquo;s own crop reports say, and the
     second half of it is the part nobody mentions.</p>
  <p>Asian specialty vegetables returned between 1.56 and 3.12 times the value per acre of the average
     Fresno County vegetable acre, in every one of the six years from 2019 to 2024. The worst year of
     the six was still 1.56 times. Over the same six years the acreage fell 36.4%, while all county
     vegetable acreage fell 15.2% &mdash; it is going out of production nearly two and a half times
     faster than the sector around it.</p>
  <p class="src">Fresno County Agricultural Crop and Livestock Reports, 2019&ndash;2024. Each year
     cross-checked against the following year&rsquo;s comparative table; the 2019 figure is
     single-sourced. We do not know why it is leaving production, and we are not going to guess. A
     premium argues against demand collapse. It does not prove a supply constraint.</p>
  <p class="src"><strong>This figure is about one line of the county&rsquo;s report, not about this
     whole catalogue.</strong> It is the &ldquo;Oriental Vegetables&rdquo; line &mdash; the crops the
     county names in that footnote and measures only in aggregate. It says nothing about the
     catalogue&rsquo;s commodity crops, which the county reports on their own lines, and we do not
     extend it to them.</p>

  <h3 style="margin-top:12px">The traceability rule may not reach you at all, and the threshold is not
      the number you have been told.</h3>
  <p>If a farm&rsquo;s average annual produce sales fall below the rule&rsquo;s adjusted threshold, the
     traceability requirements do not apply to that food. The text says $25,000; the figure is
     inflation-adjusted annually and the current adjustment puts it near <strong>$29,800</strong>.
     <span class="src">21 CFR &sect;1.1305(a), base year 2020. FDA has not published that adjusted
     figure. We computed it by FDA&rsquo;s own published method and validated the method against two
     figures FDA <em>has</em> published, reproducing them to within 0.033%.</span></p>
  <div class="note">
    <p><strong>And here is the part that catches people.</strong> Two different rules both say
       &ldquo;$25,000&rdquo; in their text, and they adjust from different base years &mdash; one from
       2020, one from 2011. The traceability figure lands near <strong>$29,800</strong>. The Produce
       Safety figure, which FDA does publish, is <strong>$34,324</strong>. A farm at $32,000 is under
       one and over the other.</p>
    <p class="src">21 CFR &sect;1.1305(a), base year 2020, computed &middot; 21 CFR &sect;112.4(a),
       base year 2011, FDA-published.</p>
    <p>Which of those applies to you depends on what you grow, what you sell it as, and what your
       three-year average is. That is your arithmetic, not ours &mdash; but now you know which two
       numbers to do it against.</p>
  </div>

  <h3 style="margin-top:12px">Two acres cannot serve a commercial contract. The county&rsquo;s own
      survey counted sixty-six growers on a single crop.</h3>
  <p>Chinese long bean was grown on 128 acres in this county by 66 separate growers &mdash; just under
     two acres each. Ten of the crops in our catalogue were farmed at under two acres per grower.</p>
  <p class="src">Ten of twenty-six, not ten of {S["total"]}: only twenty-six crops in the catalogue
     carry both an acreage and a grower count from the 2000 survey, which is twenty-six years old. Read
     it as the shape of this production, not its current size.</p>
  <p>A buyer asking for weekly case volume is asking for something no two-acre grower can promise alone
     and no single grower should have to. The network is how that commitment gets underwritten &mdash;
     not by us buying it, but by enough qualified growers standing behind one specification.</p>

  <h3 style="margin-top:12px">Where the record has holes</h3>
  <p>{S["absent_all"]} crops that Fresno markets buy are named by this county in no line and no
     footnote of any report from 2020 to 2024.
     {S["footnote"]} more are named only in a footnote to an aggregate line, with no acreage and no value
     of their own. That is the gap, and it is the county&rsquo;s own reporting that shows it.</p>
  <div class="note">
    <p><strong>We will show you every hole in the record and the source for each one. We will not tell
       you to plant anything.</strong> For the gap crops we have checked we found no extension trial in
       this valley, and a recommendation without one is somebody else&rsquo;s money at risk.</p>
    <p class="src">Agronomic viability not established for this region &mdash; see extension trial
       data.</p>
  </div>
  <p><a class="btn" href="catalogue.html">Open the catalogue &rarr;</a></p>

  <h3 style="margin-top:12px">You have signed contracts before, so here is the part that is
      different</h3>
  <p>Roughly half the production value of fruit, nut and berry farms in this country is already under
     contract, and on the farms that use them it is almost all of it. None of this is new to you.
     <span class="src">USDA Economic Research Service.</span></p>
  <p><strong>What differs is which kind of contract this is.</strong> It is not a production contract
     &mdash; nobody owns your crop while it is in the ground, nobody supplies your inputs, and
     nothing ties you to one buyer through equipment only they can use. It is a marketing contract
     <em>between you and the buyer</em>, on published terms neither of us can quietly change.
     <strong>We are not a party to it and we never buy your crop.</strong></p>
  <p class="src">Worth saying plainly, because &ldquo;contract&rdquo; usually means the other kind,
     and the other kind is the one worth being careful about.</p>

  <h3 style="margin-top:12px">And the part that actually matters: getting paid</h3>
  <p>The contract states when payment is due and what condition on arrival means, in the produce
     trade&rsquo;s own terms. <strong>Suitable shipping condition</strong> is the test &mdash; that
     the crop, at the time of billing, will arrive at the agreed destination without abnormal
     deterioration if it is handled normally in transit.
     <span class="src">7 CFR &sect;46.43(j); tolerances at &sect;46.44. The clause needs an agreed
     destination to measure anything, so the contract names one.</span></p>
  <p class="src">That clause is what disputes in this trade turn on, and it is the one most often
     missing from a contract drafted by someone outside the trade.</p>

  {how_it_moves()}

  {contact_block("Registering interest", "Two things to send, and we will tell you where that leaves you.")}
  <p class="src">The parcel number or nearest cross-streets, and roughly how much ground is sitting
     idle. <strong>That is enough</strong> &mdash; <a href="qualify.html">qualification</a> is two
     questions, not an examination of how you farm, and the crop pages are free to read whether you
     ever write or not.</p>

  <h3 style="margin-top:12px">What is already published about growing these crops</h3>
  <p>UC Cooperative Extension published a guide to Asian specialty vegetables in the Central Valley in
     2001, and seven cost-and-return studies in 2005. Those seven cover twelve of these crops &mdash;
     one study covers moqua and opo together, one covers all three eggplants, and bitter melon and
     sinqua each appear here as two entries. Both sources are public, both are on the crop pages, and
     neither is ours.</p>
  <p class="src">The 2001 guide identifies crops and describes general culture. It is not an agronomic
     manual &mdash; it says almost nothing about soil or climate per crop, and we will not pad it out
     with figures it does not contain. The 2005 cost studies carry per-acre costs and returns; they are
     twenty-one years old and we do not publish their figures until they have been re-verified and
     adjusted. We would rather tell you the study exists than quote a number from it.</p>

  <h3 style="margin-top:12px">What qualification means, and what it does not</h3>
  <p>We qualify your capacity to take on a commercial contract: your scale, the terms you can meet, the
     records you already keep. It is a statement that you can transact, within stated bounds.
     Qualifying, not exclusionary &mdash; the criteria are published, they are the same for everyone,
     and a decision can be appealed.</p>
  <p><strong>It is not a food-safety judgment.</strong> We do not inspect your food, we do not certify
     it, and nothing we issue says anything about it. Any buyer who reads our qualification as a food
     certification has read it wrong, and we would rather say so here than correct it later.</p>
  <p class="src">Dues, not a commission. We never buy your crop and we are never in the purchase path
     &mdash; which is also what keeps your buyer&rsquo;s own record relief intact. The contract settles
     delivery, risk, records, specification and remedies. It never settles price. What you sell for is
     between you and your buyer, every time. Dues and terms are published once the network&rsquo;s
     structure is settled.</p>
  <h3 style="margin-top:12px">Getting in touch</h3>
  <p>hello@ainatotable.com &mdash; one address, and it reaches a person rather than a form.</p>
  <p class="src">We have nothing to sell yet: dues and terms are published once the network&rsquo;s structure is settled. Until then the useful conversation is about what this county actually grows, and whether anything on these pages is wrong.</p>
</div></section>"""
    return page("For Growers — ʻĀina to Table", body, current="growers.html",
                desc="For anyone holding ground that is earning nothing: the thresholds, the gaps, and the two questions qualifying actually asks.")

# ── About (C2f) ───────────────────────────────────────────────────────────────
def about_page():
    body = """<section class="band"><div class="wrap stack">
  <p class="eyebrow">About</p>
  <h1>What ʻĀina to Table is</h1>
  <p><strong>A network built so that an ingredient you can trace to the ground it came out of is the
     ordinary thing to buy rather than the exceptional one.</strong> ʻĀina to Table operates in the
     Fresno region, is separate from any one grower, and is named separately from any farm.</p>
  <p>Concretely: <strong>it qualifies land</strong> &mdash; that the ground is real and committable
     and that there is a party who can contract &mdash; <strong>publishes what is known about each
     crop, and settles the terms of the transaction in the produce trade&rsquo;s own language.</strong>
     <strong>It never buys the food.</strong></p>
  <p>Dues, not a commission. The catalogue, the market conditions, the soil-health material and the
     compliance reading are free and complete on their own, whether or not anyone ever becomes a
     member.</p>

  <h3 style="margin-top:12px">Two ideas this is built on</h3>
  <div class="cards">
    <div class="card">
      <p style="color:var(--ink);font-size:1.0625rem"><strong>Labor should share in the profit of the
         food it grows &mdash; not just be paid a wage to produce something someone else profits
         from.</strong></p>
      <p>That is also the legal structure. Growers acting together on terms need a form that permits it,
         and an association of agricultural producers is the one this network is being built in.</p>
    </div>
    <div class="card">
      <p style="color:var(--ink);font-size:1.0625rem"><strong>Buyers deserve a real relationship with
         where their ingredients come from &mdash; not an anonymous line in a distributor&rsquo;s
         truck.</strong></p>
      <p>There are 48 fresh-produce wholesalers standing between this county&rsquo;s buyers and its
         farms. That sentence was written before anyone counted them.</p>
    </div>
  </div>

  <h3 style="margin-top:12px">The design</h3>
  <p>No single grower carries a contract alone. That is the whole design: enough qualified growers
     standing behind one specification that a buyer can be promised weekly volume nobody could promise
     individually.</p>

  <h3 style="margin-top:12px">What we are not</h3>
  <p>We do not inspect food and we do not certify it. We do not grow anything in Fresno County.
     <strong>We never buy it, sell it, take possession of it, negotiate its price, or appear in the
     purchase path.</strong></p>
  <p class="src">Stated as conduct rather than as a category, deliberately. What we do is describable
     without claiming a label, and a label would be a claim about regulatory status that is not ours
     to make.</p>

  <h3 style="margin-top:12px">What the dues are, and what they are not</h3>
  <p>Dues, not a commission. Nothing we are paid moves with the price or the volume of what changes
     hands &mdash; which is the whole reason we can publish a wholesale figure that argues against
     us.</p>
  <div class="note">
    <p><strong>What a member owns.</strong> The qualification record is the member&rsquo;s, not ours.
       It describes their operation, so it belongs to them and it travels &mdash; to any buyer,
       including one who has never heard of us.</p>
    <p><strong>What a member controls.</strong> Who they contract with, at what price, on what
       volume. We are not a party to the contract and we do not negotiate it.</p>
    <p><strong>How the benefit tracks use.</strong> The more ground a member commits and the more
       buyers read their record, the more the membership is worth to them. It does not accrue to us
       at their expense, because our side of it does not move with their volume.</p>
  </div>
  <p class="src">Three of the things on this site are free and will stay free: the catalogue, the
     market conditions, and the reading of the federal thresholds. <strong>They are not the offer
     &mdash; they are what we can show before anyone owes us anything.</strong> What membership adds
     is the qualification record, the published contract, somewhere to go when a load arrives out of
     condition, and the growers who have been through the same audit.</p>
</div></section>"""
    return page("About — ʻĀina to Table", body,
                desc="ʻĀina to Table is a network for ingredients you can trace to the ground they came out of. It qualifies land, publishes what is known, and never buys the food.")

# ⭐ Prices now come from the catalogue itself, not from a separate 16-crop
# mart. The LA pass used to DROP a reported block that matched a crop already
# in the catalogue — it existed to find new crops — so 74 rows had no price
# while the report on disk quoted many of them. One source of truth, and the
# attribution is recorded per row.
ZIP3 = os.path.join(DATA, "usda_terminal_market_by_zip3.csv")
REGISTRY = os.path.join(DATA, "usda_terminal_market_registry.csv")

def market_rows():
    try:
        with io.open(REGISTRY, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def zip3_payload():
    """ZIP3 → [market code, min miles, max miles, band initial].

    ⚠️ Resolved at THREE-DIGIT granularity, and 27% of prefixes span more than
    one market or more than one distance band. That is why the output is a
    RANGE and says which prefix it answered, rather than pretending to know
    the reader's exact ZIP.

    🔴 Only LIVE markets are candidates. San Francisco serves HTTP 200 for a
    report dated 01 May 2025 — it is the nearest market to much of northern
    California and offering it would be worse than offering nothing.
    """
    try:
        with io.open(ZIP3, encoding="utf-8") as f:
            rs = list(csv.DictReader(f))
    except FileNotFoundError:
        return "{}", 0
    import json
    pay = {r["zip3"]: [r["code"], int(r["mi_lo"]), int(r["mi_hi"]), r["band"][0]]
           for r in rs}
    return json.dumps(pay, separators=(",", ":")), len(rs)

def market_section():
    """⭐ Which terminal market is the reader's alternative, and whether that
    question has an honest answer where they are."""
    mk = market_rows()
    pay, n3 = zip3_payload()
    if not mk or n3 == 0:
        return ""
    live = [m for m in mk if m["status"] == "live"]
    frozen = [m for m in mk if m["status"] != "live"]
    trs = "".join(
        f'<tr><td><span class="crop">{esc(m["city"])}, {esc(m["state"])}</span>'
        f'<span class="aka">{esc(m["code"].upper())}_FV020 &middot; '
        f'{esc(m["code"].upper())}_FV010</span></td>'
        f'<td>{"Reporting" if m["status"] == "live" else "<strong>Stopped</strong>"}</td>'
        f'<td>{esc(m["report_date"])}</td></tr>'
        for m in mk)
    return f"""
  <h2 style="margin-top:28px" id="your-market">Which market is your alternative?</h2>
  <p>The figures above are Los Angeles, because that is where this network is being built. The same
     reports exist for nine other cities. <strong>Put in a postcode and this will tell you which one
     is nearest you &mdash; and whether it is close enough to mean anything.</strong></p>
  <div class="tools">
    <label for="zq">Postcode</label>
    <input id="zq" inputmode="numeric" maxlength="5" placeholder="e.g. 93701"
           style="font:inherit;padding:6px 10px;border:1px solid var(--line);
                  border-radius:var(--radius);width:9ch">
    <span class="src" id="zout">{n3} postcode areas resolved.</span>
  </div>
  <div class="note" id="zans" hidden></div>
  <p class="src"><strong>What this does and does not do.</strong> It names the market whose published
     report is closest to you, and how far away it is. <strong>It does not price this catalogue
     against that market</strong> &mdash; the crop-by-crop matching above is Los Angeles only. And it
     answers at three-digit postcode granularity, where about a quarter of areas span more than one
     market, which is why you get a range rather than a single number.</p>

  <h3 style="margin-top:12px">The eleven markets, and the one that stopped</h3>
  <div class="tbl"><table>
    <thead><tr><th>Market</th><th>Status</th><th>Latest report seen</th></tr></thead>
    <tbody>{trs}</tbody>
  </table></div>
  <div class="note">
    <p><strong>{esc(frozen[0]["city"]) if frozen else "One market"} is the reason this table
       exists.</strong> Its reports still download, still parse, and still look exactly like the
       others. <strong>The date inside them is {esc(frozen[0]["report_date"]) if frozen else "old"}.</strong></p>
    <p class="src">A service that checked whether the file loaded would have republished prices more
       than a year stale as though they were today&rsquo;s. We read the date in the report instead,
       and we leave that market out of every answer above rather than quoting it.
       {len(live)} of {len(mk)} are reporting.</p>
  </div>
<script>
(function(){{
  var P={pay};
  var BANDS={{
    d:["A buyer here can realistically source from this market, so its published price is a real alternative to buying locally.","direct"],
    f:["Reachable, but freight and a day in transit sit between you and that price. Treat it as the alternative plus the cost of getting it to you.","freight"],
    r:["Too far to be your alternative. Read it as a national reference point, not as your option.","reference"],
    n:["<strong>No live terminal market is near enough to describe your alternative, and we are not going to pretend otherwise.</strong> The nearest reporting one is listed, with the distance, so you can see why.","none"]
  }};
  var q=document.getElementById('zq'), out=document.getElementById('zans'),
      lab=document.getElementById('zout'), CITY={{}};
  [].slice.call(document.querySelectorAll('#your-market ~ .tbl tbody tr')).forEach(function(tr){{
    var c=tr.cells[0].querySelector('.aka').textContent.split('_')[0];
    CITY[c]=tr.cells[0].querySelector('.crop').textContent;
  }});
  function go(){{
    var v=(q.value||'').replace(/[^0-9]/g,'');
    if(v.length<3){{ out.hidden=true; lab.textContent='Enter at least three digits.'; return; }}
    var r=P[v.slice(0,3)];
    if(!r){{ out.hidden=true; lab.textContent='No postcode area '+v.slice(0,3)+' in the record.'; return; }}
    var b=BANDS[r[3]]||BANDS.n, city=CITY[r[0]]||r[0],
        rng=(r[1]===r[2])?(r[1]+' miles'):(r[1]+'\u2013'+r[2]+' miles');
    lab.textContent='Postcode area '+v.slice(0,3)+'.';
    out.innerHTML='<p><strong>Nearest reporting market: '+city+'</strong> &mdash; '+rng+' away.</p>'
      +'<p>'+b[0]+'</p>'
      +'<p class="src">Reports '+r[0]+'_FV020 (vegetables) and '+r[0]+'_FV010 (fruit), '
      +'USDA Agricultural Marketing Service. Distance is to the market city, not to its own dock.</p>';
    out.hidden=false;
  }}
  q.addEventListener('input',go);
}})();
</script>"""

def price_report_date():
    """The newest report date carried by the price data, as a date.

    🔴 Added 2026-11-04 after the panel's skeptic seat found the real hazard in
    promoting price to the index's lead column: a one-day snapshot from an
    external market FREEZES if the capture stops or the mart is not rebuilt,
    and a frozen price in the lead column reads as current. That is worse than
    no price column at all — and it is the same failure as the `.txt` endpoint
    that serves HTTP 200 for a report from January 2024.
    """
    best = None
    for r in rows():
        if not r["la_report"]:
            continue
        try:
            d = datetime.datetime.strptime(
                r["la_report"].split(" ", 1)[-1], "%B %d, %Y").date()
        except ValueError:
            continue
        best = d if best is None or d > best else best
    return best

# A price older than this is not a reference price, it is a historical note.
MAX_PRICE_AGE_DAYS = 14

def price_rows():
    # ⭐ Ordered by ORIGIN, not by the alphabet. Alphabetical put "Anise — Gap
    # — California" at the head of a table whose argument is that some of what
    # Los Angeles sells was grown in this valley and trucked away. The crops
    # that carry that argument now lead it, and the order is stable while the
    # report's contents are not.
    def key(r):
        if r["la_origin_sjv"] == "yes":
            g = 0
        elif r.get("la_origin_ca") == "yes":
            g = 1
        else:
            g = 2
        return (g, r["crop"])
    return sorted((r for r in rows() if r["la_price_low"]), key=key)

def price_section():
    """USDA figures ship as REPORTED market conditions: attributed, dated, with the
    market and the basis stated. Never converted into a target — the build's PRICE
    patterns stop that."""
    pr = price_rows()
    if not pr: return ""
    date = pr[0]["la_report"].split(" ", 1)[-1]
    n_total = len(rows())
    sjv = [r["crop"] for r in pr if r["la_origin_sjv"] == "yes"]
    trs = "".join(
        f'<tr><td><a href="crops/{slug(r["crop"])}.html">{esc(r["crop"])}</a>'
        f'<span class="aka">reported as {esc(r["la_report_commodity"]).lower()}</span></td>'
        f'<td>{trade_chip(r)}</td>'
        f'<td>{esc(r["la_pack"]) or "&mdash;"}</td>'
        f'<td>${float(r["la_price_low"]):.2f}'
        + (f'&ndash;${float(r["la_price_high"]):.2f}'
           if float(r["la_price_high"]) != float(r["la_price_low"]) else "")
        + '</td>'
        f'<td>{"San Joaquin Valley" if r["la_origin_sjv"] == "yes" else ("California" if r.get("la_origin_ca") == "yes" else "&mdash;")}</td></tr>'
        for r in pr)
    return f"""
  <h2 style="margin-top:28px">What the alternative costs</h2>
  <p>A Fresno buyer&rsquo;s real choice is not between a local grower and nothing. It is between a
     local grower and the wholesale channel. So here is what that channel charged for
     these crops, on the day this was published.</p>
  <p class="src">Ordered by origin: what this valley grew and sent to Los Angeles first, then the
     rest of California, then everywhere else.</p>
  <div class="tbl"><table>
    <thead><tr><th>Crop</th><th>Kind of trade</th><th>Pack</th><th>Reported price</th>
      <th>Origin</th></tr></thead>
    <tbody>{trs}</tbody>
  </table></div>
  <p class="src">Los Angeles Terminal Market Vegetables Prices (HC_FV020) and Fruit Prices
     (HC_FV010), USDA Agricultural Marketing Service, {esc(date)}. Wholesale, f.o.b. shipping point
     as USDA reports it (7 CFR &sect;46.43(i)) &mdash; the figure excludes freight. <strong>{len(pr)} of the {n_total} crops in this catalogue appear in
     those two reports.</strong> Where a crop is quoted under a broader commodity name, the name the
     report used is shown beside it, and a crop is only priced from a block that names it &mdash; a
     generic price is not treated as a specialty price.</p>
  <div class="note">
    <p><strong>Read this as the price of the alternative, not as a local price and not as a
       recommendation.</strong> It is what a wholesale market in Los Angeles transacted at. It is not
       what a Fresno grower receives, it is not what a Fresno market pays locally, and it is not a
       figure we are suggesting anyone trade at. We publish it because it is public and because the
       people on the other side of the table already know it.</p>
    <p><strong>And look at the origin column.</strong> {len(sjv)} of these were quoted from the
       San Joaquin Valley &mdash; this valley: {esc(", ".join(sjv))}. Grown here, trucked to Los
       Angeles, and priced there. That is the gap this network exists to close, with a dollar figure
       on it.</p>
    <p><strong>{n_total - len(pr)} of the {n_total} have no published price anywhere.</strong> No terminal market
       reports them, no shipping-point report reports them. The same crops the county does not count
       and the 2010 survey did not reach.</p>
  </div>
"""

# ── Gate C assertions. A violation fails the build. ───────────────────────────
FORBIDDEN = [
    (r"you are exempt",      "rule 0: unconditional exemption"),
    (r"\bexempt from\b",     "rule 0: unconditional exemption"),
    (r"no requirements",     "rule 0: unconditional exemption"),
    (r"\bcompliant\b",       "ledger 2: compliance attaches to a party and an activity"),
    (r"\bopportunity\b",     "grower boundary: advice"),
    (r"\brecommended\b",     "grower boundary: advice"),
    (r"high demand",         "grower boundary: advice"),
    (r"\bprofitable\b",      "grower boundary: advice"),
    (r"\bin demand\b",       "grower boundary: advice"),
    (r"we suggest",          "grower boundary: advice"),
    (r"\byou should\b",      "grower boundary: advice"),
    (r"easy to grow",        "grower boundary: advice"),
    (r"\blow risk\b",        "grower boundary: advice"),
    (r"deadline (has )?(moved|changed)", "ledger 7: the CFR date has not moved"),
    # ── added 2026-11-04 with the conversion repairs ──────────────────────────
    # 🔴 Incoterms do not settle freight responsibility. 7 CFR §46.43(i) puts
    # transit risk on the buyer "irrespective of how the shipment is billed",
    # so billing is severed from risk — this sentence is the exact error the
    # regulation exists to prevent.
    (r"incoterms[^.]{0,140}(settle|settled|settles|responsib)",
     "§46.43(i): billing is severed from risk; Incoterms do not settle it"),
    # 🔴 Never assert that a licence or registration is or is not required.
    # PACA's broker definition (7 U.S.C. §499a(b)(7)) has no possession and no
    # title element, and whether it reaches this venture is an open question
    # with Legal & Ethics. Copy does not answer it.
    (r"(licen[cs]ed?|registration)\s*(is|are)?\s*(not\s+)?(required|needed)",
     "open PACA question: copy never asserts licensing status"),
    (r"no\s+licen[cs]e", "open PACA question: copy never asserts licensing status"),
    # 🔴 Never self-describe as a regulatory CATEGORY. Describe conduct. The
    # footer and the About page both said "we are not a distributor, a broker
    # or a wholesaler" — three legal categories, one of which is live.
    (r"not a (distributor|broker|wholesaler|dealer|commission merchant)",
     "describe conduct, not a regulatory category"),
    # 🔴 Added 2026-11-04 with soil testing. A soil test establishes what the
    # soil IS, never what a crop WILL DO. For the uncounted crops no trial has
    # been published in this valley, so a suitability finding has no basis —
    # and a grower whose soil has just been tested will infer one unless the
    # copy refuses it outright.
    (r"(soil|ground|irrigation)[^.]{0,80}(suitable for|suited to|right for|will (grow|produce|support))",
     "a soil or irrigation result is not a crop-suitability finding"),
    (r"(suitable|suited|ideal|perfect) (for growing|conditions for)",
     "a soil or irrigation result is not a crop-suitability finding"),
]
PRICE = [r"per\s*(lb|pound|kg|case|box|carton)\b", r"/\s*lb\b", r"price per", r"\bwholesale price",
         r"\$\s?\d+(\.\d{2})?\s*(each|per|/)",
         # Added 2026-11-03 with the pricing-gate reclassification. USDA Market
         # News figures may ship as REPORTED market conditions — attributed,
         # dated, and never converted into a recommendation. These five patterns
         # are the conversion, and the build stops on any of them.
         r"suggested price", r"target price", r"recommended price",
         r"you should charge", r"\bmarket rate\b"]

def checked_class_note():
    """Say what the six actually are, in the catalogue's own terms. Two are
    gap crops; the rest the county names only inside an aggregate. Collapsing
    the two into "gap crops" is the error this note exists to prevent."""
    byname = {r["crop"]: r["crop_class"] for r in rows()}
    g = [c for c in CHECKED_NO_TRIAL if byname.get(c) == "gap"]
    o = [c for c in CHECKED_NO_TRIAL if byname.get(c) != "gap"]
    bits = []
    if g:
        bits.append(f'{len(g)} of these ({", ".join(c.lower() for c in g)}) this '
                    f'county reports in no line and no footnote')
    if o:
        bits.append(f'{len(o)} ({", ".join(c.split(" /")[0].lower() for c in o)}) '
                    f'it does name, inside an aggregate line with no acreage and '
                    f'no value of their own')
    return (" and ".join(bits) + ". Being named is not being measured, and "
            "neither is the same as an absence of extension data — which "
            "is a separate search, and the one we are reporting here.")

def text_of(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    for a,b in (("&mdash;","—"),("&ndash;","–"),("&rsquo;","’"),("&ldquo;","“"),("&rdquo;","”"),
                ("&sect;","§"),("&amp;","&"),("&times;","×"),("&reg;","®"),("&middot;","·"),
                ("&iacute;","í"),("&rarr;","→"),("&nbsp;"," ")):
        t = t.replace(a,b)
    return re.sub(r"\s+"," ",t)

def check(pages):
    fails = []
    for name, html in pages.items():
        t = text_of(html)
        for pat, why in FORBIDDEN:
            if re.search(pat, t, re.I):
                fails.append(f"{name}: FORBIDDEN — {why} :: …{re.search(pat,t,re.I).group(0)}…")
        for pat in PRICE:
            if re.search(pat, t, re.I):
                fails.append(f"{name}: PRICE — matched {pat!r}")

    # Condition 1 — relief.tlc and relief.boundary adjacent on buyers.html
    bt = text_of(pages["buyers.html"])
    i, j = bt.find(RELIEF_TLC[:48]), bt.find(RELIEF_BOUNDARY[:48])
    if i < 0 or j < 0:
        fails.append("buyers.html: condition 1 — one or both relief strings missing")
    elif not (0 < j - i < 700):
        fails.append(f"buyers.html: condition 1 — relief.boundary is {j-i} chars from relief.tlc; "
                     "they must stay adjacent")

    # Condition 2 — About carries no currency at all
    if re.search(r"\$\s?\d", text_of(pages["about.html"])):
        fails.append("about.html: condition 2 — a currency figure appears beside the structure claim")

    # Condition 3 — no acres-per-grower figure without its denominator
    # Condition 3 protects the two CROSS-CROP acres-per-grower statistics (the
    # ledger's median-2.79-across-19 and the catalogue's 10-of-26 / median 3.33),
    # which are the pair that can be quoted against each other. A single crop's
    # own arithmetic — 128 acres over 66 growers — is not one of them, but a
    # reader cannot tell the two apart, so it must carry its own attribution.
    DEN = re.compile(r"ten of twenty-six|26 catalogue crops|twenty-six crops in the catalogue"
                     r"|survey of that one crop", re.I)
    for name, html in pages.items():
        t = text_of(html)
        if re.search(r"acres? (each|per grower)", t, re.I) and not DEN.search(t):
            fails.append(f"{name}: condition 3 — an acres-per-grower figure ships without its denominator")

    # Condition 4 (B1) — the premium and the decline belong to the SPECIALTY
    # subset and must say so on the page that quotes them. Both figures are
    # computed from the county's single "Oriental Vegetables" line, so they
    # describe the crops inside that line and nothing else. The catalogue now
    # also carries commodity crops the county reports on their own lines, and
    # an unqualified premium reads as a claim about all of them.
    SUBSET_CLAIM = re.compile(r"times the value of the average|acreage fell \d", re.I)
    SUBSET_QUAL = re.compile(r"not about this whole catalogue|"
                             r"one line of the county\u2019s report|"
                             r"one line of the county's report", re.I)
    for name, html in pages.items():
        t = text_of(html)
        if SUBSET_CLAIM.search(t) and not SUBSET_QUAL.search(t):
            fails.append(f"{name}: condition 4 — the premium or decline figure ships "
                         "without naming the specialty subset it belongs to")

    # Condition 5 (B3) — the gap chip must never render on a commodity crop.
    # Keyed to the raw county status it fired on garlic, onions and table
    # grapes: a "contractable gap" chip on crops this county grows at scale.
    for r in rows():
        if r["crop_class"] != "gap":
            nm = f"crops/{slug(r['crop'])}.html"
            if nm in pages and "Contractable" in text_of(pages[nm]):
                fails.append(f"{nm}: condition 5 — gap chip on a "
                             f"{r['crop_class']} crop")

    # Condition 6 — never call a crop a gap crop unless crop_class says so.
    byname = {r["crop"]: r["crop_class"] for r in rows()}
    not_gap = [c for c in CHECKED_NO_TRIAL if byname.get(c) != "gap"]
    for name, html in pages.items():
        t = text_of(html)
        if re.search(r"gap crops? we checked|the (six|\d+) gap crops", t, re.I) \
           and not_gap:
            fails.append(f"{name}: condition 6 — calls {len(not_gap)} non-gap "
                         f"crop(s) a gap crop: {', '.join(not_gap)}")

    # Condition 7 — an unqualified "f.o.b." is a defect. The abbreviation means
    # three different things: Incoterms FOB (maritime only; the road equivalent
    # is FCA), UCC §2-319, and PACA 7 CFR §46.43(i). Wherever the site uses it,
    # the produce-trade citation has to be within reach of the reader.
    for name, html in pages.items():
        t = text_of(html)
        for m in re.finditer(r"\bf\.?o\.?b\.?\b", t, re.I):
            if "46.43" not in t[m.start():m.start() + 500]:
                fails.append(f"{name}: condition 7 — an unqualified "
                             f"\u201c{m.group(0)}\u201d ships without its 7 CFR "
                             f"\u00a746.43 citation within reach")
                break

    # Condition 8 — the surface job register, enforced.
    # DIRECT RESPONSE surfaces must carry the ask. CREDIBILITY surfaces must
    # route to a response page and must NOT point straight at the join: a
    # credibility page that asks for the membership has skipped the step that
    # earns it.
    ASK = "Email us"
    for nm in ("buyers.html", "growers.html", "qualify.html"):
        if ASK not in text_of(pages[nm]):
            fails.append(f"{nm}: condition 8 — a direct-response surface with no ask")
    for nm in ("catalogue.html", "inspect.html", "about.html"):
        t = text_of(pages[nm])
        if ASK in t:
            fails.append(f"{nm}: condition 8 — a credibility surface carrying the ask")
        if "For Buyers" not in t and "For Growers" not in t:
            fails.append(f"{nm}: condition 8 — a credibility surface with no next step")
    for nm, html in pages.items():
        if not nm.startswith("crops/"):
            continue
        # the nav carries qualify.html on every page by design — strip the
        # chrome before judging the page's own next step, or the check
        # convicts the navigation.
        body = re.sub(r"<nav.*?</nav>|<footer.*?</footer>", " ", html, flags=re.S)
        if 'href="../qualify.html"' in body:
            fails.append(f"{nm}: condition 8 — a product page pointing straight at the join")
            break

    # Vault annotation markers are a note-taking convention, not site copy.
    # One leaked into a shipped paragraph on the first prices build.
    for name, html in pages.items():
        bad = [c for c in "\u2b50\U0001f534\u26a0\u2705" if c in html]
        if bad:
            fails.append(f"{name}: vault annotation marker(s) {bad} leaked into shipped copy")

    # 🔴 price freshness. The index leads with "Trading at"; a stale figure
    # there is a false claim about today's market, so it fails the build rather
    # than shipping. Refresh with:
    #   python3 -I /home/adrian/data-engineering/scripts/capture_terminal_prices.py
    #   then rebuild the catalogue mart (scripts/build_catalogue_v2.py)
    prd = price_report_date()
    if prd is None:
        fails.append("price data carries no readable report date "
                     "(la_report) — the index cannot date its own prices")
    else:
        age = (datetime.date.today() - prd).days
        if age > MAX_PRICE_AGE_DAYS:
            fails.append(
                f"price data is {age} days old (report {prd.isoformat()}, limit "
                f"{MAX_PRICE_AGE_DAYS}) — the catalogue leads with a price column "
                f"and will not ship a stale one; re-run the capture and rebuild "
                f"the mart")

    # the name keeps its diacriticals: ʻokina U+02BB and Ā U+0100
    for name, html in pages.items():
        if "ʻĀina" not in html:
            fails.append(f"{name}: the name has lost its ʻokina or kahakō")
    return fails

def main():
    rs = rows()
    pages = {"index.html": home_page(), "catalogue.html": catalogue_page(rs),
             "inspect.html": inspect_page(), "market.html": market_page(),
             "buyers.html": buyers_page(),
             "growers.html": growers_page(), "about.html": about_page(),
             "qualify.html": qualify_page(), "growing.html": growing_page()}
    for r in rs:
        pages[f"crops/{slug(r['crop'])}.html"] = product_page(r)

    fails = check(pages)
    if fails:
        print("BUILD FAILED — Gate C conditions:")
        for f in fails: print("  ✗", f)
        return 1

    if os.path.isdir(DIST): shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "crops"))
    for name, html in pages.items():
        with io.open(os.path.join(DIST, name), "w", encoding="utf-8") as f:
            f.write(html)
    for css in ("tokens.css", "site.css"):
        shutil.copy(os.path.join(ROOT, "src", css), os.path.join(DIST, css))
    shutil.copytree(os.path.join(ROOT, "fonts"), os.path.join(DIST, "fonts"))

    slugs = [slug(r["crop"]) for r in rs]
    assert len(set(slugs)) == len(slugs), "slug collision"
    print(f"BUILD OK — {len(pages)} pages ({len(rs)} product pages), "
          f"{len(set(slugs))} unique slugs, Gate C conditions all pass")
    return 0

if __name__ == "__main__":
    sys.exit(main())
