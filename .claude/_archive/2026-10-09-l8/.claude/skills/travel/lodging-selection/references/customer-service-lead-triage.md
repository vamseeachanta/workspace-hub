# Customer-service lead triage for lodging booking

Use this reference when the user calls a lodging company/host and reports a specific property suggested by customer service.

## Durable pattern

1. Treat the suggested property as a **practical lead**, not an automatic winner.
2. Re-scrape or re-open the live listing and extract grounded facts:
   - capacity, bedrooms, beds, baths
   - kitchen evidence and missing kitchen amenities
   - view language and photo evidence
   - access/driveway constraints
   - booking-engine / reserve URL
3. Compare the suggestion against the user's **current top priority**, not the earlier default priority. If the user shifted from kitchen/amenities to panorama/view, do not let a stronger amenity fit outrank a weaker view fit without saying so.
4. Create explicit pre-payment gates for anything not proven by listing evidence.
5. If the property's view evidence may be property/trail-only, ask the host whether the view is visible from the **unit/deck/hot tub/window**, not merely from the broader property.
6. For kitchen-dependent family stays, ask for concrete equipment confirmation: stove/oven, refrigerator, microwave, cookware/dishes, dining setup. Note missing dishwasher/washer-dryer separately rather than hiding them under “kitchen.”
7. Add the customer-service update to the durable decision trail: handoff/restart file and/or GitHub issue comment if the trip is being tracked there.

## Good host-call wording

> Customer service suggested <property>. Before we book, can you confirm: (1) is the lake/ridge/nature view visible from the cabin/deck/hot tub/window, not just from the property trail, and (2) does the cabin have a full usable kitchen for family meals — stove/oven, refrigerator, microwave, cookware/dishes? Also, is driveway/access OK for our vehicle if it rains?

## Example: Broken Bow cabin case

A customer-service suggestion for Trail House at Eagle Ridge became the practical lead because it came from the lodging company after the user called. The listing had strong nature language (“gorgeous views,” National Forest, trail to lake) and amenities, but available evidence did not prove that the view was visible from the cabin/deck/hot tub rather than the property/trail. The correct closeout was therefore: practical lead, but gated on host confirmation of view-from-unit and full usable kitchen before payment.
