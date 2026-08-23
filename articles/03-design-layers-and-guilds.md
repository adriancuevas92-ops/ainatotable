# Design: The Layers & Guilds

Once you've mapped your site (see [Planning Your Site](02-planning-your-site.md)), design starts from the top down. Work through each layer in order, canopy first, and ask the same two questions at every layer: what do I want to harvest from here, and what does it need from its neighbors to thrive?

<div class="diagram-wrap">
<svg viewBox="0 0 900 450" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cross-section diagram of the seven food forest layers, from canopy at top to root and vine below and around it">

<rect class="layer-canopy" x="0" y="0" width="900" height="90"/>
<rect class="layer-understory" x="0" y="90" width="900" height="75"/>
<rect class="layer-shrub" x="0" y="165" width="900" height="65"/>
<rect class="layer-herb" x="0" y="230" width="900" height="55"/>
<rect class="layer-ground" x="0" y="285" width="900" height="40"/>
<rect class="layer-soil" x="0" y="325" width="900" height="25"/>
<rect class="layer-root" x="0" y="350" width="900" height="100"/>

<g>
  <rect x="376" y="62" width="8" height="24" fill="rgba(255,255,255,0.45)"/>
  <circle class="diagram-icon solid" cx="380" cy="42" r="27"/>
  <rect x="556" y="66" width="8" height="20" fill="rgba(255,255,255,0.45)"/>
  <circle class="diagram-icon solid" cx="560" cy="44" r="24"/>
  <rect x="736" y="58" width="8" height="28" fill="rgba(255,255,255,0.45)"/>
  <circle class="diagram-icon solid" cx="740" cy="38" r="30"/>
</g>

<g>
  <rect x="336" y="148" width="7" height="16" fill="rgba(255,255,255,0.4)"/>
  <circle class="diagram-icon solid" cx="340" cy="132" r="19"/>
  <rect x="516" y="150" width="7" height="14" fill="rgba(255,255,255,0.4)"/>
  <circle class="diagram-icon solid" cx="520" cy="135" r="17"/>
  <rect x="696" y="146" width="7" height="18" fill="rgba(255,255,255,0.4)"/>
  <circle class="diagram-icon solid" cx="700" cy="128" r="21"/>
</g>

<g>
  <circle class="diagram-icon solid" cx="348" cy="212" r="11"/>
  <circle class="diagram-icon solid" cx="372" cy="216" r="11"/>
  <circle class="diagram-icon solid" cx="360" cy="200" r="11"/>
  <circle class="diagram-icon solid" cx="528" cy="212" r="11"/>
  <circle class="diagram-icon solid" cx="552" cy="216" r="11"/>
  <circle class="diagram-icon solid" cx="540" cy="200" r="11"/>
  <circle class="diagram-icon solid" cx="708" cy="212" r="11"/>
  <circle class="diagram-icon solid" cx="732" cy="216" r="11"/>
  <circle class="diagram-icon solid" cx="720" cy="200" r="11"/>
</g>

<g>
  <ellipse class="diagram-icon solid" cx="360" cy="262" rx="16" ry="7" transform="rotate(-25 360 262)"/>
  <ellipse class="diagram-icon solid" cx="386" cy="266" rx="16" ry="7" transform="rotate(20 386 266)"/>
  <ellipse class="diagram-icon solid" cx="540" cy="262" rx="16" ry="7" transform="rotate(-25 540 262)"/>
  <ellipse class="diagram-icon solid" cx="566" cy="266" rx="16" ry="7" transform="rotate(20 566 266)"/>
  <ellipse class="diagram-icon solid" cx="720" cy="262" rx="16" ry="7" transform="rotate(-25 720 262)"/>
  <ellipse class="diagram-icon solid" cx="746" cy="266" rx="16" ry="7" transform="rotate(20 746 266)"/>
</g>

<path class="diagram-icon" d="M 300 313 Q 340 302 380 313 T 460 313 T 540 313 T 620 313 T 700 313 T 780 313" />

<g>
  <path class="diagram-icon" d="M 380 350 C 378 364, 382 372, 380 384" />
  <path class="diagram-icon" d="M 380 384 C 366 394, 358 406, 348 422" />
  <path class="diagram-icon" d="M 380 384 C 394 393, 401 404, 408 420" />
  <path class="diagram-icon" d="M 380 384 C 379 398, 377 410, 373 428" />
  <path class="diagram-icon" d="M 740 350 C 739 362, 742 368, 740 378" />
  <path class="diagram-icon" d="M 740 378 C 728 388, 720 398, 712 412" />
  <path class="diagram-icon" d="M 740 378 C 751 387, 758 397, 766 410" />
  <ellipse class="diagram-icon solid" cx="560" cy="400" rx="22" ry="16"/>
  <path class="diagram-icon" d="M 560 416 C 556 424, 552 430, 548 438" />
  <path class="diagram-icon" d="M 560 416 C 560 425, 560 432, 560 440" />
  <path class="diagram-icon" d="M 560 416 C 564 424, 568 430, 573 437" />
</g>

<path class="diagram-vine" d="M 830 345 C 790 305, 862 255, 826 210 C 790 168, 866 122, 828 78 C 806 52, 832 30, 822 12" />
<circle class="diagram-vine-leaf" cx="822" cy="245" r="6"/>
<circle class="diagram-vine-leaf" cx="850" cy="180" r="6"/>
<circle class="diagram-vine-leaf" cx="812" cy="100" r="6"/>
<text class="diagram-vine-label" x="836" y="20">VINE</text>

<text class="diagram-label" x="24" y="40">Canopy</text>
<text class="diagram-sublabel" x="24" y="62">Full-size fruit &amp; nut trees</text>

<text class="diagram-label" x="24" y="122">Understory</text>
<text class="diagram-sublabel" x="24" y="144">Smaller trees, filling canopy gaps</text>

<text class="diagram-label" x="24" y="193">Shrub</text>
<text class="diagram-sublabel" x="24" y="213">Berries &amp; shrub-scale crops</text>

<text class="diagram-label" x="24" y="264" style="font-size:20px;">Herbaceous</text>

<text class="diagram-label" x="24" y="311" style="font-size:19px;">Groundcover</text>

<text class="diagram-sublabel" x="450" y="341" text-anchor="middle" style="font-weight:700; letter-spacing:0.08em;">GROUND LEVEL</text>

<text class="diagram-label" x="24" y="395">Root</text>
<text class="diagram-sublabel" x="24" y="417">Underground crops — kalo lives here</text>

</svg>
</div>

## The seven layers

1. **Canopy** — the tallest trees, forming the top of the system. Full-size fruit and nut trees go here.
2. **Understory** — smaller or dwarf trees that fill the gaps the canopy leaves open, taking advantage of partial shade.
3. **Shrub** — berries and shrub-scale food plants, filling the space below the trees.
4. **Herbaceous** — perennial vegetables and herbs, non-woody, filling in at ground level and slightly above.
5. **Groundcover** — low, spreading plants that cover bare soil, hold moisture, and crowd out weeds so you largely don't have to.
6. **Root** — crops growing underground, using space nothing else is using.
7. **Vine** — climbers that use the vertical space on trunks and structures rather than needing their own.

Each layer is a distinct planning decision. A common beginner mistake is planting the canopy and calling it done — a food forest with only a canopy layer is an orchard, not a food forest. The other six layers are what make the system self-sustaining rather than just a collection of fruit trees.

## What a guild actually is

A guild is a small group of plants placed together on purpose because they help each other. The classic version has a few common roles:

- A **nitrogen fixer** (often a legume tree or shrub) that pulls nitrogen from the air into the soil, feeding everything planted near it
- A **nutrient accumulator** — a deep-rooted plant that pulls minerals up from lower in the soil where shallower-rooted plants can't reach
- A **pest deterrent or pollinator draw** — something aromatic or flowering that either confuses pests looking for your food crop, or brings in the insects that pollinate it
- The **food-producing plant** itself, which is the actual point of the guild — everything else exists to support it

You don't need every role filled to get value from grouping plants this way. Even a simple pairing — a fruit tree with a nitrogen-fixing shrub planted near its base — is a real guild and a real improvement over planting the fruit tree alone.

## A worked example: Hawaiʻi, wet-tropical

This is drawn from real, already-producing planting in South Kona, not a textbook example:

- **Canopy:** breadfruit or citrus
- **Understory:** banana, which tolerates the partial shade under a canopy tree well
- **Shrub:** coffee, which does well in dappled light
- **Herbaceous / root:** kalo (taro) and ʻōlena (turmeric) — both real, currently producing crops on the reference site this content is drawn from
- **Groundcover:** sweet potato, which spreads to cover soil while also producing a harvest
- **Vine:** passionfruit, trained up a canopy tree's trunk rather than a separate structure

That's a functioning guild stack in a single vertical footprint — six layers, each producing something, each placed with a reason.

## Clear before you plant

On a site with existing invasive growth, design and clearing happen together, not in sequence — you generally can't tell what a piece of ground is actually capable of until the invasives are out. Guinea grass, Christmas berry, Cat's claw, and similar aggressive invasive species common in Hawaiʻi will outcompete a young planting before it has a chance to establish. Real example: the South Kona site this content draws from cleared Guinea Grass, Maile Pilau, Cat's Claw, and Christmas Berry before kalo, ʻōlena, and koa went in — the clearing wasn't a side task, it was the first phase of the design.

## Next

Once the layer plan and a first guild or two are sketched onto your site map, the next real question is what the ground underneath all of it needs — see [Soil, Water & Establishment](04-soil-water-and-establishment.md).
