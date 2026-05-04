---
name: risk-and-redundancy
description: Use when populating the Watch-outs section of a trip plan. Encodes failure modes (closures, weather, motion sickness, altitude, kid logistics) and the rule that every trip needs a Plan B for load-bearing legs. Invoked by trip-planner.
type: reference
---

# risk-and-redundancy

The "no surprises" promise. A good trip plan surfaces what could go wrong inside the plan itself, with a fallback for each load-bearing leg, so the family is never blindsided.

## The watch-outs taxonomy

Every trip should consider risks across these eight categories. Skip a category only if it genuinely doesn't apply.

### 1. Weather closures

What can shut down on short notice:

- **Mountain lifts and cogwheel railways:** fog, high wind, lightning. Schilthorn / Klein Matterhorn / Pilatus all close 5–10 days/year in summer, more in shoulder season.
- **Coastal ferries:** rough seas, hurricane warnings (Gulf, Atlantic, Pacific NW)
- **Mountain passes / scenic byways:** snow closures (Alpine, Rocky, Sierra; even May–June in high passes)
- **Beach access:** red tide (FL Gulf), jellyfish blooms, hurricane evacuation orders
- **National park gates:** wildfire smoke, flooding (especially desert flash floods)
- **Avalanche / rockfall closures:** alpine roads, NM/UT/CO state highways

**Always name the specific failure mode** in the trip body, not generic "check weather". E.g., #68 says: "Schilthorn, Klein Matterhorn, and Pilatus can shut on short notice for fog/wind. Build in a buffer day or be willing to swap to a lower-altitude alternative."

### 2. Sold-out / fully-booked

- **Premium reservations:** Glacier Express in summer; Jungfraujoch on clear days; Yosemite Tunnel View parking; Antelope Canyon tours; Alhambra entry tickets
- **Lodging:** US national park towns 9 months out; Lauterbrunnen / Wengen 4 months out for May–June; beach condos peak season
- **Events:** local festivals can sell out the entire town's lodging — check trip dates against major festivals
- **Restaurants:** Michelin-starred / hyped restaurants 2+ months ahead

For each load-bearing reservation, name the open-window: "Glacier Express opens 3 months ahead, fills for window seats."

### 3. Motion sickness / altitude / physical strain

- **Cogwheel railways with steep gradient** (Pilatus 48%, Mt. Washington 25%) — bring Dramamine
- **Switchback mountain roads** (Going-to-the-Sun, Stelvio Pass, Trollstigen)
- **Boat tours / ferries** in choppy waters
- **High-altitude attractions:** Jungfraujoch 3,454 m, Pikes Peak 4,302 m, Tibetan plateau anywhere — limit time at summit, hydrate, no alcohol
- **Long hikes:** check kid / elder fitness gates; provide turnaround points

### 4. Kid / elder logistics

- **Long transit days:** plan bathroom + food breaks every 2 hours
- **Naptime windows:** 1 PM – 3 PM with toddlers
- **Stroller access:** cobblestoned hill towns (Italian medieval, French Provence) are stroller-hostile
- **Stair-only lodgings:** elevator filter is non-negotiable for elderly + heavy bags
- **Kid energy peak:** mornings; schedule the cognitive-load activity before lunch
- **Picky eaters:** familiar food first night; ease into local cuisine

### 5. Sunday / holiday closures

- **Switzerland:** most grocery stores closed Sunday (train station Coops/Migros are exception)
- **Germany / Austria:** Sunday closures even more strict
- **Italy:** August (especially Aug 15 / Ferragosto) — much of Rome / non-tourist towns shut
- **Spain / France:** afternoon siesta closures 2–5 PM in smaller towns
- **US national parks:** entry station hours; some parks close in winter
- **Religious holidays:** Easter/Christmas; Ramadan in Muslim-majority countries (food access changes)

### 6. Currency / payment / connectivity

- **Cash-only reality:** rural Italian trattorias, Japanese small inns, French boulangeries, German biergartens
- **Currency:** Switzerland is **CHF not Euro**; UK is **GBP not Euro**; Norway is NOK; Sweden is SEK
- **Card acceptance:** Amex rarely accepted in Europe; some Japanese / German shops are Visa/MC only
- **Cellular dead zones:** rural national parks, Norwegian fjords, parts of Iceland, Alpine valleys
- **Download offline:** Google Maps, lodging address, train tickets, lodging confirmation PDFs

### 7. Documents / visas / health

- **Passport validity:** must be valid ≥ 6 months past return date for most international travel
- **ETIAS** (Europe-Schengen): rolling out 2026; verify status at booking
- **Vaccinations:** check CDC for destination-specific recommendations 4–6 weeks ahead
- **Travel insurance:** medical + cancellation; non-trivial for Switzerland (healthcare excellent but expensive without coverage)
- **Prescription medication:** carry in original bottles + doctor's note for international
- **Driver's license:** International Driving Permit required in Italy, Greece, parts of Asia

### 8. Local pitfalls

The "wish I'd known" knowledge per region:

- **Zermatt:** car-free; last vehicle stop is Täsch + 12-min train
- **Italian ZTL zones:** historic centers fine the rental car ~€100 per drive-in
- **Iceland F-roads:** require 4WD; rental insurance often excludes them
- **Hawaii:** no rental cars on Lanai; book the inter-island flight first
- **Yellowstone:** geothermal area boardwalks only — children go off-trail and die yearly
- **Beach destinations:** lifeguard hours; rip currents; no-swim red flags
- **Train station luggage:** US Amtrak has limited overhead; Eurostar has explicit size limits

## The Plan B rule (load-bearing)

Every load-bearing leg of the trip must have a named fallback. A leg is load-bearing if its failure cancels the rest of the day or trip.

| Load-bearing leg | Plan B |
|---|---|
| Glacier Express reservation | Regular SBB regional train (same scenery, no panoramic windows, no supplement) |
| Jungfraujoch on cloudy day | Schilthorn / Mt. First / Trümmelbach Falls |
| Hot Springs NP bathhouse closed | Hike Hot Springs Mountain Tower |
| Beach day, red tide warning | Day-trip to Mobile Bay aquarium / inland state park |
| Beavers Bend cabin booking falls through | Broken Bow Lake state park lodge |
| Flight cancellation Day 1 | Hotel willing to flex check-in by 24 hrs |
| Restaurant reservation lost | Backup #2 in same neighborhood |

If a leg has no acceptable Plan B, mark it explicitly: "If the Glacier Express seats are sold out, the alpine scenery alternative is Bernina Express; both should be booked as a pair."

## Buffer day

For trips ≥ 5 days, build in **at least one buffer half-day** — no scheduled activity, available to absorb a closure / illness / spontaneous opportunity. Mark it explicitly in the itinerary so it doesn't get filled by accident.

## Watch-outs section template

```markdown
## Watch-outs

- **<Most likely failure mode>** <how it presents> <Plan B>
- **<Second failure mode>** ...
- ...
- **<Local pitfall #1>** ...
- **<Document / health gotcha>** ...
- **<Sunday / closure timing>** ...
- **<Kid / elder logistics>** ...
- **<Currency / payment>** ...
```

Aim for 6–10 bullets. Fewer = under-prepared trip plan; more = unreadable.

## What separates this from "common sense"

A travel agent's value is naming the **specific** failure mode, not generic advice:

- ❌ "Check the weather" — useless
- ✅ "Schilthorn closes for high winds 5–10 days/year in summer; have a Trümmelbach Falls alternative ready"

- ❌ "Drive carefully" — useless
- ✅ "Going-to-the-Sun Road has alpine switchbacks that trigger motion sickness; sit in front, eat lightly before"

- ❌ "Bring layers" — useless
- ✅ "Jungfraujoch is -5 °C in summer; valley is 22 °C; pack one warm layer per person carry-on, not check-in"

The bar: every watch-out should name **what closes**, **why**, **how often**, **how it presents**, and **what to do instead**.
