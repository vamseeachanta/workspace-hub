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

## Mixed-destination issue hygiene

When an existing trip thread mixes distinct destination decisions (for example OK / Broken Bow plus Austin / Texas Hill Country), split them into separate GitHub issues before adding more booking detail.

Operational pattern:

1. Inspect the parent/background issue and search existing issues for both destination names before creating anything new.
2. Reuse or reference any existing destination issue when one exists; otherwise create one issue per destination with a booking-oriented title.
3. Keep the parent issue as background and add one cross-linking comment that points to the destination-specific issues.
4. In the destination issue, preserve the current lead candidate and add new options as gated contenders, not as a flat research dump.
5. Keep the recommendation conservative when view evidence differs by type: a wooded/private/forest view is not the same as a verified mountain/ridge/panorama view from the booked unit.
6. If a sensitive-looking local file path appears during repo search, do not read it for trip planning; represent it only as `[REDACTED]` if it must be mentioned.

Example shape:

- Parent/background issue: vacation ideas or mixed planning thread.
- OK issue: `Booking shortlist: OK / Broken Bow cabin with kitchen + verified view`.
- Austin issue: `Trip planning: Austin / Texas Hill Country options`.
- Parent comment: “Split for booking workflow: OK issue <link>; Austin issue <link>; current OK lead <property>; alternatives <short list>; next gate <view/kitchen/fees/cancel>.”

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

## Cost-estimate add-on for booking issues

When the user asks for a cost estimate after a booking-readiness review, add the estimate to the same GitHub trip issue as a separate transactional comment. Do not leave the table only in chat.

Use observed booking-engine prices when available, but label the estimate as planning-only unless checkout/final payment has been reached.

Minimum cost-estimate issue comment shape:

```markdown
## Cost estimate — <trip / lead lodging option>

Planning estimate only — re-verify everything at booking. Prices in USD, rounded.

**Assumptions used:** <party size>, <lead lodging>, <target dates / nights>, <pets/extra adults>, <food plan>. <Observed booking-rate evidence and tax/fee caveat.>

| Bucket | Basis / evidence | Low | High |
|---|---|---:|---:|
| Lodging | <nightly rates + tax/fee basis> | $X | $Y |
| Fuel / road costs | <origin + route buffer> | $X | $Y |
| Food / groceries / restaurants | <cooking/restaurant assumption> | $X | $Y |
| Activities / rentals | <free-to-paid activity range> | $X | $Y |
| Misc. buffer | <supplies/parking/firewood/etc.> | $X | $Y |
| **Estimated trip total** | <exclusions> | **$X** | **$Y** |

### Optional charges to watch
| Optional item | Added cost |
|---|---:|
| <pet/extra adult/fallback nights/etc.> | <cost formula> |
```

Operational pattern:

1. Draft the comment to a temporary markdown file.
2. Post with `gh issue comment <number> --repo vamseeachanta/achantas-data --body-file <file>`.
3. Verify by viewing the issue comments and checking that the last comment contains the expected table.
4. Reply with the issue comment URL plus a compact total-range summary.

Pitfall: some booking engines expose hidden currency or selected-date fields that are inconsistent with visible rates. In that case, compute from visible nightly rates plus any observed pay-now/tax factor, state the caveat, and require final checkout re-verification before payment.
