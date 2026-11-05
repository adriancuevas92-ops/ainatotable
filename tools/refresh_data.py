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
import filecmp, os, shutil, sys

MARTS = "/home/adrian/data-engineering/marts"
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
FILES = (
    "aina_to_table_crop_catalogue_v2_2026-11-04.csv",
    "usda_terminal_market_by_zip3_2026-11-04.csv",
    "usda_terminal_market_registry_2026-11-04.csv",
)


def main(check=False):
    if not os.path.isdir(MARTS):
        sys.exit(f"mart directory not found: {MARTS}\n"
                 "This script only runs on the machine that builds the marts.")
    os.makedirs(DATA, exist_ok=True)
    stale, copied = [], []
    for name in FILES:
        src, dst = os.path.join(MARTS, name), os.path.join(DATA, name)
        if not os.path.exists(src):
            sys.exit(f"missing mart: {src}")
        same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
        if same:
            continue
        stale.append(name)
        if not check:
            shutil.copyfile(src, dst)
            copied.append(name)

    if check:
        for name in stale:
            print(f"  STALE  {name}")
        print(f"{len(stale)} of {len(FILES)} differ from the mart")
        return 1 if stale else 0

    for name in copied:
        print(f"  copied {name}")
    print(f"{len(copied)} of {len(FILES)} refreshed"
          + ("" if copied else " — data/ already matched the marts"))
    if copied:
        print("\nNow: python3 -I build.py   then commit data/ with the output")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
