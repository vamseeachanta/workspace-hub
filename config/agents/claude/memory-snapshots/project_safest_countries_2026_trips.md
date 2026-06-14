---
name: project_safest_countries_2026_trips
description: achantas-data trip shortlist built from the 2026 Global Peace Index Top 10 (hub
metadata: 
  node_type: memory
  type: project
  originSessionId: 767b765f-fcc5-4882-8b1f-edcd74f0d831
---

2026-06-09: Built a family trip shortlist in **achantas-data** (`/mnt/local-analysis/achantas-data`) from the BBC "World's Safest Countries 2026" article (Global Peace Index Top 10). Followed the repo's established **hub-and-spoke trip pattern** (cf. South America #107–113): trips are GitHub issues labeled `documentation,dispatch:ready,machine:dev-primary,domain:travel-planning-international`, plus a mirror markdown artifact under `_travel/<year>/`.

- **Hub:** #118 (ranking matrix, IAH/family params, decision matrix, 2026 entry notes, open decisions).
- **Per-country children:** Iceland #119, New Zealand #120, Slovenia #121, Ireland #122, Austria #123, Portugal #124, Singapore #125, Finland #126, Japan #127. Each has best/worst season, itinerary sketch, lodging, **live-researched 2026 cost table** (IAH airfare + family-of-4 all-in), watch-outs, US-passport entry notes, go/maybe/skip.
- **Switzerland (GPI #3) reused existing #68** — did NOT duplicate.
- **Artifact merged to main:** `_travel/2026/safest-countries-2026.md` (PR #128, commit `1388f18`). **Handoff doc:** `docs/session-handoffs/2026-06-09-safest-countries-2026-trips.md` (PR #130, commit `cf4ba25`).

**Cost posture (family of 4, all-in):** value=Portugal $6.2–8.8k / Slovenia $7–9.5k / Singapore $7.2–10k / Ireland $8.5–13k; mid=Finland $8–13.5k / Japan $9–13k / Austria $9.5–13k; bucket-list=Iceland $11–15k / New Zealand $17–24k.

**GOTCHA — achantas-data CI is whole-tree, pre-existing red:** every PR runs `lint` (markdownlint) + `check` (lychee link-check) over the ENTIRE repo, and main already has ~27 markdownlint errors + ~68 dead links in unrelated files (`_family/*`, `_finance/india_land/*`, `00_tx_ag_land.md`). So every PR shows red CI regardless of content. PR state is `UNSTABLE` not `BLOCKED` → checks are non-required, merge is allowed. Verify your own added files pass via `npx markdownlint-cli2 <file>` (the `_travel`/`docs` additions were 0-error) and merge over the pre-existing red. Local `main`==`origin/main`, clean base, branch from origin/main.

**Open for next session:** (1) confirm family size (totals assume 4); (2) pick season window(s); (3) pick a near-term lead to mature into a booking itinerary (Portugal=value, Japan=easy IAH-NRT nonstop) following `tmp/claude-trip-maturation-prompt.md`. Related: [[feedback_check_issue_state_before_implementing_on_detached_head]], [[feedback_one_task_at_a_time]].
