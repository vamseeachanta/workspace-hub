---
name: itinerary-design
description: Use when constructing a day-by-day itinerary inside a trip plan. Encodes base-count rules, jet-lag handling, transit-day discipline, slack budgeting, and the "last day = travel only" rule. Invoked by the trip-planner skill.
type: reference
---

# itinerary-design

Constructing a day-by-day plan that doesn't fall over on contact with reality.

## The base-count rule

| Trip length | Max # of overnight bases |
|---|---|
| 3 days / 2 nights | 1 base |
| 4–5 days | 2 bases |
| 6–8 days | **3 bases** (default for a week) |
| 9–14 days | 4 bases |
| 15+ days | 5+ bases, but each base ≥ 2 nights |

**Rule:** Never plan a base for fewer than 2 nights. Single-night stops mean you spend the whole trip packing/unpacking. Exception: a deliberate "transit night" near the airport on the way in or out.

## Jet-lag day = hotel, not Airbnb

For international trips with > 4 hours of time-zone shift, **the first night must be at a hotel, not an Airbnb**. Reasons:

- Hotel front desks handle late/early check-in flexibly; Airbnbs typically do not
- Hotels have on-site breakfast for the inevitable 5 AM jet-lag wake-up
- Help with luggage, transit info, and onward arrangements when you're cognitively offline

This is why #68 anchors Day 1 at a Lucerne hotel before moving to Lauterbrunnen Airbnb on Day 3.

## The last day = transit-only rule

The final day of any trip is a travel day only. Do NOT plan a "morning hike then afternoon flight" — flight delays, security lines, and traffic eat the morning. The last activity should be the night before. Build your departure day as: pack, breakfast, transit to airport, fly home.

## Slack budgeting

For every 7 days of trip, plan **at least one buffer half-day** (no scheduled activity). Reasons:

- Recovery from altitude/long hikes
- Weather closures (Alps lift shutdowns, beach storms, road washouts)
- Family member sickness / fatigue
- A spontaneous local recommendation that turns into the trip's best memory

Mark this in the itinerary explicitly as "buffer afternoon" or "flex day" — don't pretend it doesn't exist.

## Transit math

When estimating how long it takes to get from A to B with a family:

- **By train (Europe):** scheduled time + 30 min buffer per transfer
- **By car (US road trip):** Google Maps estimate × 1.25 with kids (bathroom + food stops)
- **By plane:** door-to-door = scheduled flight + 3 hrs (airport arrival, security, baggage, transit to lodging)
- **First-day arrival from intercontinental:** door-to-door + 2 hrs of jet-lag drag before you're functional

If a day's transit + planned activities exceed 10 functional hours, split the day or skip one activity.

## Day shape rules

- **One headline activity per day.** Two big things compete; the second always feels rushed.
- **Morning > afternoon for outdoors.** Better light for photos, cooler temps, less crowded for popular sites.
- **Indoor / restaurant fallback for every outdoor day.** Especially mountain/beach trips where weather is volatile.
- **Kid energy peaks at 10–11 AM.** Schedule the cognitive-load activity (museum, history site) then; save the playground / pool for late afternoon.

## Sequence direction

When the trip touches multiple regions, the sequence direction matters more than people expect:

- **Easy → hard, low altitude → high altitude** so the family acclimates progressively. Lucerne (440 m) → Lauterbrunnen (800 m) → Jungfraujoch day-trip (3,454 m) is correct; reversing this triggers altitude headaches on Day 1.
- **Familiar food → adventurous food** for sensitive eaters; ease into local cuisine.
- **Quietest base last** so the trip ends restful, not chaotic.
- **Flagship moment in the middle two-thirds**, never on Day 1 (jet lag) or last day (transit).

## When to use the day-by-day Markdown table

Render the itinerary as a 3-column table: `Day | Base | Plan`. The base column makes mid-trip moves visible. Bold the day-of-week label (e.g., `**Day 1 (Sat)**`) so the reader can map plans to specific calendar days.

## What NOT to include in the day-by-day

- Specific restaurant reservations beyond "dinner in Old Town" — they churn
- Specific train times — they change seasonally
- Anything past 9 PM — leave evenings unscripted
- Driving/transit times to the minute — round to the half-hour and add buffer

## Reference patterns

- **Lucerne → Lauterbrunnen → Zermatt** (#68): three bases, 2 nights each, ascending altitude, jet-lag day at hotel, last day transit-only. This is the gold-standard 7-day international template.
- **Houston → Broken Bow** (#41): single base, 2–4 nights, day-trip excursions to lookouts. Gold-standard domestic-cabin template.
- **Houston → Dallas → Oklahoma → Houston** (#19): linear road trip, single-night stops. Acceptable only because total nights ≥ 5 and pacing allows recovery.
