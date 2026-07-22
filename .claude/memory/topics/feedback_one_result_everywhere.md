> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_one_result_everywhere.md

---
name: feedback_one_result_everywhere
description: Standing rule — present ONE result everywhere (no model/version labels or duality) until the user explicitly adds more
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 468a3d4d-74ba-473e-b6c7-e195d94a7036
---

**"For now, we only have one result everywhere until things change explicitly from the user."** (owner, 2026-07-12)

Standing presentation rule for results the user's audiences see — website (aceengineer.com),
Hugging Face datasets, client pages, PDFs, the Field Explorer. Present a **single authoritative
result** with clean product language. Do NOT surface: model/version labels (V30, V50), duality
("latest vs frozen reference"), or internal-method jargon ("sanctioned", "frozen", "benchmark") on
these client/website/HF surfaces.

**Why:** today there is exactly one methodology and one set of results (wed V50-latest, per the
World Oil April 2026 validation). Versioning/plurality is an internal concern, not a client one —
exposing it reads as unfinished or confusing.

**How to apply:**
- Client/website/HF surfaces → say just "economics" / "field results" / "performance". Keep
  `V30 / V50 / frozen / benchmark / sanctioned` ONLY as internal validation & reproducibility terms
  in tests and audit baselines (e.g. `golden_baseline_v30.yml`), never rendered to a user.
- Do NOT pre-build multi-model / versioned scaffolding, selectors, or "choose a model" UI on spec.
  Add plurality ONLY when the user explicitly says a second model/result is being introduced.
- When that day comes it's an explicit, owner-gated change — until then, one result is the default
  and the simplification, not a temporary hack.

**Corollary (owner, 2026-07-12): new results must "pop" live immediately from the pending/hanging
phase — no manual staging gate.** When a new result (or a previously-`pending` field, e.g. a
"reserves pending" placeholder that gets its data) becomes available, it should surface into the
single live view automatically, not sit staged/withheld. This is the self-perpetuating pipeline
(EPIC `wh#3485`: publish a result + one `capabilities.yaml` line → CI carries it to website/HF).
So: build the results flow so adding data auto-promotes it to the live single result; don't leave
new results parked in a hanging/pending state waiting on a hand-publish.

**Staleness / multi-value decision rule (owner, 2026-07-12):** new results pop; stale results are
superseded (they sit "under" the current one, not surfaced). Where more than one candidate value
still exists and you must collapse to the ONE displayed result, use a **simple, consistent,
conservative default — the lowest number (or a consistent combination)** — NOT elaborate
reconciliation logic. Keep it deliberately simple: **"we'll progress this further when we really
see a use case for it."** Don't build a sophisticated selection/aggregation engine on spec; a
consistent conservative pick is the placeholder policy until a concrete need appears.

Applied in [[project_wed971_economics_life_to_date_fix.md]] (#981 dropped V30 framing; wed#982 +
the "drop frozen/benchmark from website-facing results" refinement carry it the rest of the way).
Related: [[feedback_placeholder_links_to_filing_issue]] (honest "pending", never a fabricated
value) — a single result can still say "not available yet" rather than invent one.
