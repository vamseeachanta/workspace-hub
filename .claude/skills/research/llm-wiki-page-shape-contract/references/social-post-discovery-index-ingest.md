# Social-post discovery-index ingest pattern

Use when a social post points to a public index/catalog rather than containing the substantive technical source itself (example: X post pointing to a Papers With Code conference page).

## Pattern

1. Capture both layers:
   - Social pointer: author, handle, post date/time if visible, post URL, short quoted text.
   - Expanded destination: final URL, page title, observed counts/facets, observation date.
2. Route by substance:
   - If the destination is a public research/source index, write a `sources/` page in the strategic/research-discovery domain.
   - Do not create a concept page from a single pointer/index unless another source or implemented workflow triangulates the pattern.
   - Do not promote individual papers/tools/results from the index until the actual paper/project page has been reviewed.
3. Treat index counts as observed page state, not authoritative ground truth:
   - Record discrepancies between social-post claims and destination-page counts.
   - Do not sum overlapping task/domain facets as unique-paper totals.
4. Recommended page framing:
   - “research-discovery infrastructure signal,” “source index,” or “triage surface.”
   - Explicitly state what the page may and may not be cited for.

## Verification

- Frontmatter exists and required domain fields are present.
- Index source/page counts are bumped consistently.
- Log records routing decision and any count discrepancy.
- Legal sanity scan passes for public-bound material.
- If YAML dependencies are unavailable, fall back to lightweight frontmatter presence/key checks rather than treating dependency absence as task failure.
