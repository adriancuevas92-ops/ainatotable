#!/usr/bin/env python3
"""Generate the favicon / app-icon / social-share image set from the site's
own retired symbol mark, in the two brand accent colours.

This closes the one open item [[2026-11-07 - Symbol Eliminated; Wordmark-Only
Going Forward]] itself logged as "owed": a wordmark does not compress to a
16px tab icon, and nothing was ever built to fill that gap. This does NOT
revive the mark in the nav lockup or reverse that decision -- the mark still
appears nowhere in the page content build.py produces, only in these
standalone icon files.

The mark geometry is copied from MARK in build.py (the same masked five-petal
path data) rather than imported, because a favicon/OG image needs literal
hex colours baked in -- it has no CSS, no custom properties, no page context
-- while build.py's own copy stays a currentColor glyph for any future
in-page use. If the geometry ever changes, change it in both places; a
comment is left in each pointing at the other.

Renders through actual Chrome (already a build-verification dependency on
this project, not a new one) rather than adding an SVG-rasterizing library:
write a standalone HTML page sized to exactly the output's pixel dimensions,
screenshot it with a transparent background, and that screenshot IS the
output file -- no cropping, no separate crop step to get wrong.

Run:  python3 -I tools/make_icons.py
Output: images/icons/favicon.svg, favicon-16.png, favicon-32.png,
        apple-touch-icon.png (180x180), og-image.png (1200x630)
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

# GREEN/BLUE are the mark's own merch colours (round five, "I want to use
# those colors on branded merch") -- a separate, explicit decision from the
# site's own screen palette in tokens.css, deliberately NOT tied to it, so
# they don't change just because tokens.css does.
GREEN = "#008F63"
BLUE = "#0B5ED7"
# PAGE/HEADER_GREEN DO represent the site's own current screen branding (the
# OG-image is a preview of the site itself) -- kept in sync with tokens.css
# --page / --brand-green. Institutional-green palette, 2026-11-22.
PAGE = "#FFFFFF"
HEADER_GREEN = "#407A52"

VIEWBOX = "-1.2199 -1.2859 2.484 2.484"
MASK_RECT = '<rect x="-1.2199" y="-1.2859" width="2.484" height="2.484" fill="#fff"/>'
MASK_PATHS = (
    '<path d="M-0.0047,-0.0246 0.4131,-1.1892 0.6828,-1.0577 0.0222,-0.0114Z" fill="#000"/>'
    '<path d="M0.0219,-0.0121 1.2587,0.0254 1.217,0.3225 0.0177,0.0176Z" fill="#000"/>'
    '<path d="M0.0182,0.0171 0.3648,1.205 0.0693,1.2571 -0.0113,0.0223Z" fill="#000"/>'
    '<path d="M-0.0106,0.0226 -1.0333,0.7193 -1.1741,0.4544 -0.0247,-0.0039Z" fill="#000"/>'
    '<path d="M-0.0248,-0.0031 -1.0034,-0.7604 -0.795,-0.9762 -0.004,-0.0247Z" fill="#000"/>'
)
# Same 3-green/2-blue petal split, stem+dot blue, considered for the nav
# lockup revival this round and NOT used there -- used here instead, where
# a fixed two-colour mark is exactly what a merch-bound icon needs.
PETALS = [
    (GREEN, "M0,0C-0.1817,-0.2787 -0.4728,-0.6002 -0.3227,-0.9063C-0.2124,-1.1329 0.1666,-1.1998 0.3478,-1.0246C0.4163,-0.757 0.1463,-0.3365 0,0Z"),
    (BLUE, "M0,0C0.2089,-0.2589 0.4247,-0.6351 0.7623,-0.587C1.0119,-0.5521 1.1925,-0.2123 1.0819,0.0141C0.8486,0.162 0.3652,0.0351 0,0Z"),
    (GREEN, "M-0,0C0.3108,0.1187 0.7353,0.2077 0.7938,0.5436C0.8377,0.7917 0.5704,1.0685 0.3209,1.0333C0.1082,0.8571 0.0794,0.3582 -0,0Z"),
    (BLUE, "M0,-0C-0.0168,0.3322 0.0297,0.7635 -0.2717,0.9229C-0.4941,1.0414 -0.84,0.8727 -0.8836,0.6245C-0.7817,0.3677 -0.3161,0.1863 0,-0Z"),
    (GREEN, "M0,0C-0.3212,0.0866 -0.7169,0.2642 -0.9617,0.0268C-1.1431,-0.1481 -1.0896,-0.5292 -0.8669,-0.6474C-0.5913,-0.6298 -0.2748,-0.2431 0,0Z"),
]
STEM = (BLUE, "M-0.0507,-0.0342 0.4378,-0.7585 0.5392,-0.69 0.0507,0.0342Z")
DOT = (BLUE, None)  # ellipse, handled separately


def mark_svg(mask_id="mki"):
    petals = "".join(f'<path fill="{c}" d="{d}"/>' for c, d in PETALS)
    return (
        f'<svg viewBox="{VIEWBOX}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><mask id="{mask_id}" maskUnits="userSpaceOnUse" x="-1.2199" y="-1.2859" width="2.484" height="2.484">'
        f'{MASK_RECT}{MASK_PATHS}</mask></defs>'
        f'<g><g mask="url(#{mask_id})">{petals}</g>'
        f'<path fill="{STEM[0]}" d="{STEM[1]}"/>'
        f'<ellipse fill="{BLUE}" cx="0.5386" cy="-0.7985" rx="0.135" ry="0.1242"/>'
        f'</g></svg>'
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


def icon_html(size, pad_frac=0.14):
    """A square page, mark centered with a small margin, background
    transparent so it reads correctly on both light and dark OS chrome."""
    pad = round(size * pad_frac)
    inner = size - 2 * pad
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;width:{size}px;height:{size}px;background:transparent}}
  .wrap{{width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;box-sizing:border-box;padding:{pad}px}}
  svg{{width:{inner}px;height:{inner}px;display:block}}
</style></head><body><div class="wrap">{mark_svg()}</div></body></html>"""


def og_html():
    w, h = 1200, 630
    mark_size = 220
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;width:{w}px;height:{h}px;background:{PAGE};
    font-family:Georgia,"Noto Serif",serif}}
  .wrap{{width:{w}px;height:{h}px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:28px;box-sizing:border-box}}
  svg{{width:{mark_size}px;height:{mark_size}px;display:block}}
  h1{{margin:0;font-size:56px;color:{HEADER_GREEN};font-weight:700}}
  p{{margin:0;font-family:Arial,sans-serif;font-size:24px;color:#53606A}}
</style></head><body><div class="wrap">{mark_svg("mkog")}
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
    # verifying it would be worse than not claiming it.
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
