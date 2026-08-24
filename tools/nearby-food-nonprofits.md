# Find Nearby Food-Access Nonprofits

If you run a restaurant, market, or kitchen on Hawaiʻi Island, this tool shows you which nonprofits with a real, stated mission of getting fresh, local food to people are closest to you — not just us. We built it for the same reason we built everything else on this site: understanding where the friction actually is, and easing it, isn't something we think should be limited to our own supply chain.

<div class="proximity-band" id="proximityFinder">
  <div class="proximity-head">
    <h3>Find nonprofits near you</h3>
    <p class="proximity-sub">Enter your address to see distances to verified food-access organizations on Hawaiʻi Island.</p>
  </div>

  <form id="proximityForm" class="proximity-form">
    <label for="proximityAddress">Your address</label>
    <input type="text" id="proximityAddress" name="address" placeholder="e.g. 123 Ali'i Dr, Kailua-Kona, HI" autocomplete="off">
    <button type="submit" class="btn">Find nearby nonprofits</button>
  </form>

  <p class="proximity-status" id="proximityStatus" hidden></p>
  <div class="proximity-results" id="proximityResults" hidden></div>

  <p class="proximity-credit">Address lookup via <a href="https://nominatim.openstreetmap.org/" target="_blank" rel="noopener">OpenStreetMap</a>. Nothing you enter is stored — the lookup happens in your browser, not on our servers. Distances shown are straight-line, not driving distance — a quick way to compare "closer" vs. "farther," not a promise of how long the drive actually takes.</p>
</div>

## What this is, honestly

A short, real list — not a directory. Each entry was verified directly (a real mission statement, a real address, geocoded from official sources) rather than pulled from a database and trusted blindly. That's a deliberate choice: a longer list that includes anything vaguely food-adjacent would be less useful than a short one you can actually trust.

Right now that means three organizations: [The Food Basket](https://www.hawaiifoodbasket.org/) (Hawaiʻi Island's food bank, running the DA BOX fresh-produce CSA program), [Family Support Hawaiʻi](https://familysupporthawaii.org/) (farm-to-early-childhood food access across West Hawaiʻi), and [Kohala Food Hub](https://www.kohalafoodhub.com/) (regional food-system infrastructure in North Kohala). More will be added here as they're verified the same way — this list grows slowly and honestly, not all at once.

## Why we built this instead of keeping it to ourselves

Because the actual mission isn't "route more business to ʻĀina to Table" — it's closing the gap between the people growing food and the people cooking it, for the whole area, not just for us. A tool like this costs us very little to build and give away, and if it helps a restaurant find a real community partner nearby — someone doing meaningful work on food access — that's worth more than keeping it proprietary. If you know of a real, mission-driven organization that should be on this list, [tell us](mailto:hello@ainatotable.com).
