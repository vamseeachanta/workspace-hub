# Achantas-data lodging booking-mode pattern

Use this reference when the user asks to review existing vacation-trip records in `achantas-data` and move toward an actual booking, especially for cabins/view-driven stays.

## Durable record first

1. Inspect the existing GitHub issue or trip record before starting fresh web search.
2. Identify the current top-priority lodging candidate and the exact open booking gates.
3. Add/update one durable issue comment rather than leaving the decision only in chat.

## Booking gates for cabin/view stays

For each serious candidate, verify and record:

- Direct listing URL and booking-engine URL, if separate.
- Exact target dates, guest count, pet count, and minimum-night rule.
- Availability status for the target dates.
- All-in payable total, including cleaning fee, taxes, service fee, and deposit/payment schedule.
- Cancellation policy and refund cutoff.
- Full usable kitchen evidence: stove/range, oven or cooktop, full refrigerator, cookware/dishes, dining area, coffee setup, dishwasher if relevant.
- View-from-booked-place evidence: visible from the specific unit/cabin/deck/balcony/hot tub/window, not only from the property grounds or generic marketing photos.
- Access constraints: road/driveway grade, 2WD/4WD requirement, late arrival practicality, parking.
- Contact/phone verification needed before payment.

## View-language discipline

When the user asks for "mountain views," do not treat regional marketing language as sufficient. Classify the actual evidence:

- **Direct panorama:** mountain/hill/lake view visible from the booked unit/deck/hot tub/window.
- **Partial/seasonal:** view exists but may be obstructed by trees, angle, season, or neighboring cabins.
- **Property-only:** scenic area or trail view exists, but not from the booked unit.
- **Fallback urban/water view:** valid only if the user accepts a substitute experience.

## Area substitution rule

If a city itself cannot satisfy the requested view class, state that explicitly and widen to the nearest realistic region instead of forcing weak in-city matches. Example: Austin proper does not provide a Broken Bow/Ouachita-style mountain-cabin experience; closest substitutes are Texas Hill Country / Canyon Lake / Wimberley / Dripping Springs / Lake Travis, with the tradeoff that they are outside Austin proper.

## Comment shape for GitHub issues

Use a compact, booking-action-oriented comment:

```markdown
## Booking readiness — <trip/region>

**Current top priority:** <property + URL>

| Rank | Property | Booking status | Kitchen evidence | View-from-booked-place evidence | Open gates | Action |
|---|---|---|---|---|---|---|
| 1 | <name> | <availability/all-in status> | <specific evidence> | <specific evidence> | <fees/cancel/contact> | <book/call/hold> |

### Pre-payment gates
- Confirm the exact view is visible from the booked cabin/unit/deck/hot tub/window.
- Confirm full usable kitchen equipment.
- Confirm all-in total and cancellation cutoff.
```

Keep the issue note transactional. The goal is to make the next booking action obvious, not to write a travel essay.
