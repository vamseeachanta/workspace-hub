<!--
TEMPLATE: Cross-trip ranking matrix
Used by: trip-planner skill (when archetype = "ranking")
Reference issues: #67
Replace all `<...>` placeholders. Use 1–5 scale where 5 is best.
-->

## Feature: family travel ranking decision matrix

Create and maintain a single review-friendly matrix for the top travel options so family members can compare choices quickly without opening every issue first.

## Purpose

The existing travel issues contain detailed seasonal photos, lodging notes, and destination-specific caveats. This feature issue summarizes the **top N ranked choices** in a tabular format with the most important decision factors:

1. Overall ranking
2. Location / destination
3. Estimated one-way drive time / flight time from Houston
4. Scenery quality
5. Food quality
6. Lodging quality / cabin or hotel fit
7. Family ease / kid-friendly logistics
8. Season robustness
9. Weather / water-level / closure risk
10. GitHub issue hyperlink for detailed review

## Top <N> travel ranking matrix

> Drive/flight times are practical planning estimates and should be rechecked before booking. Scores use a 1–5 scale where 5 is best. Risk is Low / Medium / High based on weather, water color, seasonal dependency, and travel commitment.

| Rank | Location / destination | State / country | Est. travel from Houston | Best trip style | Scenery | Food | Lodging | Family ease | Season robustness | Risk | GH issue hyperlink |
|---:|---|---|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | <Destination> | <ST> | <X.X hr> | <One-line style> | <1–5> | <1–5> | <1–5> | <1–5> | <1–5> | <Low/Med/High> | [Open #NN](<url>) |
| 2 | ... | | | | | | | | | | |
| ... | | | | | | | | | | | |

## Quick interpretation

- **Best balanced choice:** #<NN> <reason>.
- **Best <category> alternative:** #<NN> <reason>.
- **Best <category> choice:** #<NN>.
- **Best <category> backup:** #<NN>.

## Decision checklist before selecting a weekend/trip

- [ ] Confirm target travel dates and total nights available.
- [ ] Check latest weather, road conditions, park closures, lake/river conditions, and recent visitor photos.
- [ ] Confirm lodging availability and cancellation policy.
- [ ] Decide if family wants: <category 1>, <category 2>, <category 3>, or <category 4>.
- [ ] Re-rank if the family prioritizes shorter travel time over scenery.
- [ ] Re-rank if the family prioritizes food quality over nature scenery.
- [ ] Re-rank if travelling with kids/elders who need low-walking logistics.

## Follow-up improvement

If useful, convert this into a weighted scoring matrix with adjustable weights for:

- Travel time
- Scenery
- Food
- Lodging
- Kid/elder friendliness
- Cost
- Weather risk
- Seasonal photo confidence
- Number of activities within 30 minutes
- Overall family excitement

## Related detailed issues

- <Parent trip 1>: #<NN>
- <Parent trip 2>: #<NN>
- <Parent trip 3>: #<NN>
