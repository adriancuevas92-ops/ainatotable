# Find Farms, Markets & Food Nonprofits Near You

If you run a restaurant, market, or kitchen on Hawaiʻi Island, this tool shows you what's actually near you — small farms you could source from, farmers markets you could buy or sell at, and nonprofits with a real, stated mission of getting fresh, local food to people. Not just us. We built it for the same reason we built everything else on this site: understanding where the friction actually is, and easing it, isn't something we think should be limited to our own supply chain.

<div class="proximity-band" id="proximityFinder">
  <div class="proximity-head">
    <h3>Find what's near you</h3>
    <p class="proximity-sub">Enter your address to see distances to verified farms, farmers markets, and food-access nonprofits on Hawaiʻi Island.</p>
  </div>

  <form id="proximityForm" class="proximity-form">
    <label for="proximityAddress">Your address</label>
    <input type="text" id="proximityAddress" name="address" placeholder="e.g. 123 Ali'i Dr, Kailua-Kona, HI" autocomplete="off">
    <button type="submit" class="btn">Find what's nearby</button>
  </form>

  <p class="proximity-status" id="proximityStatus" hidden></p>
  <div class="proximity-results" id="proximityResults" hidden></div>

  <p class="proximity-credit">Address lookup via <a href="https://nominatim.openstreetmap.org/" target="_blank" rel="noopener">OpenStreetMap</a>. Nothing you enter is stored — the lookup happens in your browser, not on our servers. Distances shown are straight-line, not driving distance — a quick way to compare "closer" vs. "farther," not a promise of how long the drive actually takes.</p>
</div>

## What this is, honestly

A short, real list — not a directory. Each entry was verified directly (a real address, geocoded from official sources, a real description of what they actually do) rather than pulled from a database and trusted blindly. That's a deliberate choice: a longer list that includes anything vaguely food-adjacent would be less useful than a short one you can actually trust.

Right now that means nine entries:

- **Farms** — [Ola Mahina Gardens at Kealaola Farm](https://www.kealaolafarm.com/) (organic produce, greens, coffee), [Mermaid Mushrooms](https://www.bigislandlocavorestore.com/suppliers/mermaid-mushrooms) (gourmet mushrooms), [Greenwell Farms](https://www.greenwellfarms.com/) and [Rooster Farms](https://www.roosterfarmshop.com/) (both coffee — genuinely useful if you're sourcing for a café, not for produce)
- **Farmers markets** — South Kona Green Market (Sundays, Captain Cook), South Kona Fruit Stand (a stand, not a vendor market), Keauhou Farmers Market (Saturdays, Kailua-Kona)
- **Nonprofits** — [The Food Basket](https://www.hawaiifoodbasket.org/) (Hawaiʻi Island's food bank), [Family Support Hawaiʻi](https://familysupporthawaii.org/) (farm-to-early-childhood food access), [Kohala Food Hub](https://www.kohalafoodhub.com/) (regional food-system infrastructure)

More will be added as they're verified the same way — this list grows slowly and honestly, not all at once.

## Why we built this instead of keeping it to ourselves

Because the actual mission isn't "route more business to ʻĀina to Table" — it's closing the gap between the people growing food and the people cooking it, for the whole area, not just for us. A tool like this costs us very little to build and give away, and if it helps a restaurant find a real farm, market, or community partner nearby, that's worth more than keeping it proprietary. If you know of a real, mission-driven farm, market, or organization that should be on this list, [tell us](mailto:hello@ainatotable.com).
