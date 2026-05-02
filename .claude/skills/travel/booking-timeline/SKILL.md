---
name: booking-timeline
description: Use when constructing the Booking & reservation timeline section of a trip plan. Encodes the 4-month / 2-month / 6-week / 1-week reservation cascade and refund-window rules. Invoked by trip-planner.
type: reference
---

# booking-timeline

When to lock what. Reservations have hard deadlines: lodgings fill, scenic-train window seats sell out, fees lock. Get the order wrong and the trip falls apart.

## The 4-tier cascade

Render this as a Markdown table in the trip body. Adjust the lead-times by trip type (international ≥ 4 months out; domestic ≥ 6 weeks; weekend ≥ 1 week).

```markdown
## Booking & reservation timeline

| When | Action |
|---|---|
| **4–6 months out** | Lock dates, book flights, lodging |
| **2–3 months out** | Buy rail/transit pass; reserve scenic-train seats |
| **3–6 weeks out** | Reserve summit/peak attractions; travel insurance |
| **1–2 weeks out** | Confirm visa / ETIAS; download apps + offline maps |
| **Trip day** | Activate passes; check-in 24 hr ahead for flights |
```

## What goes in each tier

### 4–6 months out (the lock-in window)

Things that fill up earliest:

- **Flights** — international flights are cheapest 4–6 months out; US domestic 2–3 months
- **Peak-season lodging** — Swiss alpine villages (May–June), US national park gateway towns, Greek/Italian summer islands
- **Limited-capacity attractions:** Alhambra, Vatican Museums (Friday-night), Yosemite NP campsites, Antelope Canyon tours
- **Train passes** can wait until 2 months — most are open-dated until activation
- **Trip insurance** — buy within 14 days of first deposit for pre-existing-condition coverage

**For domestic / weekend trips: collapse this to "6 weeks out".**

### 2–3 months out (the seat-selection window)

- **Scenic-train seat reservations:** Glacier Express opens 3 months ahead; Bernina Express same; Eurostar opens 6 months
- **Restaurant reservations** at hyped places (Michelin, OpenTable cult restaurants)
- **Specific tour bookings:** guided national park tours, snorkel/dive trips, Northern Lights chases
- **Car rental** if needed — book early for August / Christmas / Easter peaks; otherwise OK to wait
- **Buy the rail pass** if it's open-dated until activation

### 3–6 weeks out (the experience window)

- **High-altitude / weather-dependent attractions:** Jungfraujoch slot, Pikes Peak time-entry, Yosemite Half Dome permit
- **Travel insurance** — buy by this point even if you didn't earlier
- **Cellular plan / SIM** — order international SIM, set up eSIM, or call carrier for travel package
- **Notify card issuers** of travel dates (most banks no longer require this, but some still flag transactions)

### 1–2 weeks out (the prep window)

- **Visa / ETIAS / ESTA** — verify approval status; some take 72 hrs to process
- **Download apps:** transit (SBB Mobile, Citymapper, etc.), maps offline, lodging confirmations as PDFs
- **Currency:** order foreign cash if needed for arrival expenses (taxis, tips). Or plan ATM withdrawal at the airport
- **Pack-list review:** specific to destination (altitude jacket? snorkel? rain gear?)
- **Pet / house sitter:** confirm dates; leave keys
- **Mail hold:** USPS or Amazon vacation hold

### Trip day & arrival

- **Activate the rail pass** on first travel day (most are app-validated, not paper)
- **Flight check-in:** 24 hrs ahead online to lock seat assignment
- **Carry-on essentials:** passport, prescriptions, charger, change-of-clothes, snack
- **Save offline:** lodging address + arrival instructions to phone

## Refund-window rules

These are the cancellation windows to look for when booking. Aim for the most flexible option that fits the budget.

| Item | Free-cancellation window to look for |
|---|---|
| Hotels | ≥ 30 days out (most have this; some chains offer 24 hrs) |
| Airbnb / Vrbo | "Flexible" or "Moderate" cancellation policy; avoid "Strict" |
| Flights (refundable) | Premium fare class only — usually not worth the markup |
| Flights (non-refundable) | 24-hour cancel window per US DOT for tickets bought directly from airline |
| Trip insurance | "Cancel for any reason" rider — pricier but recovers ~75% |
| Tours / activities | Look for "free cancellation up to 24/48/72 hrs before" |
| Rail passes | Most are non-refundable once activated; refundable if not yet activated |
| Scenic-train seat reservations | Often non-refundable supplements; flexible base fare on pass |

## The "what if dates change" rule

Build flexibility into the lock-in. If the trip dates might slip:

- Choose lodging with ≥ 30-day free-cancel
- Wait on non-refundable flights until dates are locked
- Hold the rail pass open-dated (don't activate)
- Postpone travel insurance until 14 days out (still within pre-existing coverage if you bought-then-canceled-and-rebought)

## Region-specific timing nuances

| Region | Booking timing nuance |
|---|---|
| US national parks | Lottery-based permits open 6 months ahead (Half Dome, The Wave); regular campsites 5 months ahead; lodge stays 13 months ahead |
| Switzerland | Glacier Express opens 90 days; Jungfraujoch is same-day in shoulder season but slot-based in summer |
| Italy | Restaurants in Tuscany / Cinque Terre book 1 month ahead in summer; Vatican Museums Fri-eve 60 days ahead |
| Japan | JR Pass must be bought BEFORE arrival (cheaper) or in-country at premium; Shinkansen reservations open 30 days ahead |
| UK | Tower of London / Stonehenge timed entry; book 2 months ahead in summer |
| Iceland | Northern Lights tours weather-dependent; lodging in Reykjavík fills 4 months ahead Sept–Mar |
| Greek islands | Ferries fill in August; book ferry + island lodging together 2 months ahead |

## Reference

- **#41 Beavers Bend:** cabins fill 6 months ahead in fall (peak); 2 months ahead in summer
- **#68 Switzerland:** full 4-tier timeline rendered in body; emphasizes Swiss Travel Pass open-dated flexibility + Glacier Express lock-in
