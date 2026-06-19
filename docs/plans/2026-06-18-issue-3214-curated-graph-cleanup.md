# Plan for #3214: reconcile curated skill graph (8 stale nodes) + fix the when_to_use boundary regression (43→1)

> **Status:** adversarial-reviewed (r1 Claude MAJOR → revised; flat-boundary fix replaced by depth-relative)
> **Complexity:** T2
> **Date:** 2026-06-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3214
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-18-plan-3214-claude.md

> Surfaced by #3208's coherence check. Two parts (independent):
> **A** = drop 8 stale curated nodes; **B** = a generator boundary fix (Part B turned out
> to be a **#3208 regression**, not 43 hand-edits — see Evidence).

---

## Resource Intelligence Summary

### Part A — 8 stale curated nodes (verified 2026-06-18)
Curated `.planning/skills/skills-knowledge-graph.yaml` references skills with no SKILL.md in the active tree (allowlisted in `check-skill-index-coherence.py` `KNOWN_STALE_CURATED`):
- **Archived (2)** — exist only under excluded `_archive/`: `digitalmodel/orcaflex-modeling`, `digitalmodel/orcaflex-post-processing` (`_archive/engineering/marine-offshore/...`). Archived ≠ active routing target → drop from the active graph.
- **Truly absent (6)** — no SKILL.md anywhere: `workspace-hub/agent-orchestration`, `workspace-hub/compliance-check`, `workspace-hub/sparc-workflow`, `workspace-hub/workspace-cli`, `digitalmodel/aqwa-analysis`, `assetutilities/pdf-utilities`.
- No active skill maps cleanly to any of the 8 (active digitalmodel skills are `orcaflex-reporting-fixture-proof-pattern`, `naval-architect-expert`, … — different) → **drop, not repoint.**
- **Graph entanglement:** all 8 appear in `nodes:` (defs) AND `edges:` (from/to, ~lines 757-983) AND `feed_chains`/domain lists (~1034-1121). Removing a node requires removing every edge that references it + every domain-list mention → **dangling-edge risk**.

### Part B — 43 "unrecognized heading" advisories are a #3208 REGRESSION (verified)
The 43 are NOT exotic headings — they are standard `## When to Use This Skill` followed immediately by a `### USE when:` subsection (sampled: slack-api, polars, dnv, docker, sphinx all match this shape). #3208 widened `_section`'s body boundary from `##` to `#{1,6}`, so capture now **stops at the `###` subsection → empty section text → falls through to backfill**. The original `##`-only boundary captured through subsections.
- **Empirical fix (tested, then reverted):** boundary `#{1,6}` → `#{1,2}` (stop only at next h1/h2, include `###/####` subsections): backfill **464 → 422** (recovers **42** skills' authored when_to_use); residual advisory **43 → 1** (only `github/github-repo-management`).

### Existing code
- `scripts/ai/build_skill_index.py:58-59` — the two `_section` patterns with the `#{1,6}` boundary (the regression site).
- `scripts/enforcement/check-skill-index-coherence.py` — `KNOWN_STALE_CURATED` (8 ids) to empty; (b) advisory + (c) determinism already in place.
- `config/agents/skill-graph-index.yaml` — generated `by_domain` view; regenerate via `scripts/coordination/routing/lib/skill_graph.sh --rebuild-index`.

### Gaps
- No integrity check that curated `edges`/`feed_chains` endpoints are defined nodes → dangling edges would pass silently after node removal.

### Evidence
- 8 stale: `find .claude/skills -type d -name <skill>` → 2 in `_archive`, 6 absent.
- Boundary fix: `build_skill_index.py --check | grep -c backfill` → 422 with `#{1,2}` vs 464 with `#{1,6}`; residual advisory = 1.

<!-- sources: issue + knowledge-graph + skill-graph-index + build_skill_index + check-skill-index-coherence + live measurements + sampled SKILL.md = 7 -->

---

## Deliverable

The curated graph references only skills that exist (8 stale nodes + their edges/feed-chains/domain entries removed, `by_domain` index regenerated, `KNOWN_STALE_CURATED` emptied, a new integrity check preventing future dangling edges); and the #3208 `_section` boundary regression is fixed so `## When to Use` sections include their subsections (42 skills' authored when_to_use recovered; advisory 43→1).

---

## Design

**Part B — rewrite `_section` with a DEPTH-RELATIVE boundary (r1-MAJOR-1/2; flat `#{1,2}` rejected).**
r1 measured that flat `#{1,2}` over-captures: an all-`###` file (`doc-audit-and-close-workflow`) has `### Trigger` swallow to EOF (322→2541 chars), and the exact-vs-prefix heuristic mis-binds `c-corp-rd-tax-strategy` (a Phase-5 `### When to Use` wins over the canonical `## When to Use This Skill`, amplified to 1049 chars). So neither `#{1,6}` (empty-capture → 42 lost) nor `#{1,2}` (over-capture) is right. Replace the regex pair with a small line-scanner:
```
_section(body, heading):
  scan lines for ATX headings `^\s*(#{2,4})\s+(title)$`
  candidates = headings whose title == heading (exact) or startswith heading + word-boundary (prefix)
  if none: return ""
  pick: prefer EXACT over prefix, then SHALLOWEST depth, then EARLIEST line   # fixes MAJOR-2
  d = matched heading depth; capture following lines until the next heading of depth <= d  # fixes MAJOR-1
  return normalized text
```
This stops a `##` section at the next `#`/`##` (keeps its `###` subsections), and a `### Trigger` at the next `###`+ (no EOF swallow). Regenerate `skill-index-full.yaml`; #3208 (c) determinism stays green after recommit. Expect backfill↓ (~42 recovered) WITHOUT the over-capture entries r1 found — add a capture-bound test (MAJOR-1 fix b).
- Residual advisory (`github/github-repo-management` + any remaining): normalize heading or accept advisory (Open Decision 1).

**Part A — graph surgery (r1-MAJOR-3/4 corrections folded in).** Structure is: the **knowledge-graph** (`skills-knowledge-graph.yaml`) hand-holds `nodes:`, `edges:`, a `coverage:` block (`coverage.*.skills` lists — lines ~1031-1153, NOT "feed_chains"), and a `stats:` block (lines ~1157-1169). The **generated** `skill-graph-index.yaml` holds `by_domain`/`by_input_type`/`by_output_type`/`feed_chains` (all awk-derived from nodes/edges → regen purges the 8 automatically).
- Remove the 8 `- id:` node blocks + every `edges[]` with a `from`/`to` in the 8 (filter programmatically by id, not by hand).
- Remove the 8 from the hand-edited `coverage.*.skills` lists (regen does NOT touch coverage).
- Update the hand-maintained `stats:` (`total_nodes` 51→43, `total_edges`, `edge_type_counts`) — or make it generated (MAJOR-4).
- Regenerate `skill-graph-index.yaml` (`skill_graph.sh --rebuild-index`).
- Empty `KNOWN_STALE_CURATED`.
- **New integrity check** (extend `check-skill-index-coherence.py`): every id in **all four** generated index sections (by_domain, by_input_type, by_output_type, feed_chains) AND every `edges[].from/.to` AND every `coverage.*.skills` id is a defined node id (no dangling refs). (a) now runs with an empty allowlist. Self-verifying + blocks future dangling refs (#3058).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/ai/build_skill_index.py` | boundary `#{1,6}`→`#{1,2}` (Part B regression fix) |
| Regenerate | `config/agents/skill-index-full.yaml` | backfill 464→422 |
| Modify | `.planning/skills/skills-knowledge-graph.yaml` | drop 8 nodes + their edges + feed_chains/domain refs |
| Regenerate | `config/agents/skill-graph-index.yaml` | by_domain view (skill_graph.sh --rebuild-index) |
| Modify | `scripts/enforcement/check-skill-index-coherence.py` | empty KNOWN_STALE_CURATED + add graph-integrity (no dangling edges) check |
| Modify | `tests/coordination/test_tier_table_no_drift.py`? no — | (n/a) |
| Create | `tests/enforcement/test_skill_graph_integrity.py` | dangling-edge + empty-allowlist + boundary-recovery tests |
| Modify | `.claude/skills/github/github-repo-management/SKILL.md` | normalize heading (if advisory→0 chosen) |
| Update | docs/plans/README.md | index |

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| test_section_recovers_subsection (B) | `## When to Use\n### USE when:\n<text>` → section-sourced | source=="section", text non-empty |
| test_section_h3_no_eof_overcapture (B/MAJOR-1) | all-`###` file: `### Trigger` stops at next `###`, not EOF | captured text excludes later `###` blocks |
| test_section_prefers_exact_shallow_earliest (B/MAJOR-2) | `## When to Use This Skill` + later `### When to Use` → binds the shallow canonical one | text from the `##` heading, not the `###` |
| test_section_word_boundary (B) | "When to Useful" does NOT match "When to Use" | no match |
| test_no_known_stale_curated (A) | allowlist emptied | KNOWN_STALE_CURATED == set() |
| test_coherence_passes_with_empty_allowlist (A) | (a) green after node removal | exit 0 |
| test_graph_no_dangling_refs (A/MAJOR-3) | edges from/to + ALL 4 index sections (by_domain/by_input_type/by_output_type/feed_chains) + coverage.*.skills → all defined node ids | no dangling |
| test_graph_no_dangling_refs_fails_on_injected_orphan (A) | the integrity check actually FAILS on a dangling ref | non-zero |
| test_stats_block_matches (A/MAJOR-4) | stats.total_nodes == len(nodes) | match |
| test_eight_ids_absent_from_index (A) | none of the 8 in skill-graph-index.yaml | absent |
| test_full_index_determinism_green (B) | (c) regen==committed (full index) | green |
| (note) graph-index equality assertions exclude the `generated_at` date line (MINOR-5) | | |

---

## Acceptance Criteria

- [ ] 8 stale nodes + their edges + feed_chains/domain refs removed; `skill-graph-index.yaml` regenerated; `KNOWN_STALE_CURATED` emptied
- [ ] Graph-integrity check (no dangling edges/domain refs) added + green; coherence (a)/(c) green with empty allowlist
- [ ] `_section` boundary fixed (`#{1,2}`); index regenerated (backfill ≤ 422; 42 recovered); advisory 43→1 (→0 if heading normalized)
- [ ] `uv run pytest tests/enforcement/ tests/coordination/ -q` green; no regression
- [ ] Review artifact posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-18:** verdict **MAJOR**, all reproduced empirically + folded in:

| # | Sev | Finding | Resolution |
|---|---|---|---|
| MAJOR-1 | MAJOR | flat `#{1,2}` over-captures (all-`###` `doc-audit` `### Trigger` → EOF, 322→2541; `subagent-sandbox` 409→3009). "42 recovered / strictly better" was false (46 changed) | replaced with **depth-relative** boundary (stop at next heading depth ≤ matched) + capture-bound test |
| MAJOR-2 | MAJOR | exact-vs-prefix mis-binds `c-corp-rd-tax-strategy` (Phase-5 `### When to Use` wins over canonical `## When to Use This Skill`), amplified by `#{1,2}` | pick prefers EXACT→SHALLOWEST→EARLIEST; regression test |
| MAJOR-3 | MAJOR | plan misdescribed structure: `feed_chains` is in the GENERATED index (+ by_input_type/by_output_type), not the graph; the graph has a hand-edited `coverage:` block regen won't clean | integrity check covers all 4 index sections + `coverage.*.skills`; coverage lists hand-cleaned |
| MAJOR-4 | MAJOR | hand-maintained `stats:` (total_nodes 51, edges 52) goes stale | update stats (or generate) + `test_stats_block_matches` |
| MINOR-5 | MINOR | graph-index `generated_at` date churn → flaky equality | exclude the date line in equality assertions |
| OK | — | empty-allowlist safe; index removal propagates via regen; baseline numbers (464/43/422) verified | — |

**r2 — Codex:** UNAVAILABLE (env timeout, repeated this session).

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR→addressed | boundary made depth-relative; exact-mis-binding fixed; integrity scope widened to all sections + coverage + stats |

---

## Risks and Open Questions

- **OPEN DECISION 1 — the 1 residual advisory** (`github/github-repo-management`): normalize its heading to a recognized form (advisory→0, trivial one-file edit) vs leave it advisory (non-blocking). Recommend **normalize** for a clean zero.
- **OPEN DECISION 2 — split or combined PR:** Part B (boundary fix, low-risk, recovers 42 skills now) vs Part A (graph surgery, higher-risk). Recommend **one PR, Part B first** (B de-risks A's index regen); but splittable if you prefer B to land immediately (it's a live router-quality regression).
- **Risk — Part A dangling refs:** removing 8 nodes risks orphans across edges + 4 generated index sections + hand-edited coverage lists. Mitigation: integrity check (widened per MAJOR-3) run BEFORE commit; edges/coverage filtered programmatically by id.
- **Risk — Part B over/under-capture:** the depth-relative boundary is the correct fix (r1-MAJOR-1); a capture-bound + exact-shallowest-earliest test guard it. The `_section` rewrite changes captured text for several entries → larger index diff (expected; regenerate + recommit).
- **Risk — Part B determinism:** regen the full index + recommit in the same PR or #3208 (c) flips red. Handled.
- **Note:** Part B fixes a #3208 regression — the live index currently under-serves ~42 skills' authored when_to_use to the router; worth landing promptly.
- **Resolved (r1):** flat-boundary over-capture (→ depth-relative); exact mis-binding (→ shallowest); integrity scope (→ all 4 sections + coverage); stats drift (→ update/generate); date-churn (→ exclude in assertions).

## Complexity: T2

**T2** — generator one-liner + index regen (low-risk) + graph surgery with a new integrity guard (higher-risk) + tests. Review = Claude inline (+ Codex if env permits; it has timed out repeatedly this session).
