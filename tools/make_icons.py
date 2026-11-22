#!/usr/bin/env python3
"""Generate the favicon / app-icon / social-share image set as a plain text
monogram -- no pictorial mark.

Retires the site's former five-petal "plant" symbol entirely. Adrian,
2026-11-22, after the favicon/app-icon work shipped (round five/six): "the
plant symbol/logo needs to be retired entirely, it's not on brand. I don't
see it on the page itself anymore but now see it in the tab description on
a chrome browser." The mark was never revived in the page content -- only
in these standalone icon files -- and this file is now the only place it
existed at all; it's deleted outright, not just unused, the same way
--accent-bright was deleted from tokens.css rather than left dead.

Checked jpmorgan.com's own actual favicon before designing a replacement
(downloaded it directly: a flat "JPM" text monogram, solid fill, no
pictorial symbol) rather than guessing at what "on brand" should look like.
This follows the same pattern: a solid --brand-green square, the single
letter "Ā" (the wordmark's own most distinctive character, carrying
the macron this brand's identity already turns on) in white Noto Serif
Bold, centred. Still answers the original, still-standing need from
[[2026-11-07 - Symbol Eliminated; Wordmark-Only Going Forward]] (a square
icon a wordmark alone can't fill) without reviving a symbol that decision
retired.

Renders through actual Chrome (already a build-verification dependency on
this project, not a new one) rather than adding an SVG-rasterizing library:
write a standalone HTML page sized to exactly the output's pixel
dimensions, screenshot it, and that screenshot IS the output file.

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
FONT_PATH = os.path.join(ROOT, "fonts", "NotoSerif-700.woff2")

# Kept in sync with tokens.css --page / --brand-green / --on-dark. These are
# the site's own current screen branding (the OG image previews the site
# itself; the monogram IS the icon), so they move when tokens.css does.
PAGE = "#FFFFFF"
BRAND_GREEN = "#407A52"
ON_DARK = "#F2F5F1"
MONOGRAM_LETTER = "Ā"  # the macron-bearing "A" from "ʻĀina" -- the
                            # wordmark's own most distinctive character, not a
                            # generic initial picked for convenience.


def _font_face():
    return f"""@font-face{{font-family:"Noto Serif";font-weight:700;
    src:url("file://{FONT_PATH}") format("woff2")}}"""


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


def monogram_svg(size=512, corner_frac=0.18):
    """A solid --brand-green square (rounded, the same radius ratio most
    platforms apply to a square icon anyway) with the monogram letter in
    --on-dark, centred. Solid fill, not a thin mark on transparent -- the
    same reason JPMorgan's own favicon is a flat-filled "JPM" block: a
    high-contrast solid shape is what actually reads at 16px, which a
    delicate line-art mark never did either.
    """
    r = round(size * corner_frac)
    font_size = round(size * 0.62)
    return f"""<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" rx="{r}" fill="{BRAND_GREEN}"/>
  <text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle"
    font-family="Noto Serif, Georgia, serif" font-weight="700"
    font-size="{font_size}" fill="{ON_DARK}">{MONOGRAM_LETTER}</text>
</svg>"""


def icon_html(size, corner_frac=0.18):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  {_font_face()}
  html,body{{margin:0;padding:0;width:{size}px;height:{size}px;background:transparent}}
  svg{{display:block}}
</style></head><body>{monogram_svg(size, corner_frac)}</body></html>"""


def og_html():
    w, h = 1200, 630
    mono_size = 160
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  {_font_face()}
  html,body{{margin:0;padding:0;width:{w}px;height:{h}px;background:{PAGE};
    font-family:Georgia,"Noto Serif",serif}}
  .wrap{{width:{w}px;height:{h}px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:28px;box-sizing:border-box}}
  .mono{{width:{mono_size}px;height:{mono_size}px}}
  h1{{margin:0;font-size:56px;color:{BRAND_GREEN};font-weight:700}}
  p{{margin:0;font-family:Arial,sans-serif;font-size:24px;color:#53606A}}
</style></head><body><div class="wrap"><div class="mono">{monogram_svg(mono_size)}</div>
  <h1>&#699;&#256;ina to Table</h1>
  <p>A network for ingredients you can trace to the ground they came out of.</p>
</div></body></html>"""


def main():
    os.makedirs(OUT, exist_ok=True)

    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write(monogram_svg())
    print("wrote favicon.svg")

    for size, name in [(16, "favicon-16.png"), (32, "favicon-32.png"),
                       (192, "icon-192.png"), (512, "icon-512.png")]:
        # Transparent canvas so only the rounded-rect itself is opaque --
        # otherwise the corners outside the rounded rect would fill with
        # Chrome's default background and the icon would look square again.
        render_png(icon_html(size), size, size, os.path.join(OUT, name), transparent=True)
        print(f"wrote {name} ({size}x{size})")

    # apple-touch-icon is a special case: iOS applies its own rounded-corner
    # mask and expects a full-bleed solid square to mask, not an
    # already-rounded, already-transparent-cornered icon -- corner_frac=0,
    # transparent=False.
    render_png(icon_html(180, corner_frac=0), 180, 180,
               os.path.join(OUT, "apple-touch-icon.png"), transparent=False)
    print("wrote apple-touch-icon.png (180x180)")

    render_png(og_html(), 1200, 630, os.path.join(OUT, "og-image.png"), transparent=False)
    print("wrote og-image.png (1200x630)")

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
