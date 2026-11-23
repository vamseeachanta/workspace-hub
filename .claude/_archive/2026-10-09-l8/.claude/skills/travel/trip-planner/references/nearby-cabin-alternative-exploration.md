# Nearby cabin alternative exploration

Use this reference when the user asks to explore alternatives to a known cabin/destination vibe, especially a drivable domestic family cabin trip.

## Trigger shape

Examples:
- “Explore similar options in nearby Texas.”
- “Find something like Broken Bow but closer.”
- “Same cabin/hot tub/forest feel, less drive time.”

This is usually an **idea / ranking** task, not a full trip plan or booking task. Create or update a GitHub tracking issue when the user asks to “create an issue,” “track this,” or the comparison will span multiple destination clusters.

## Workflow

1. **Capture the source vibe as criteria.** Translate the reference destination into concrete filters: drive-time gate, cabin style, hot tub/private deck, forest/views, dog policy, hiking/water access, family fit, and cost baseline.
2. **Search existing trip issues first.** Reuse an active matching issue if one exists; create a new issue only when no active issue covers the exploration or the user explicitly asks for one.
3. **Use a ranking-matrix issue shape.** The issue should contain: origin approximation, drive-time gate, target feel, cost baseline, candidate regions, evaluation criteria, and next research tasks.
4. **Benchmark against the known option.** If the user provides a baseline such as “acceptable cabin ~$750 / 3 nights; good family cabin ~$1,000 / 3 nights,” record it in the issue and compare every candidate against it. A closer option still needs to justify a premium with better water, views, hot tub, dog policy, or family amenities.
5. **Verify drive time independently.** Use a routing source or mapping API estimate from the user’s approximate origin; label it as planning-time / non-live-traffic if applicable. Do not rely on generic city-center drive times when the user specified a side of town.
6. **Treat web search as lead generation, not booking proof.** Search snippets can identify candidate companies or regions, but booking-readiness requires direct listing/company pages or booking-engine verification.
7. **Use named properties only when established and source-backed.** For Airbnb/Vrbo category pages, describe search filters and examples as leads; do not present them as verified availability or invent listing names. Local cabin companies with public listing pages can be named if their amenities are source-backed.
8. **Post findings as an issue comment.** Prefer a compact ranked table/comment over rewriting the entire issue body after the first pass. Include URLs, caveats, and next booking gates.
9. **Escalate to one child issue per ranked option when requested.** If the user asks for deeper exploration after the ranking pass, create one child issue for each ranked destination/region instead of one enormous parent comment. Each child issue should be self-contained: summary, parent link, visual review board, fit-against-requirements table, lodging leads with source URLs, 3-night cost math against the user's baseline, nearby activities, cost verdict, and open booking gates. Then comment on the parent with links to all child issues.
10. **Verify the rendered issue tree.** After creating child issues, re-query each issue with `gh issue view --json number,title,state,url,labels,body,comments` and verify: open state, expected label, parent link in every child body, image embeds present, cost-verdict section present, and parent comment contains every child URL.

## Ranking fields

Use these columns in the comment where possible:

| Lane | Drive from origin | Match to reference vibe | Cost expectation vs baseline | Verified leads | Caveats / next checks |
|---|---:|---|---|---|---|

## Common caveats

- “Hot tub” availability is often per-unit, not property-wide; verify the exact unit before recommending.
- “Pet-friendly” often means fee + breed/weight rules; verify before payment.
- “Views” can mean property-area views, not from the cabin/deck/hot tub. For view-sensitive decisions, classify the view evidence.
- Search pages and aggregators may be stale; direct listing pages and final booking engines are more authoritative.
- If a candidate exceeds the drive-time gate, mark it as a stretch instead of forcing it into the shortlist.

## Example pattern from session

For a west-Houston family looking for a Broken Bow / Lookout-style substitute, the useful ranking lanes were:
1. Wimberley / Canyon Lake — best hot-tub + deck + Hill Country view substitute.
2. Lake Livingston / Sam Houston National Forest — best short-drive pine/lake/hiking substitute.
3. Bastrop / Lost Pines — short-drive pine/ranch/seclusion backup.
4. New Braunfels / Gruene — family river-town activities, less secluded.
5. Caddo Lake / Uncertain — atmospheric cypress/swamp stretch if drive-time exceeds the gate.
