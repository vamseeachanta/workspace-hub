# Package-deal comparison issue tree

Use this when the user wants to compare travel-package deals across multiple countries, regions, resorts, or operators, especially when they explicitly asks for each option to become its own GitHub issue and a single parent comparison issue.

## Trigger examples

- "Plan South America as each individual GitHub issue for each country; compare them all in a single issue."
- "Research Costco Travel deals for several destinations and compare."
- "Make one issue per country/resort, with a parent ranking issue."

## Workflow

1. **Resolve the tracking repo and labels first.** Default travel planning repo is `vamseeachanta/achantas-data` when the user is using personal trip planning. List available labels and reuse existing labels only unless the user asks to create new taxonomy.
2. **Search for duplicates before creating anything.** Search by trip region, vendor, and major destination names. If a matching parent exists, reuse it and add child issues/comments instead of creating a duplicate tree.
3. **Create the parent comparison issue first.** Parent should contain:
   - Summary and trip goal.
   - Candidate list and why each is in scope.
   - Comparison criteria table: package price, flights/route complexity, number of nights, family fit, seasonality, safety/health notes, visa/entry constraints, cancellation terms, and booking confidence.
   - Vendor-access evidence and limitations.
   - Child issue checklist placeholders or a section to fill after children are created.
4. **Create one child issue per serious option.** Child should contain:
   - Parent link-back.
   - Vendor/package search target.
   - Why this option belongs in the comparison.
   - Fit dimensions and open questions.
   - Fields for package name, travel dates, nights, airports, inclusions/exclusions, total price, member perks, cancellation terms, and booking deadline.
5. **Patch the parent with final child links.** After child creation, edit the parent body to replace placeholders with issue checklist links. Re-query the parent to verify the rendered body includes every child.
6. **Verify every child links back to the parent.** Use `gh issue view --json number,title,url,labels,body` or equivalent and check parent URL/body markers before reporting success.
7. **Clean temporary body files.** If bodies were staged under `/tmp/<slug>`, remove them after verification unless they are needed for a handoff.

## Vendor-access limitations

Travel vendors often block automated browsing or require member/login context. Do not convert that into a durable negative claim that the vendor cannot be accessed. Instead:

- Record the observed access limitation in the issue body with exact error class only when it affects confidence.
- Use search-index snippets as low-confidence discovery evidence, not as confirmed package details.
- Mark package names/prices/inclusions as `needs member-session verification` until checked from a normal logged-in browser.
- Do not claim a deal exists or is bookable unless the live vendor page or booking engine was reached and the specific package details were visible.

## Costco Travel-specific notes

For Costco Travel package research:

- Direct package pages may require normal browser/member context; if access fails, preserve the research path and keep confidence explicit.
- `Travel-Offers` pages and indexed search-result snippets can identify likely regional package surfaces, but they do not prove current availability, price, or inclusions.
- Child issues should include a Costco verification checklist: package name, dates, origin airport, included hotels/tours, Shop Card/member perks, cancellation policy, final price, and whether flights are included.

## Minimal parent closeout evidence

When reporting completion, include:

- Parent issue URL.
- Child issue URLs.
- Label used.
- Verification that parent links to children and children link to parent.
- Any vendor-access limitation affecting confidence.
