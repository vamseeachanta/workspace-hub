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

## Reference — past lodging patterns

- **#41 Beavers Bend cabins:** specific named lodging companies (Beavers Bend Lodging) — OK because brand is established.
- **#68 Switzerland:** 1 hotel (Lucerne, named candidates) + 2 Airbnb search-criteria blocks (Lauterbrunnen, Zermatt) — the gold-standard international template.
- **#56 Destin, #59 30A:** beach-trip destinations; condo / Airbnb filters around walkable-to-beach + balcony view.
