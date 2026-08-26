# ʻĀina to Table — site maintenance handoff

Paste this whole document as your first message in a new Claude Code
session to pick up maintenance on this project with full context.

## What this project is

ʻĀina to Table (ainatotable.com) is a free food-forest planning
information site, and the public face of a food forest venture based
on the family's land in South Kona, Hawaiʻi. It's partnered with a
real nonprofit, **Nā Hoa Ululāʻau O Kalamawaiʻawaʻawa** (own site:
ululaau.org), which manages and restores the actual land — the
nonprofit does restoration; ʻĀina to Table is the separate commercial
venture that grows and sells from it. Keep these two entities
distinct in any copy — never conflate them, never shorten the
nonprofit's name (see "Hard rules" below).

Core thesis carried through the whole site: food is one of the
fastest ways to connect with a culture, and this venture is built on
Hawaiian values — laulima (many hands, shared ownership of what's
grown, not just wage labor), mālama ʻāina (reciprocal care for the
land), kuleana (responsibility that comes with access). The site
gives away real planning information for free before selling
anything.

## Where everything lives

- **Working directory**: `C:\Users\adria\Claude\food-forest-website\`
- **GitHub repo**: `adriancuevas92-ops/ainatotable` (public), remote
  `origin` already configured, branch `main`.
- **Live site**: https://ainatotable.com — GitHub Pages, custom
  domain, HTTPS enforced. DNS is at Porkbun (the domain registrar);
  A records point at GitHub Pages' four IPs, plus a `www` CNAME to
  `adriancuevas92-ops.github.io` (added manually — Porkbun's own
  wildcard CNAME would otherwise swallow `www` and route it to their
  parking page instead of GitHub Pages).
- **Deploy mechanism**: GitHub Actions, `.github/workflows/deploy.yml`
  — on every push to `main`, it runs `python build.py` and publishes
  `site/` to GitHub Pages via `actions/upload-pages-artifact` +
  `actions/deploy-pages`. You do not deploy manually; you push to
  `main` and it deploys itself. Watch it with
  `gh run list --limit 1` / `gh run watch <id>`.
- **Email**: `hello@ainatotable.com` is a real, working paid mailbox
  (Porkbun Email Hosting, ~$36/yr after a 15-day trial that started
  2026-08-23 — check it hasn't lapsed).

## Build system

Static site generator, deliberately dependency-light:

- `build.py` — reads Markdown from `articles/` and `tools/`, converts
  to HTML with the `markdown` package, rewrites internal links via a
  `LINK_MAP`, wraps every page in a shared header/nav/footer template,
  writes everything to `site/` (gitignored, rebuilt fresh every time —
  never hand-edit anything under `site/`).
- Run it locally with `python build.py` from the project root.
  Requires `pip install -r requirements.txt` (just the `markdown`
  package).
- **Known Windows gotcha**: if you serve `site/` locally with
  `python -m http.server` and then try to rebuild, `build.py`'s
  `shutil.rmtree(SITE)` can fail with `PermissionError: [WinError 32]`
  because the running server still holds the directory open. Kill the
  server first: find the PID with
  `netstat -ano | grep ":<port>" | grep LISTENING` and
  `taskkill //PID <pid> //F`, then rebuild.
- **Git identity isn't configured globally** in this environment —
  every commit needs `git -c user.name="Adrian Cuevas" -c
  user.email="adriancuevas92@gmail.com" commit ...` or it fails.
- **GitHub CLI isn't on PATH** by default — prefix commands with
  `export PATH="$PATH:/c/Program Files/GitHub CLI"` in Bash, or call
  it by full path.

## Directory structure

```
articles/                  — Markdown source for every page (one file per page)
  home.md                  — landing page, has raw HTML hero + card grid
  01-what-is-a-food-forest.md ... 08-glossary.md  — the 8-part Learn library
  homeowners-start-your-food-forest.md
  restaurants-own-your-ingredients.md
  case-study-na-hoa-ululaau.md   — the nonprofit case study + live weather widget
  about-contact.md          — mission/values + contact
tools/                      — the 4 downloadable planning tools (worksheet, planner, species list, hand-pounded poi starter checklist)
assets/
  style.css                 — all site styling, one file, CSS custom properties for the palette
  weather.js                — vanilla JS, powers the case study page's live weather widget (Open-Meteo API)
  photos/                   — real photos of the actual South Kona site (sourced from ululaau.org, with permission implied by family relationship)
build.py                    — the static site generator (see above)
requirements.txt            — just `markdown`
.github/workflows/deploy.yml — the GitHub Actions deploy workflow
content-plan.md             — original content plan / site map (historical reference)
MAINTENANCE-HANDOFF.md      — this file
```

Gitignored (present locally, not in the repo): `site/` (build output),
`logo-canvas/` and `assets/logo/` (Claude Design working files from
logo exploration — see "Logo status" below).

## Hard rules — things that broke before, don't repeat them

1. **Hawaiian diacritics must render correctly, always.** This site
   uses the ʻokina (a glottal-stop mark, e.g. in ʻĀina, Hawaiʻi,
   ʻōlena) and macron vowels (ā, ē, ī, ō, ū) constantly and
   correctly is non-negotiable — this has been the single most
   corrected category of mistake on this project.
   - The **ʻokina character is U+02BB** (MODIFIER LETTER TURNED
     COMMA, decimal 699 / `&#699;`). **Not** U+02BC (decimal 700,
     MODIFIER LETTER APOSTROPHE) — that's a different character and
     was shipped by mistake once (in a generated PDF) before being
     caught and fixed. If you're ever unsure which character is in a
     string, check its codepoint, don't eyeball it.
   - **Fraunces (a Google Font) silently fails to render these
     diacritics correctly** — it drops the macron on lowercase ā and
     mangles the ʻokina into a stray mark. It was the original
     heading font and had to be replaced site-wide. **Headings use
     Noto Serif now** (`assets/style.css`, `h1, h2, h3` and every
     other `font-family: "Noto Serif"` rule) — verified correct via
     pixel-level canvas measurement, not just eyeballing. Do not
     reintroduce Fraunces, or any other font, without actually
     verifying ʻokina + macron render correctly first (render it,
     screenshot or measure it, don't assume).
   - When in doubt on a specific word's correct spelling, check how
     it's already spelled elsewhere on the site (grep for it) rather
     than guessing.
2. **The nonprofit's full name is "Nā Hoa Ululāʻau O
   Kalamawaiʻawaʻawa."** Not the shortened "Nā Hoa Ululāʻau" — that
   was used inconsistently early on (heading said one thing, body
   text said another) and had to be corrected site-wide. Use the full
   name every time the org is named.
3. **The site's location is South Kona** (Captain Cook, near
   Kealakekua Bay — coordinates roughly 19.5064, -155.9169), **not
   North Kona** — those are two different districts on Hawaiʻi
   Island. This was flagged once as a possible mix-up; South Kona is
   confirmed correct and used consistently everywhere (including the
   weather widget's coordinates).
4. **Don't put a location or gloss in parentheses right after a
   Hawaiian word/name.** E.g. "Nā Hoa Ululāʻau (South Kona)" was
   flagged as reading like a mistranslation, because that's exactly
   the pattern the site uses elsewhere for real translations (e.g.
   "ʻŌlena (turmeric)"). If a heading needs a location, put it on its
   own line/subtitle instead of in parens.
5. **Cultural tone**: no tiki/tourist clichés, no palm-tree-and-sunset
   imagery, no generic Polynesian tribal patterns. The kalo (taro)
   leaf is the one visual motif in use, chosen deliberately because
   kalo is already central to the site's real content (the Hāloa
   genealogy story on the About page), not decoration borrowed from
   outside it. Content tone generally: matter-of-fact and declarative
   (modeled after agroecologyfund.org/what-is-agroecology/ — short
   sentences, plain statements, not marketing rhetoric), honest about
   the venture's early stage rather than polished-sounding, and
   explicit that this is a real business (not hidden or apologized
   for) built on top of real cultural values.
6. **Don't fabricate specifics about the nonprofit** you haven't
   verified — e.g. don't claim they have a specific volunteer program
   or in-kind donation process unless you've actually seen it on
   ululaau.org. Keep copy about them general/honest rather than
   invented.

## Logo status — unresolved, don't re-guess

A full logo system was explored and largely **rejected**:

- A hand-coded SVG attempt (kalo leaf mark, badge/seal, lockup) was
  built, but had real centering/alignment problems.
- It was rebuilt properly via the Claude Design canvas tool (more
  precise, verified via pixel measurement) and published — that
  artifact still exists but is a separate exploration, not adopted.
- A refined version was found in a **claude.ai/design project**
  (project id `ac381ff8-ba30-4f4f-bb3c-0903ec739989`, accessed via the
  `DesignSync`/`claude_design` MCP tool) with three directions:
  **1A** (circular seal with the leaf + values text), **1B**
  (horizontal icon + wordmark lockup — **this is the one direction
  the user actually approved**), and **1C** (a completely different
  "tree mark," not the leaf — never adopted, conflicts with 1A/1B's
  symbol).
- 1B was integrated into the live site header + favicon once, but
  **was reverted** — the user's exact words were "It doesn't work as
  a site header." It was reverted with `git revert` (commit
  `c5dbbc3`), so the header is back to plain text
  "ʻĀina to Table," no favicon.
- 1B was exported as a standalone PDF at its native 760×260 size
  (delivered to the user directly, not committed to the repo).
- **Net state: there is currently no logo anywhere on the live
  site.** If asked to add one again, start from 1B (the only
  approved direction) but **do not simply reinsert it into the site
  header** the same way — that was explicitly rejected. Ask where/how
  before re-implementing, and consider that "doesn't work as a site
  header" likely means something about scale, contrast, or the
  cream/dark-green swap needed for the header background specifically
  — worth asking rather than re-guessing the same execution.

## Live weather widget (case-study.html)

`assets/weather.js` + markup embedded in
`articles/case-study-na-hoa-ululaau.md` (`<div class="weather-band"
id="konaWeather" data-lat="19.5064" data-lon="-155.9169">`). Fetches
current conditions + 4-day forecast from the free Open-Meteo API (no
key required), plus a live-ticking local clock in HST. Refreshes every
10 minutes client-side. If you touch this, keep the lat/lon in sync
with "South Kona" (see Hard Rules #3) and don't break the loading /
error states (`#weatherLoading`, `#weatherError`, `#weatherContent`).

## Recent changes (most recent first, as of 2026-08-25)

1. Home page (`articles/home.md`): hero paragraph and closing
   "See it working" section rewritten to make the mission explicit —
   invasive growth is what interrupted the kalo/ʻōlena/breadfruit
   guild, the goal is scaling it back up (not keeping it small), and
   framed as putting control back with the people doing the growing
   (laulima/labor-ownership throughline). Kept to the site's
   info-first voice — stated as fact, not a pitch. Verified okina
   codepoints (U+02BB) render correctly in browser before pushing.
2. New Tools page: `tools/hand-pounded-poi-starter-guide.md` — a
   practical checklist companion to `how-poi-is-made.md` (what
   Hawaiʻi's hand-pounded exemption actually requires, realistic
   startup cost, GAP/insurance expectations for institutional sales,
   the upland-vs-wetland taro note, and a UBIT caution for nonprofits).
   Deliberately generalized, not tied to any specific grower — this
   site doesn't publish Nā Hoa Ululāʻau's own internal business
   planning (that stays in the family's private working notes), only
   generalized public information anyone growing kalo could use, same
   split already established for the grant-tracker tool. Added to
   `build.py`'s `PAGES` list and cross-linked from
   `how-poi-is-made.md`. Committed and pushed to `main`
   (`c8aa935`); deploy watched end-to-end via `gh run watch`, confirmed
   live at `/tools/hand-pounded-poi-starter-guide.html` with correct
   diacritics.
3. Case study page: "Support the restoration work directly" section
   added, linking to `https://ululaau.org/contact`. Explicitly framed
   as *not* only monetary — "time, tools, materials, and expertise"
   — because the nonprofit accepts more than donations and the copy
   shouldn't imply otherwise.
4. Site header/favicon logo: added, then reverted (see "Logo status"
   above).
5. Org full name fix, Noto Serif font fix, case-study heading fix, the
   ʻĀina okina fix, the weather widget build — see git log for full
   detail, messages are descriptive.

## Suggested first move in a new session

Run `git log --oneline -20` and `git status` to see exactly where the
repo stands relative to this document (things may have moved since it
was written), then `python build.py` to confirm the build still works
cleanly before making any changes.
