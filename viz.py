"""Build-time SVG visualizations for the ʻĀina to Table public surface.

No client-side charting library, no new dependency -- every shape here is
computed once, at build time, from data already in rows()/price_chart_rows(),
the same way the retired MARK constant in build.py was always a hand-built
inline SVG rather than an image asset.

Split into its own module per the round-one VFX/web-design panel's
front-end-engineer seat (2026-11-22): the risk named wasn't any single
visualization, it was accumulating enough ad hoc SVG-generation logic inside
one already-2100-line build.py that it stops being the single auditable file
it currently is. Everything that computes a <svg> string lives here instead.

Colours are never hard-coded: every fill references a CSS custom property
(var(--line), var(--brand-green)), the same discipline tokens.css already
holds every other colour to, so a future palette change recolours these
shapes automatically instead of needing a second edit here.
"""


def range_bar_svg(lo, hi, value, width=120, height=14):
    """A horizontal bar from lo to hi with a tick at value's position.

    Purely decorative and supplementary -- the exact numbers already ship as
    text right next to every bar this draws, so this never becomes the only
    place a reader could get the figure from (the same "colour never carries
    meaning alone" rule tokens.css states for chips applies here too).
    aria-hidden because of that: a screen reader already has the real numbers
    in the adjacent text and gains nothing from a second, harder read of the
    same fact as a shape.
    """
    if hi <= lo:
        frac = 0.5
    else:
        frac = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    tick_w = 3
    tick_x = frac * (width - tick_w)
    track_y = height / 2 - 2
    # Institutional-green palette, 2026-11-22: Adrian, "bring everything into
    # the new color palette." The blue track (round five, built specifically
    # for the merch-colors ask) is retired from screen UI -- the merch icon
    # itself is untouched, a separate asset for a separate physical purpose,
    # but this bar is part of the site's own screen tone, which is what's
    # being brought into line here. Back to a neutral track (--line) with a
    # single confident tick (--brand-green) -- the track and the tick need
    # to read as two different things (the range vs. the one point inside
    # it that matters), and two shades of one green would have blurred that
    # distinction right as the tick became the exact same brand colour used
    # everywhere else on the page.
    return (
        f'<svg class="range-bar" viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" aria-hidden="true" focusable="false">'
        f'<rect x="0" y="{track_y:.1f}" width="{width}" height="4" rx="2" '
        f'fill="var(--line)"/>'
        f'<rect x="{tick_x:.1f}" y="0" width="{tick_w}" height="{height}" rx="1.5" '
        f'fill="var(--brand-green)"/>'
        f'</svg>'
    )


def span_bar_svg(lo, hi, width=120, height=14):
    """A plain lo-to-hi bar, no tick.

    Round-two VFX/web-design panel (2026-11-22): checked the actual mart
    before building this -- product pages' "What Los Angeles paid" carries
    only a single report's lo/hi (or one figure, when lo == hi), never a
    separate "latest" point distinct from that range the way Market's
    multi-year county data does. range_bar_svg's tick exists to mark a real
    third data point; faking one here (e.g. at the midpoint) would draw a
    position the data never reported. This shape draws only what the data
    actually contains: the width of the spread, nothing else. Call only
    when hi > lo -- a single reported price has no spread to show.
    """
    track_y = height / 2 - 2
    return (
        f'<svg class="range-bar" viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" aria-hidden="true" focusable="false">'
        f'<rect x="0" y="{track_y:.1f}" width="{width}" height="4" rx="2" '
        f'fill="var(--brand-green)"/>'
        f'</svg>'
    )
