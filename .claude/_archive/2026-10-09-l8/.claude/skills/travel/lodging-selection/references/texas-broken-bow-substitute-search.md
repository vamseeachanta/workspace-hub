# Texas Broken Bow-Style Cabin Substitute Search

Use this reference when the user wants the Broken Bow / Beavers Bend feel — secluded cabin, private hot tub, wooded setting, hiking, possible water access, dog-friendly — but wants to stay within roughly 4 hours of west Houston.

## Durable search pattern

1. Preserve the user's reference vibe as explicit filters instead of restarting with generic weekend-getaway criteria:
   - secluded/private cabin
   - hot tub or soaking feature
   - forest/pine/wooded or hill-country nature setting
   - hiking or state/national forest nearby
   - lake/river/swimming/kayaking optional but high-value
   - dog-friendly where requested
   - practical drive-time gate from west Houston
2. Create/reuse a parent GitHub issue for the cross-region ranking when the user asks to “explore this” rather than book immediately.
3. Create child issues only for serious lanes, not every brainstormed town. Each child should carry:
   - parent backlink
   - drive-time reality from west Houston
   - fit-to-reference-vibe table
   - lodging search lanes, not invented Airbnb/Vrbo listings
   - live examples only if grounded by URLs and availability/pricing evidence
   - next booking gates: exact dates, guest count, pet rules, hot tub proof, kitchen proof, view/privacy proof, all-in cost
4. For closeout, verify all issue URLs with `gh issue view`, then write a session handoff if the user asks to exit or restart later.

## Candidate ranking frame from the 2026-05 session

Rank by closeness to the Broken Bow feel, not by generic popularity:

| Lane | Drive from west Houston | Fit | Tradeoff |
|---|---:|---|---|
| Lake Livingston / Sam Houston National Forest | ~1.5–2 hr | Closest pine-forest + lake + hiking analogue; short drive | Fewer polished luxury-cabin and restaurant options than Hochatown |
| Wimberley / Canyon Lake / Hill Country | ~3–3.5 hr | Best hilltop cabin, hot tub, river/swimming-hole, destination feel | Cypress/limestone/open vistas, not dense pine forest |
| Bastrop / Lost Pines | ~2.5 hr | Pine outlier west of Houston; resort/cabin fallback | State park/fire-recovery context; less lake-cabin inventory |
| New Braunfels / Gruene | ~3 hr | Riverfront family activity, tubing, restaurants | More river-town than secluded forest cabin |
| Caddo Lake / Uncertain | ~4–5+ hr depending west-Houston start point | Atmospheric cypress/moss/kayaking, unique and magical | Often outside a strict 4-hour gate from Katy/west Houston; bayou/waterfront feel rather than hilltop hot-tub-over-pines |

## No-dates preliminary scout pattern

When the user provides party size and trip length but not exact dates, keep the output explicitly **fit-only**:

- Create/reuse one parent GitHub issue for the exploration.
- Add a comment with ranked candidate regions and named direct-booking/property URLs only when grounded by live source pages.
- Do not claim live availability, exact pricing, or final taxes/fees.
- Label missing inputs: exact 3-night date window, dog yes/no and size, all-in budget, private-hot-tub mandatory vs optional, water/view mandatory vs optional.
- If using drive-time evidence, state the origin proxy (for example Katy/west Houston) and do not preserve stale approximations when routing contradicts them.

Property leads from the 2026-05 west-Houston scout that are worth checking first once dates are known:

| Lead | Region | Why it fits | Caveat |
|---|---|---|---|
| Stay in Babia | Sam Houston NF / Montgomery | Secluded A-frame cabins, forest setting, private hot tubs, sleeps 4, pet-friendly cabins available | More luxury A-frame/glamping than large log cabin; verify specific pet-friendly unit |
| Lost Forest Cabins | Richards / Sam Houston NF | Private forest acreage, pond/forest views, fishing/kayaking/paddleboarding/trails | Private hot tub and pet policy need live confirmation |
| Two Creeks Crossing | Lake Livingston | Family cabin resort, water access, some pet-friendly cabins | Hot tub appears shared rather than private |
| Hideout Cabin Wimberley | Wimberley | Pet-friendly, hot tub, deck/views, near Wimberley Square | Hill Country overlook, not dense pine forest; river bed may be dry |
| Darlings Hill El Sol / La Luna | Wimberley | Secluded, private hot tub, pets allowed, sleeps 2–4 | Verify sleeping setup for a child |
| Pine Tree Palace | Bastrop / Lost Pines | Private hot tub, pine grove, family-sized layout, near parks/water | Confirm current pet terms before booking |
| Son’s Geronimo | New Braunfels area | Creek/kayak/pool-heavy family activity | Resort-like; shared hot tubs; pet policy needs confirmation |
| Birdsong Cabins Ruby Red Bird | Wimberley | Private pool + hot tub, 2BR, privacy | Not pet-friendly per policy signal |

## Practical issue-tree shape

Parent issue title pattern:

`Travel Explore: Broken Bow-style cabin alternatives within ~4 hours of west Houston`

Child issue title patterns:

- `Travel Explore: Lake Livingston / Sam Houston National Forest cabin option details`
- `Travel Explore: Wimberley / Canyon Lake cabin option details`
- `Travel Explore: Bastrop / Lost Pines cabin option details`
- `Travel Explore: New Braunfels / Gruene cabin option details`
- `Travel Explore: Caddo Lake / Uncertain cabin option details`

## Pitfalls

- Do not over-index on restaurants/shops when the user's reference point is Broken Bow cabin seclusion; rank the nature/lodging fit first, then note destination amenities as a secondary tradeoff.
- Do not call Wimberley or New Braunfels “forest equivalents.” They are Hill Country / river-town substitutes with different landscape texture.
- Do not treat Lake Livingston/Sam Houston as a luxury-cabin market without checking live inventory; its strength is proximity and pine/lake bones, not Hochatown-style lodging density.
- Do not invent Airbnb/Vrbo listing names. Use search lanes unless live listing URLs are verified.
- When moving from exploration to booking, switch to the normal domestic cabin booking-readiness workflow in `SKILL.md` and verify exact dates, pet fees/rules, hot tub photo evidence, kitchen evidence, privacy/view evidence, and all-in cost.
