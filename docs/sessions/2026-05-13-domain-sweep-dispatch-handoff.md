# Domain Sweep Dispatch Handoff — 2026-05-13

This handoff covers the **18 research subissues across 3 domains** that need parallel execution by external accounts.

## Account 2 (Rigor Lane — Standards + Academic)

Open a fresh Claude/Codex/Gemini session and paste this prompt:

```
You are Account 2 in a multi-account Domain Knowledge Sweep workflow.

Repository: https://github.com/vamseeachanta/workspace-hub
Local path (if cloned): /mnt/local-analysis/workspace-hub

Your queue (process IN ORDER, commit after each, watch GraphQL quota):

1. https://github.com/vamseeachanta/workspace-hub/issues/2669 — R1 Hydrodynamics Standards
2. https://github.com/vamseeachanta/workspace-hub/issues/2670 — R2 Hydrodynamics Academic
3. https://github.com/vamseeachanta/workspace-hub/issues/2677 — R1 Mooring Standards
4. https://github.com/vamseeachanta/workspace-hub/issues/2678 — R2 Mooring Academic
5. https://github.com/vamseeachanta/workspace-hub/issues/2688 — R1 Pipelines Standards
6. https://github.com/vamseeachanta/workspace-hub/issues/2689 — R2 Pipelines Academic

For each issue:
1. Read the body: `gh issue view <NUM>`
2. Follow the scope and output format specified IN the issue
3. Write the deliverable to the path the issue names
4. Commit with: `research(<domain>): <stream> deliverable for #<NUM>`
5. Comment on the issue with the deliverable summary
6. Move to next

Rules (CRITICAL — do not violate):
- Conform to citation contract at .claude/rules/calc-citation-contract.md
- LinkedIn content FORBIDDEN as primary technical source (memory rule feedback_llm_wiki_concept_pages_need_public_references)
- Prefer free-access PDFs and DOIs where available
- Each standard entry needs: code_id, publisher, revision, title, scope
- Each academic source needs: author, title, year, DOI/ISBN, free-access URL, page/chapter pointers
- Watch quota: `gh api rate_limit --jq '.resources.graphql'`. If <100 remaining, STOP.
- IMPORTANT new rule from today's audit (memory feedback_silent_verdict_flip_defect_class):
  When cataloging a standard, capture both the EDITION/REVISION and the SECTION/CLAUSE,
  not just the code_id. Two implementations citing the same code_id can diverge
  numerically because they implement different sections/editions.

Parent context (read-only): #2667 (feature parent), #2668 (Hydro), #2676 (Mooring), #2687 (Pipelines)

Begin with #2669.
```

---

## Account 3 (Broader Lane — Industry + LinkedIn Marketing)

Open a fresh Claude/Codex/Gemini session and paste this prompt:

```
You are Account 3 in a multi-account Domain Knowledge Sweep workflow.

Repository: https://github.com/vamseeachanta/workspace-hub
Local path (if cloned): /mnt/local-analysis/workspace-hub

Your queue (process IN ORDER, commit after each):

1. https://github.com/vamseeachanta/workspace-hub/issues/2671 — R3 Hydrodynamics Industry
2. https://github.com/vamseeachanta/workspace-hub/issues/2672 — R4 Hydrodynamics LinkedIn (marketing surface)
3. https://github.com/vamseeachanta/workspace-hub/issues/2679 — R3 Mooring Industry
4. https://github.com/vamseeachanta/workspace-hub/issues/2680 — R4 Mooring LinkedIn (marketing surface)
5. https://github.com/vamseeachanta/workspace-hub/issues/2690 — R3 Pipelines Industry
6. https://github.com/vamseeachanta/workspace-hub/issues/2691 — R4 Pipelines LinkedIn (marketing surface)

For each issue:
1. Read the body: `gh issue view <NUM>`
2. Follow the scope and output format specified IN the issue
3. Write the deliverable to the path the issue names
4. Commit with: `research(<domain>): <stream> deliverable for #<NUM>`
5. Comment on the issue with the deliverable summary
6. Move to next

Rules (CRITICAL for R4 LinkedIn issues):
- LinkedIn issues (R4) are MARKETING SURFACE ONLY
- NEVER import technical content from LinkedIn into wiki / codebase docs
- R4 deliverable is purely outreach tracking — a YAML expert list
- For R3 (industry), prefer conference proceedings (OMAE, ISOPE, OTC), vendor docs, journals — these CAN be cited as technical sources
- Use WebFetch first for LinkedIn per memory feedback_webfetch_first_for_linkedin
- If WebFetch fails on LinkedIn → use claude-in-chrome browser tools (NOTE: subagents can't drive Chrome per memory; run on main session)
- Each LinkedIn expert needs: handle, name, role, expertise tags, outreach_priority
- Watch quota: `gh api rate_limit --jq '.resources.graphql'`. If <100 remaining, STOP.

Parent context (read-only): #2667 (feature parent), #2668 (Hydro), #2676 (Mooring), #2687 (Pipelines)

Begin with #2671.
```

---

## Account 1 (This Lane — Synthesis)

Account 1's queue is for the main session (this one) and runs AFTER Accounts 2/3 complete R1-R4 per domain:

- R5 Code audits: already complete (Hydro [#2673](https://github.com/vamseeachanta/workspace-hub/issues/2673), Mooring [#2681](https://github.com/vamseeachanta/workspace-hub/issues/2681), Pipelines [#2692](https://github.com/vamseeachanta/workspace-hub/issues/2692))
- R6 Synthesis (per domain): blocked on R1-R5 completion
  - [#2674](https://github.com/vamseeachanta/workspace-hub/issues/2674) Hydro R6
  - [#2682](https://github.com/vamseeachanta/workspace-hub/issues/2682) Mooring R6
  - [#2693](https://github.com/vamseeachanta/workspace-hub/issues/2693) Pipelines R6
