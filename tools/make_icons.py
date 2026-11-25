#!/usr/bin/env python3
"""Generate the favicon / app-icon / social-share image set for ʻĀina to
Table.

Reversed 2026-11-25: round five (2026-11-22) had revived the retired
five-petal mark ([[2026-11-07 - Symbol Eliminated; Wordmark-Only Going
Forward]]) as a two-tone icon specifically to fill this gap, with Adrian's
direct go-ahead at the time ("yes, build a two-tone favicon/icon"). Adrian,
2026-11-25: seeing it live in his own browser tabs, he asked for "the
remnants of the old logo" gone. That reverses the round-five approval, not
the Nov 7 one -- the mark was never revived in the nav lockup and still
isn't. This file no longer references the mark geometry at all; see
build.py's own MARK constant for the retired asset's continued provenance
record (still kept there, still unused).

The replacement is a plain typographic monogram -- "Ā" (U+0100, the same
kahakō-bearing letter the wordmark itself opens with, not a plain "A") in
white on the site's one locked identity colour, HEADER_GREEN. This is the
literal "the name is the feature instead of a logo" decision applied to the
one surface a wordmark can't reach on its own: a 16px tab icon has no room
for "ʻĀina to Table" as a string, but it has room for the ʻokina-bearing
letter the name itself starts with.

Renders through actual Chrome (already a build-verification dependency on
this project, not a new one) rather than adding an SVG-rasterizing library:
write a standalone HTML page sized to exactly the output's pixel dimensions,
screenshot it with a transparent background, and that screenshot IS the
output file -- no cropping, no separate crop step to get wrong.

Run:  python3 -I tools/make_icons.py
Output: images/icons/favicon.svg, favicon-16.png, favicon-32.png,
        apple-touch-icon.png (180x180), icon-192.png, icon-512.png,
        og-image.png (1200x630), site.webmanifest
These are committed, build artefacts of a design decision -- not generated
by build.py itself, the same way data/ is refreshed by its own script and
then committed rather than rebuilt on every run.
"""
import os
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "icons")

# The site's one locked identity colour (institutional-green palette,
# 2026-11-22) -- kept in sync with tokens.css --brand-green deliberately,
# since this monogram IS the current screen branding, not a separate merch
# treatment the old two-tone mark was.
PAGE = "#FFFFFF"
HEADER_GREEN = "#407A52"
LETTER = "Ā"  # LATIN CAPITAL LETTER A WITH MACRON -- the exact letter
# ʻĀina to Table's own wordmark starts with, written as a literal codepoint
# rather than typed, per the vault's diacritical hard rule. Matches the same
# &#256; (decimal 256 = 0x100) og_html below and build.py's own wordmark use.


def mark_svg():
    """A solid HEADER_GREEN square (no corner radius -- iOS/Android apply
    their own masking, and a favicon tab reads fine square) with the single
    monogram letter centered, in a serif face matching the site's own Noto
    Serif role. Full-bleed, self-contained, scales to any output size."""
    return (
        '<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="32" height="32" fill="{HEADER_GREEN}"/>'
        '<text x="16" y="23" text-anchor="middle" '
        'font-family="Georgia, \'Noto Serif\', serif" font-weight="700" '
        f'font-size="20" fill="#FFFFFF">{LETTER}</text>'
        '</svg>'
    )


def render_png(html, width, height, out_path, transparent=True):
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "render.html")
        with open(html_path, "w") as f:
            f.write(html)
        cmd = [
            "google-chrome", "--headless", "--disable-gpu",
            f"--window-size={width},{height}",
            "--virtual-time-budget=1000",
            f"--screenshot={out_path}",
        ]
        if transparent:
            cmd.append("--default-background-color=00000000")
        cmd.append(f"file://{html_path}")
        subprocess.run(cmd, check=True, capture_output=True)


def icon_html(size):
    """A square page exactly the output's own pixel size, the monogram SVG
    filling it completely -- no padding, since the square fill IS the icon,
    not a mark floating on a separate background."""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;width:{size}px;height:{size}px;background:transparent}}
  svg{{display:block;width:{size}px;height:{size}px}}
</style></head><body>{mark_svg()}</body></html>"""


def og_html():
    """Purely typographic -- no monogram here either. The wordmark itself,
    at full size, is the social-share image; this is the same "name is the
    feature" decision applied to the one other surface that used to carry
    the retired mark."""
    w, h = 1200, 630
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;width:{w}px;height:{h}px;background:{PAGE};
    font-family:Georgia,"Noto Serif",serif}}
  .wrap{{width:{w}px;height:{h}px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:28px;box-sizing:border-box}}
  .bar{{width:72px;height:6px;background:{HEADER_GREEN}}}
  h1{{margin:0;font-size:64px;color:{HEADER_GREEN};font-weight:700}}
  p{{margin:0;font-family:Arial,sans-serif;font-size:24px;color:#53606A}}
</style></head><body><div class="wrap"><div class="bar"></div>
  <h1>&#699;&#256;ina to Table</h1>
  <p>A network for ingredients you can trace to the ground they came out of.</p>
</div></body></html>"""


def main():
    os.makedirs(OUT, exist_ok=True)

    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write(mark_svg())
    print("wrote favicon.svg")

    for size, name in [(16, "favicon-16.png"), (32, "favicon-32.png"), (180, "apple-touch-icon.png"),
                       (192, "icon-192.png"), (512, "icon-512.png")]:
        render_png(icon_html(size), size, size, os.path.join(OUT, name))
        print(f"wrote {name} ({size}x{size})")

    render_png(og_html(), 1200, 630, os.path.join(OUT, "og-image.png"), transparent=False)
    print("wrote og-image.png (1200x630)")

    # Round-six panel, 2026-11-22: round five built the icon FILES but never
    # the manifest that makes them actually function as an "app icon" on
    # Android -- apple-touch-icon alone covers iOS home-screen bookmarking,
    # but Android's "add to home screen" reads a web manifest for its icon,
    # name and theme colour, and nothing pointed it at one. 192/512 are the
    # two sizes a manifest is expected to offer. purpose "any" only, not
    # "maskable" -- a maskable icon needs a safe-zone padding rule this
    # glyph was never designed against, and claiming that support without
    # verifying it would be worse than not claiming it. Unaffected by the
    # 2026-11-25 monogram swap -- still true of the new icon.
    import json
    manifest = {
        "name": "ʻĀina to Table",
        "short_name": "ʻĀina to Table",
        "start_url": "/",
        "display": "standalone",
        "background_color": PAGE,
        "theme_color": PAGE,
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    with open(os.path.join(OUT, "site.webmanifest"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print("wrote site.webmanifest")


if __name__ == "__main__":
    if shutil.which("google-chrome") is None:
        raise SystemExit("google-chrome not found on PATH -- required to rasterize icons")
    main()
