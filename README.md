# ʻĀina to Table — public surface

Static site. `python3 -I build.py` regenerates everything into `dist/`.

**Eight surfaces plus one generated page per crop.** The 166 product pages come from
`data/aina_to_table_crop_catalogue_v2_2026-11-04.csv` — one template decided once, as
Gate C1 approved. No CMS: 166 pages from 166 rows, regenerated when the data changes.

The catalogue index leads with **price and origin** as of 2026-11-04 (decisions D2–D4):
Crop · Trading at · Origin quoted · In season here · What kind of trade this is. The
cuisine filter was retired from the index — it covered 74 of 166 rows, so using it hid
55% of the catalogue. Cuisine stays on the product page.

Copy is the approved decks C2a–C2f in
`~/vaults/Brand & Design/03 - Brand Work/`. Every factual line traces to a ledger
claim in `Message Strategy v1` §6 — 27 verified, 3 computed, 7 forbidden, 1 drafting rule.

## The build is a gate, not a bundler

`build.py` refuses to write output if any of these fails:

1. **The 20 forbidden-string patterns** (drafting rule 0, ledger claims 2 and 7, the
   grower-view advice list, the open PACA question, the Incoterms/§46.43(i) error,
   the soil-result boundary) against the rendered text of every page.
2. **The 10 price patterns.** Prices themselves ship — reported, attributed and dated,
   as decided 2026-11-03. What the build stops is the *conversion* of a reported figure
   into a recommendation (`suggested price`, `target price`, `market rate`,
   `you should charge`) and per-unit retail phrasing. `about.html` additionally carries
   no currency figure at all, because the statement about lawful coordination sits there.
3. **Price freshness.** `MAX_PRICE_AGE_DAYS = 14`, read from the report date inside
   `data/`. The catalogue index leads with a price column, so a stale figure there is a
   false claim about today's market and the build refuses it rather than shipping it.
   Refresh with `python3 -I tools/refresh_data.py`, then rebuild.
4. **`relief.tlc` and `relief.boundary` stay adjacent** on `buyers.html`. The flat
   statement about which party the rule binds is only safe because the boundary
   follows it immediately.
5. **No acres-per-grower figure without its denominator.**
6. **The name keeps its ʻokina and kahakō** on every page. Diacriticals are letters.
7. **No vault annotation marker** (⭐ 🔴 ⚠ ✅) reaches shipped copy.

The first run failed on 2 and 5. The 2026-11-04 rebuild failed on 7, which caught a
marker inside a JavaScript comment. See the Decision Log for both.

## Deliberate absences

- **No photography.** The six South Kona images retired with the Origin page; no crop
  photography exists. The mark, the locked palette and the typography carry the identity.
- **No native-range map and no botanical names yet.** Kew's structured distribution
  source refuses automated access, and a GBIF occurrence record is not a native range.
- **No member surface.** Phase 4, blocked on formation, not on design.
- **Single theme.** The palette is locked and measured; a page that recoloured to the
  viewer's OS would not be the thing that was locked.

## Layout

    build.py       the generator and the gate
    preview.py     transforms dist/ into a clickable artifact preview
    data/          the three CSVs the build reads, vendored. NOT read from
                   ~/data-engineering/marts: a CI runner cannot see that path,
                   and local and CI must build the same site from one commit
    tools/         refresh_data.py — re-copies data/ from the marts
    src/tokens.css the locked palette as code. Colour-named aliases were removed
                   at this build, as the file itself instructed
    src/site.css   layout, role-named tokens only
    fonts/         6 woff2 subsets, all carrying U+02BB
    dist/          output — do not edit, not committed; it is regenerated
    .github/       the Pages deploy. MANUAL ONLY — there is no push trigger,
                   because messaging approval and the PACA question are open

## Deploying

`main` is ainatotable.com. The Pages deploy runs on push to `main`, so **merging
publishes**. A branch push deploys nothing.

That makes the pull request the gate, and two things must close on it before a merge:

- Adrian's standing instruction to confirm messaging and strategy before content ships.
- The PACA broker question with Legal & Ethics — `7 U.S.C. §499a(b)(7)` has no
  possession and no title element, and whether it reaches this venture is unresolved.
  It is recorded as blocking the public copy.

The custom domain is held in repo settings, not a tracked `CNAME` file, so it survives
an Actions deploy without anything in `dist/`.

`build.py` is itself a gate and runs in CI: it refuses to write output on any Gate C
violation, including price data older than `MAX_PRICE_AGE_DAYS`. A stale catalogue fails
the build rather than publishing a false claim about today's market.
