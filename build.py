"""
Static site builder for ʻĀina to Table (ainatotable.com).
Reads the Markdown content under articles/ and tools/, converts it to HTML,
rewrites internal links, and writes a deployable static site to site/.

No framework, no build system beyond this script and the `markdown` package
(pip install markdown) — deliberately simple so it's easy to maintain by hand.
Run: python build.py
"""

import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
SITE = ROOT / "site"
SITE_NAME = "ʻĀina to Table"
SITE_TAGLINE = "Free information on planning a food forest — and taking ownership of your food supply."

# source markdown path (relative to ROOT) -> output path (relative to SITE, root-relative URL)
PAGES = [
    ("articles/home.md", "index.html"),
    ("articles/01-what-is-a-food-forest.md", "learn/what-is-a-food-forest.html"),
    ("articles/02-planning-your-site.md", "learn/planning-your-site.html"),
    ("articles/03-design-layers-and-guilds.md", "learn/design-layers-and-guilds.html"),
    ("articles/04-plant-selection.md", "learn/plant-selection.html"),
    ("articles/05-soil-water-and-establishment.md", "learn/soil-water-and-establishment.html"),
    ("articles/06-timeline-and-what-to-expect.md", "learn/timeline-and-what-to-expect.html"),
    ("articles/07-maintenance-and-harvest.md", "learn/maintenance-and-harvest.html"),
    ("articles/08-glossary.md", "learn/glossary.html"),
    ("articles/restaurants-own-your-ingredients.md", "restaurants.html"),
    ("articles/homeowners-start-your-food-forest.md", "homeowners.html"),
    ("articles/case-study-na-hoa-ululaau.md", "case-study.html"),
    ("articles/about-contact.md", "about.html"),
    ("tools/site-assessment-worksheet.md", "tools/site-assessment-worksheet.html"),
    ("tools/seven-layer-planting-planner.md", "tools/seven-layer-planting-planner.html"),
    ("tools/hawaii-species-starter-list.md", "tools/hawaii-species-starter-list.html"),
]

# basename of source .md file -> root-relative output URL, for link rewriting
LINK_MAP = {Path(src).name: "/" + out for src, out in PAGES}

NAV = [
    ("/", "Home"),
    ("/learn/", "Learn"),
    ("/homeowners.html", "For Homeowners"),
    ("/restaurants.html", "For Restaurants"),
    ("/case-study.html", "Case Study"),
    ("/tools/", "Tools"),
    ("/about.html", "About"),
]

MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")


def rewrite_links(md_text: str) -> str:
    def repl(match: re.Match) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        basename = href.split("/")[-1]
        if basename in LINK_MAP:
            return "](" + LINK_MAP[basename] + ")"
        return match.group(0)

    return MD_LINK_RE.sub(repl, md_text)


def page_title(html_body: str, fallback: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html_body, re.S)
    if match:
        return re.sub("<[^>]+>", "", match.group(1)).strip()
    return fallback


def render_page(title: str, body_html: str, out_path: Path) -> str:
    depth = len(out_path.relative_to(SITE).parts) - 1
    css_href = "/assets/style.css"
    nav_links = "\n".join(
        f'      <a href="{href}">{label}</a>' for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {SITE_NAME}</title>
<meta name="description" content="{SITE_TAGLINE}">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_href}">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/logo-header.svg" alt="" width="30" height="30">{SITE_NAME}</a>
    <nav>
{nav_links}
    </nav>
  </div>
</header>
<main class="wrap content">
{body_html}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>{SITE_NAME} — free information, always. Grown out of a real food forest in South Kona, Hawaiʻi.</p>
    <p><a href="/about.html">About</a> &middot; <a href="mailto:hello@ainatotable.com">hello@ainatotable.com</a></p>
  </div>
</footer>
<script src="/assets/weather.js" defer></script>
</body>
</html>
"""


def build_index_page(section_title: str, entries: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'  <li><a href="{href}"><span class="num">{i}</span> {label}</a></li>'
        for i, (href, label) in enumerate(entries, start=1)
    )
    return f'<h1>{section_title}</h1>\n<ul class="pillar-grid">\n{items}\n</ul>\n'


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    md = markdown.Markdown(extensions=["tables", "sane_lists"])

    for src_rel, out_rel in PAGES:
        src_path = ROOT / src_rel
        out_path = SITE / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        raw = src_path.read_text(encoding="utf-8")
        raw = rewrite_links(raw)
        md.reset()
        body_html = md.convert(raw)
        title = page_title(body_html, fallback=out_rel)
        out_path.write_text(render_page(title, body_html, out_path), encoding="utf-8")
        print(f"built {out_rel}")

    # Simple hand-built index pages for the two section landing URLs referenced in nav
    learn_entries = [
        (LINK_MAP[Path(src).name], page_title(md.convert(rewrite_links((ROOT / src).read_text(encoding="utf-8"))), src))
        for src, _ in PAGES if src.startswith("articles/0")
    ]
    (SITE / "learn").mkdir(parents=True, exist_ok=True)
    (SITE / "learn" / "index.html").write_text(
        render_page("Learn", build_index_page("Learn", learn_entries), SITE / "learn" / "index.html"),
        encoding="utf-8",
    )
    print("built learn/index.html")

    tools_entries = [
        (LINK_MAP[Path(src).name], page_title(md.convert(rewrite_links((ROOT / src).read_text(encoding="utf-8"))), src))
        for src, _ in PAGES if src.startswith("tools/")
    ]
    (SITE / "tools").mkdir(parents=True, exist_ok=True)
    (SITE / "tools" / "index.html").write_text(
        render_page("Tools & Templates", build_index_page("Tools & Templates", tools_entries), SITE / "tools" / "index.html"),
        encoding="utf-8",
    )
    print("built tools/index.html")

    # Assets
    shutil.copytree(ROOT / "assets", SITE / "assets", dirs_exist_ok=True)
    print("copied assets/ (style.css + photos/)")

    # Custom domain for GitHub Pages
    (SITE / "CNAME").write_text("ainatotable.com\n", encoding="utf-8")
    print("wrote CNAME (ainatotable.com)")

    print(f"\nSite built at {SITE}")


if __name__ == "__main__":
    main()
