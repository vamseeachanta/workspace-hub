# Regional cabin alternative issue-tree pattern

Use this when a user asks to explore multiple cabin/lodging regions that are substitutes for a known reference vibe (for example “Broken Bow feel closer to Houston” or “Arkansas Broken Bow-style options”), especially when Airbnb/Vrbo are allowed but listing churn makes named marketplace listings unsafe.

## Durable structure

Create a parent issue for the reference-vibe search, then destination/lane child issues when there are 3+ serious regions.

Parent issue should contain:
- the reference vibe and hard filters (origin, drive tolerance, cabin/hot tub/forest/water/pet/kitchen requirements);
- budget posture with explicit “base rate vs all-in fees” caveat;
- ranked region table with drive, vibe fit, cost expectation, and tradeoffs;
- visual review board with one source-grounded image per lane;
- booking-readiness gates before payment;
- links to existing related destination issues.

Child issue should contain:
- parent backlink;
- related existing destination issues;
- fit-against-requirements table;
- visual board with listing/destination images;
- lodging leads table: Lead, Source URL, Why it fits, Cost evidence, Open gates;
- cost verdict and next booking gates.

## Ranking rule

Rank by user’s actual priority, not by geography alone. For Broken Bow-style cabin searches, useful axes are:
1. closest match to reference feel (secluded cabin, hot tub, forest/mountain, water/hiking);
2. drive time from the stated origin;
3. probability of finding a family-sized private-hot-tub cabin under target budget;
4. pet-friendliness if required;
5. destination infrastructure (restaurants, activities, rainy-day options).

If the best vibe is a much longer drive, say so directly and keep a shorter-drive/value fallback alive.

## Airbnb/Vrbo handling

Airbnb/Vrbo search pages are valid as marketplace lanes, but do not invent or over-commit to individual listing names from search pages. Put them in the lodging leads table as “search lanes” with listing-level verification gates:
- exact dates and final all-in price;
- pet rules and fees;
- private/unit-specific hot tub;
- full kitchen proof from text and photos;
- view or water evidence from the booked cabin/deck/hot tub/window, not generic property marketing.

Named local cabin-company listings are acceptable when grounded by live source pages and public details.

## Verification closeout

Before reporting completion after issue creation:
- use `gh issue view` on every created issue;
- verify parent has a child-link comment;
- verify each child has parent backlink and image markup when visuals were promised;
- remove temporary markdown/body files created under `/tmp`;
- surface unrelated dirty repo state as unrelated residue, not as task output.

## Example issue tree

Arkansas Broken Bow-style lodging exploration created:
- parent: `Travel Explore: Arkansas Broken Bow-style cabin alternatives`
- children: Eureka Springs / Beaver Lake; Lake Ouachita / Hot Springs / Mount Ida; Mena / Ouachita Mountains; Buffalo National River / Jasper / Ponca; Petit Jean / Mount Magazine fallbacks.

The useful pattern is not the exact destinations; it is the parent + lane child split, ranking table, visual boards, source-grounded lodging leads, and explicit booking gates.