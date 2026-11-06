#!/usr/bin/env python3
"""Copy the three catalogue marts into data/, so the repo can build itself.

The build reads data/ and never /home/adrian/data-engineering/marts, because a
CI runner cannot see that directory and because local and CI must produce the
same site from the same commit. That means the repo copy goes stale on its own
and this is what refreshes it.

Run:  python3 -I tools/refresh_data.py
      python3 -I tools/refresh_data.py --check   # exit 1 if a copy is stale

After refreshing, rebuild and commit data/ with the output — the price
freshness gate in build.py (MAX_PRICE_AGE_DAYS) reads the report date out of
the copy in data/, so a stale copy fails the build rather than shipping.
"""
import datetime, filecmp, glob, io, os, shutil, sys

MARTS = "/home/adrian/data-engineering/marts"
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# 🔴 Resolved by GLOB, not pinned to a date.
# build_catalogue_v2.py writes aina_to_table_crop_catalogue_v2_<today>.csv — a
# NEW filename every run. This script and build.py both pinned the 2026-11-04
# name, so neither would ever have seen a rebuilt mart and the price-freshness
# gate would have failed with no way to satisfy it. The marts keep their dated
# names (point-in-time discipline); the repo copy takes a STABLE name so
# build.py is never edited to follow a date, and data/PROVENANCE.txt records
# which dated mart each copy came from.
FILES = {
    "crop_catalogue_v2.csv": "aina_to_table_crop_catalogue_v2_*.csv",
    "usda_terminal_market_by_zip3.csv": "usda_terminal_market_by_zip3_*.csv",
    "usda_terminal_market_registry.csv": "usda_terminal_market_registry_*.csv",
    "price_per_acre_chart.csv": "fresno_price_per_acre_chart_*.csv",
}


def newest(pattern):
    """The most recent mart matching pattern, by the DATE IN THE FILENAME.

    ⚠ Not by mtime: a re-copied or touched older file would win on mtime and
    silently reinstate stale data, which is the failure this whole gate exists
    to prevent.
    """
    hits = sorted(glob.glob(os.path.join(MARTS, pattern)))
    return hits[-1] if hits else None


def _write_provenance(prov):
    with io.open(os.path.join(DATA, "PROVENANCE.txt"), "w", encoding="utf-8") as fh:
        fh.write("Which dated mart each committed copy came from.\n"
                 "Written by tools/refresh_data.py; do not edit by hand.\n"
                 f"Data last changed: {datetime.date.today().isoformat()}\n\n")
        fh.write("\n".join(prov) + "\n")


def main(check=False):
    if not os.path.isdir(MARTS):
        sys.exit(f"mart directory not found: {MARTS}\n"
                 "This script only runs on the machine that builds the marts.")
    os.makedirs(DATA, exist_ok=True)
    stale, copied, prov = [], [], []
    for dest_name, pattern in sorted(FILES.items()):
        src = newest(pattern)
        if src is None:
            sys.exit(f"no mart matches {pattern} in {MARTS}")
        dst = os.path.join(DATA, dest_name)
        prov.append(f"{dest_name}  <-  {os.path.basename(src)}")
        same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
        if same:
            continue
        stale.append(dest_name)
        if not check:
            shutil.copyfile(src, dst)
            copied.append(f"{dest_name}  <-  {os.path.basename(src)}")

    if check:
        for name in stale:
            print(f"  STALE  {name}")
        print(f"{len(stale)} of {len(FILES)} differ from the newest mart")
        return 1 if stale else 0

    # 🔴 Written only when something was actually copied. Rewriting it on every
    # run put a fresh timestamp in the tree each time, which made data/ dirty
    # forever and would have produced a noise commit every night. "When the data
    # last CHANGED" is the useful fact; "when we last checked" is in the log.
    if copied:
        _write_provenance(prov)
    for line in copied:
        print(f"  copied {line}")
    print(f"{len(copied)} of {len(FILES)} refreshed"
          + ("" if copied else " — data/ already matched the newest marts"))
    if copied:
        print("\nNow: python3 -I build.py   then commit data/")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
