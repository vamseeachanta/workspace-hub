---
name: lodging-selection
description: Use when recommending lodging inside a trip plan. Encodes the hotel-vs-Airbnb decision matrix, walk-distance gates, never-fabricate-listings rule, and the specific search-criteria template for Airbnb/Vrbo entries. Invoked by trip-planner.
type: reference
---

# lodging-selection

Choosing where to sleep is the most decision-heavy part of trip planning. This skill encodes the rules that prevent the common mistakes (random Airbnb in the wrong neighborhood, named hotel that's three years closed, listing IDs invented from thin air).

## Hotel vs Airbnb decision matrix

| Use a hotel when… | Use an Airbnb / Vrbo when… |
|---|---|
| First night of an international trip (jet lag) | Stay is ≥ 2 nights at a single base |
| Single-night transit stop | Family ≥ 4 people (rooms get tight, kitchen helps) |
| Traveling with elderly / mobility-limited family | Restaurant prices are 2× US (Switzerland, Norway, Iceland) |
| You need late check-in flex / luggage storage | A specific neighborhood matters more than amenities |
| Total stay ≤ 1 night | You want a balcony / view / specific feature |
| Business component (need front-desk billing) | Pet-friendly is required |

**Default for a 1-week international trip:** 1 hotel (jet-lag arrival) + 2 Airbnbs (mountain/region bases). This was #68's pattern.
**Default for a domestic cabin trip:** 1 cabin/Airbnb the whole time (#41 pattern).
**Default for a weekend trip:** 1 hotel — no need to set up an Airbnb for a single night.

## Walk-distance gates (load-bearing for international rail trips)

Lodging must satisfy these distance gates from the relevant transit anchor, or the trip falls apart on the move-day:

| Trip type | Gate |
|---|---|
| Train-anchored European trip | ≤ 12 min walk to the train station from the lodging |
| Airport arrival hotel | ≤ 30 min by direct transit (train/shuttle) to the airport |
| Car-free village (Zermatt, Wengen) | ≤ 12 min walk uphill or station-side |
| Beach/resort trip | ≤ 10 min walk to beach access OR has on-site beach |
| National park base | ≤ 30 min drive to the main park entrance |

If the listing fails the gate, the move-day with luggage becomes a 30-minute crisis at 7 AM. Don't accept it.

## Hard rule: never fabricate specific listings

For Airbnb / Vrbo recommendations: **describe search criteria, do NOT invent listing names or IDs.**

Listings on those platforms have churn — properties sell, owners delist, prices double seasonally. A specific Airbnb-listing recommendation in a trip plan written six months before travel is dead by the time the user clicks it.

For hotels: named-property recommendations are OK only if the property is established (5+ years, branded, or independent with strong online presence). Always provide 2–3 alternatives at different price tiers in case the top pick is unavailable.

## The Airbnb/Vrbo search-criteria template

Each Airbnb/Vrbo recommendation block must include these fields:

```markdown
### Airbnb / Vrbo #N — <Town/Region> (Day X–Y)

**Search criteria:**
- Town: **<specific towns or neighborhoods>** (rationale — why this area, not the next one over)
- Property: **N-bedroom <type>**, balcony/feature with <view>, sleeps M
- Walking distance: ≤ X min to **<load-bearing destination>** (e.g., train station, ski lift, beach access)
- Filters: kitchen, washer, elevator if applicable, pet-friendly if applicable
- Avoid: <neighborhood/feature to skip>, <a known trap like "high-floor without elevator">
- Backup search: <a fallback area + what's gained or lost>
```

The "Walking distance" line is the single most important field — it's the one that prevents the move-day crisis described above. The "Avoid" line is the second most important — it's how you encode local knowledge the user wouldn't get from a generic search.

## The hotel-recommendation template

```markdown
### Hotel — <City> (Day X–Y)

Why a hotel here: <one sentence — usually jet lag, single-night transit, or service needed>

| Property | Tier | Why |
|---|---|---|
| **<Name 1>** | Upper-mid / luxury | <why — location, family rooms, brand fit> |
| **<Name 2>** | Mid-upper | <why> |
| **<Name 3>** | Mid | <why — reliable fallback> |

Search criteria if those are full: **<neighborhood>, walkable to <transit>, family room or 2 connecting rooms, breakfast included, free cancellation through ~30 days out**.
```

Always offer 3 tiers so the user has choices, and always include the fallback search criteria so a sold-out top pick doesn't dead-end the plan.

## Filters that matter more than people think

When writing search criteria, these filters punch above their weight:

- **Free cancellation through ~30 days out** — protects against trip changes, schedule slippage, and weather pivots
- **Breakfast included** — saves 1 hr/day of "where do we eat" friction with kids
- **Elevator** — heavy bags + uphill village (Wengen, hill-town Italy) = elevator is non-negotiable
- **Kitchen** (Airbnb) — economic for ≥ 3 nights in expensive countries
- **Washer/dryer** (Airbnb) — pack lighter, multi-week trips become single-week pack
- **Walkable to local grocery** — for Airbnbs especially; lookup if Coop/Migros/etc. is within 5 min

## Region-specific lodging pitfalls

| Region | Pitfall | Fix |
|---|---|---|
| Swiss Alps | "Matterhorn view" listings where the actual Matterhorn is not visible from the unit | Verify via listing photos that the Matterhorn pyramid is visible from a window, not the lobby/balcony of another unit |
| Italian hill towns | Stairs everywhere; no elevator | Filter for elevator OR ground-floor; ask hosts about access |
| Florida beach condos | "Gulf-view" can mean partial view from the bathroom | Demand "Gulf-front" or "direct beach view" with current photos |
| Japan ryokan | Westernized rooms vs traditional tatami; bath rules vary | Read recent reviews for Western-toilet, foreign-friendly bathing |
| US national park towns | Town has 8 lodgings, all booked 9 months out | Book the moment dates are locked; consider the next town over |
| Beach destinations during hurricane season (Jun–Nov US Gulf/Atlantic) | Storms mean evacuation orders | Insist on free-cancellation policies; trip insurance |

## Domestic cabin booking-readiness workflow

Use this when the user is no longer asking for general trip planning, but is trying to choose/book a cabin with specific amenities such as kitchen, view, hot tub, pet-friendly, or child suitability.

1. **Verify exact dates and weekday labels.** Booking engines often display the authoritative check-in/check-out dates; if the user or issue body says weekday names, verify them with a date tool before repeating them.
2. **Sanity-check geography and activity proximity.** When a candidate lodging plan mentions mountains, parks, scenic drives, or day-trip attractions, verify approximate distance/travel practicality before treating them as local highlights. If a named attraction is hundreds of miles away or outside the destination cluster, correct it and substitute nearby verified activities.
3. **Named cabins are acceptable only when grounded.** For established local cabin companies with live listing pages and booking engines, specific named cabin recommendations are OK. Do not invent Airbnb/Vrbo-style listings.
3. **Separate amenity evidence from marketing copy.** For kitchen requirements, look for listing specs plus photo evidence: full kitchen, stove/oven, refrigerator, dishwasher, coffee setup, cookware, or dining table. For scenic-view requirements, inspect photos/contact sheets and identify whether the view is visible from the unit, deck, balcony, or hot tub — not just from the resort area.
4. **Translate regional view language explicitly.** In destinations like Broken Bow / Beavers Bend / Hochatown, “mountain view” may realistically mean hilltop, ridge, Ouachita forest, water, or elevated tree views. Say so, and recommend a phone confirmation before payment if the user means an unobstructed mountain panorama.
5. **Add a mountain-view-over-proximity lane when needed.** If central Broken Bow/Hochatown candidates only prove wooded/private views, widen the search to nearby ridge/mountain-view cabin clusters (for example Smithville / Talimena Scenic Byway / Ouachita foothills). Verify distances to Beavers Bend, Broken Bow Lake, and restaurants before recommending; state the tradeoff as “better verified mountain panorama, longer drive to Hochatown/park.”
6. **Report booking-readiness, not just attractiveness.** Include exact availability status, observed base price, capacity, bed/bath count, kitchen evidence, view evidence, vehicle/access constraints, cancellation/final-fee gaps, and direct listing + booking-engine URLs.
7. **Separate base-price math from all-in booking proof.** When the user gives a target such as “~$500 total for 3 nights,” compute the observed 3-night base rate, then explicitly classify whether taxes, cleaning fees, platform fees, pet fees, and cancellation terms are verified or still unknown. Do not call a lead “within budget” unless the final payable total is verified; use wording like “base rate near target; all-in likely above target after fees” when only nightly rates are known.
6. **State checkout verification level precisely.** If browser automation reaches only the availability/price page and cannot complete checkout progression, say: availability and base price were verified, but final taxes/fees/cancellation/payment constraints remain unverified. Do not imply a final payable total.
7. **When documenting in a GitHub issue, use a visual booking board.** If the user asks to document options or add pictures/actions, post one review-friendly comment with a stable marker, ranked options table, one listing-source image per option, direct listing/booking URLs, and a clear action column. Avoid burying the recommendation in narrative; make the next booking action obvious.
8. **If view/panorama is a critical criterion, add multiple view photos — not a single hero image.** Build a view-evidence board with several listing-source images per serious candidate, then classify each as: direct unit/deck/hot-tub panorama, wooded/private nature view, property/trail-only view, water view, or non-view/interior. If the primary practical option has only wooded/private views while another option has stronger panorama evidence, pause the booking recommendation and escalate to a host call before payment.
9. **Add verified phone/contact details once the decision path requires a host call.** When the next action is “call host before booking,” look up the host/company contact page or listing footer, extract the phone number from a live source, and add it to both the handoff/restart checklist and any durable issue comment. Keep the phone comment transactional: company/host, phone, which cabins/questions it covers, source URL, and the exact booking gate to verify. Do not leave a “call host” instruction without the number if the number is publicly retrievable.
11. **Treat customer-service suggestions as practical leads, not automatic winners.** If the user calls the host/company and gets a suggested property, immediately ground it in the live listing, then re-score it against the user's current top priority. If view/panorama became primary, do not let a kitchen/amenity-strong property win unless view-from-unit is verified. Convert unresolved facts into explicit pre-payment gates: view visible from cabin/deck/hot tub/window, full usable kitchen equipment, and access/driveway suitability.
12. **When the user says to review existing trip records and book, start from the durable planning record.** Inspect the existing trip issue/repo notes first, identify the current top-priority property, and convert the thread into booking gates: target dates, guest count, all-in price, cancellation cutoff, full-kitchen proof, and view-from-booked-place proof. Do not restart with generic lodging search unless the top candidate fails a gate.
13. **Split mixed destination threads before booking detail.** If the durable record contains multiple possible trips, create or reuse destination-specific issues before adding detailed lodging evidence. Keep the parent/background issue cross-linked, and put each destination’s booking board, lead candidate, alternatives, and gates in its own issue.
14. **Do not force city-proper matches when the requested view class is geographically unrealistic.** State the mismatch and widen to the nearest realistic region while preserving the user’s core criterion. Example: Austin proper is an urban/lake-view fallback, while Texas Hill Country / Canyon Lake / Wimberley / Dripping Springs are the real search zones for a Broken Bow/Ouachita-style cabin-with-views substitute.
15. **For multi-region cabin alternatives, split durable records into a parent issue plus lane children.** When the user asks to explore several substitute regions for a reference vibe, create or reuse a parent issue for the cross-region ranking and create child issues for each serious destination lane. Parent: reference filters, ranked lane table, visual board, booking gates, related issue links. Child: parent backlink, fit table, visual board, lodging-leads table, cost verdict, and next booking gates. Verify all issue links and parent comments with `gh issue view` before reporting completion.

See `references/regional-cabin-alternative-issue-trees.md` for the reusable parent/child GitHub issue pattern for Broken Bow-style regional cabin searches, including Airbnb/Vrbo search-lane handling, visual boards, and verification closeout.
See `references/ok-broken-bow-cabin-booking-2026.md` for a concrete Broken Bow cabin booking example, including multi-photo panorama evidence, contact-sheet view verification, visual issue-comment structure, Checkfront booking-readiness caveats, phone/contact closeout, and the closeout pattern for late priority inversions where panorama becomes the primary gate.
See `references/customer-service-lead-triage.md` for the reusable pattern when a host/customer-service call produces a new property lead that must still be gated before booking/payment.
See `references/achantas-data-booking-mode.md` for the achantas-data issue-tracking pattern: start from the existing trip issue, preserve the top-priority candidate, write a compact booking-readiness table with kitchen/view/pre-payment gates, and add/verify cost-estimate tables as issue comments when the user asks for pricing.

## Reference — past lodging patterns

- **#41 Beavers Bend cabins:** specific named lodging companies (Beavers Bend Lodging) — OK because brand is established.
- **#68 Switzerland:** 1 hotel (Lucerne, named candidates) + 2 Airbnb search-criteria blocks (Lauterbrunnen, Zermatt) — the gold-standard international template.
- **#56 Destin, #59 30A:** beach-trip destinations; condo / Airbnb filters around walkable-to-beach + balcony view.
