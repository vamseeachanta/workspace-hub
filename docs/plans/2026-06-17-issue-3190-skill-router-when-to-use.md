# Plan for #3190: Provider-neutral skill router + when_to_use frontmatter (Codex/agy self-serve skills)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3190
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3190-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/ai/run_agent.py` (214 lines) — pure resolver + thin dispatch. `materialize_prompt()` (~144-160) renders advisory→enforced→agent prompt; this is the seam to prepend a matched skill. `main()` takes `--agent/--provider/--file/--execute` — **no query/skill input today**. `WRAPPERS` defines only `codex`, `gemini`, `claude`.
- Found: `config/agents/skill-graph-index.yaml` (511 lines; keys generated_at/source/by_domain/by_input_type/by_output_type/feed_chains) — a **curated ~51-skill subset**, NOT one entry per SKILL.md. No `when_to_use` (`grep -c` → 0).
- Found: `.planning/skills/skills-knowledge-graph.yaml` — the TRUE source the index regenerates from; 51 `- id:` nodes (repo/category/domain/input_types/output_types/capabilities). No `when_to_use`. **This is where `when_to_use` must live** (index is auto-generated, do-not-hand-edit).
- Found: `scripts/coordination/routing/lib/skill_graph.sh` — index generator + query CLI (`--rebuild-index`, `--capability "<q>"` fuzzy substring). Builds index from the knowledge graph, not by scanning `.claude/skills/`.
- Found: `scripts/agents/soul-runtime-lib.sh:7-29` — builds the FAMILY-level Skill index in AGENTS.runtime.md (deliberately family-level ~50 lines, not per-SKILL.md).
- Found: `config/agents/provider-capabilities.yaml` capability_bindings — providers claude/codex/gemini only. `tests/ai/test_run_agent.py` + `_oracle.py` — TDD harness (deterministic core + slow 3-provider oracle).

### Standards / LLM Wiki
Not applicable / none — harness routing.

### Documents consulted
Issue #3190 (3-part scope + cross-provider acceptance test); `config/agents/codex/AGENTS.runtime.md:173-195` (no-native-loader → family index contract); `skill_graph.sh` header (rebuild cmd + existing `--capability` fuzzy match = closest analog).

### Gaps identified
- `when_to_use` exists nowhere (`grep -rl '^when_to_use:'` → 0; not in graph or index).
- Only **402 of 3113** SKILL.md have a `## When to Use` section; 34 use `## Trigger`; rest neither → a parser must tolerate missing/variant sections.
- No provider-neutral router (closest is bash `skill_graph.sh --capability`, no provider/context_tags, not Python-callable).
- `run_agent.py` has no `--query`/`--context-tags` and no skill-prepend.
- **agy has no dispatch wrapper**; Hermes dispatches THROUGH the codex wrapper → "agy prepends the skill" only satisfiable transitively or deferred.

### Evidence
#3190 OPEN (parent #3058). Files verified. Counts: 46 families, 3113 SKILL.md, 402 with `## When to Use`, 34 `## Trigger`, 0 `when_to_use:` frontmatter. Gap proofs via grep empties. N/A reproduction (capability-build). Sources: 7.

---

## Approach / Deliverable
A provider-neutral `scripts/ai/skill_router.py` that ranks skills for `(query, provider, context_tags)` by reading `when_to_use` from the regenerated index (no rescanning 3113 files at dispatch), `when_to_use` populated in the source graph, and a `materialize_prompt` step in `run_agent.py` that prepends the top-ranked skill — so Codex/Hermes (via codex wrapper) + Gemini get the same match Claude would.

- Router ranks by query↔when_to_use token overlap + context_tags↔domain overlap; provider recorded for audit/phrasing, **not** used to re-rank (skills are provider-neutral); returns None on no match (fail-open).
- `run_agent.py`: add `--query`/`--context-tags`, call router, prepend `# Routed skill: <id> — read .claude/skills/<id>/SKILL.md` in `materialize_prompt`, record in manifest. No-`--query` path is byte-identical to today (back-compat).
- `skill_graph.sh --rebuild-index`: emit a flat router-friendly `skills:` block carrying id/domain/when_to_use (prefer a small Python helper over awk for the nested block).
- `.planning/skills/skills-knowledge-graph.yaml`: add `when_to_use:` to the 51 nodes (source of truth); optional `extract_when_to_use.py` seeds from existing sections.

## Files to change
Create: `scripts/ai/skill_router.py`, `tests/ai/test_skill_router.py`, optional `scripts/ai/extract_when_to_use.py`.
Modify: `scripts/ai/run_agent.py`, `tests/ai/test_run_agent.py`, `scripts/coordination/routing/lib/skill_graph.sh`, `.planning/skills/skills-knowledge-graph.yaml`, `docs/plans/README.md`. Regenerate: `config/agents/skill-graph-index.yaml`.

## TDD test list
router-loads-index; ranks-by-when_to_use-overlap; context-tags-boost; no-match-returns-none (fail-open); **provider-neutral (identical top id across codex/gemini/claude)**; tie-break-deterministic; extract-parses-section; extract-handles-Trigger-alias; extract-missing-section→[]; run_agent-prepends-matched-skill; run_agent-no-query-no-prepend (byte-identical back-compat); run_agent-manifest-records-skill; rebuild-index-emits-when_to_use. Red first.

## Risks / open questions
- **Risk (HIGH):** index covers only **51 curated skills**, not 3113. Router matches only those 51 unless the graph is expanded. **Decide at approval:** ship against the curated set (T3 as scoped) OR expand to full coverage (larger, separate sibling of #3058). This is the biggest scope risk.
- **agy/Hermes literalism:** no agy wrapper; Hermes via codex. Confirm "agy prepends skill" is satisfied transitively or deferred.
- **Parser robustness:** 402/3113 have the section → must fail-open on the rest.
- index is auto-generated → `when_to_use` MUST live in the source graph or it's wiped on rebuild.
- **Open:** provider affect ranking? Recommend NO (record for audit only). Top-1 vs top-k prepend? Plan: top-1 (prompt budget), manifest records top-k.

## Adversarial review (T3 — 3 providers)
PENDING. Force: coverage-mismatch (51 vs 3113 — accept curated subset or demand full?); agy/Hermes wrapper literalism; parser fail-open; back-compat byte-identical no-query path.

## Acceptance criteria
Mirror issue #3190: tests pass; no regression (no-query byte-identical); `when_to_use` populated for the 51 graph nodes; index regenerated with `skills:`+when_to_use (idempotent, no hand-edit); cross-provider determinism (codex vs gemini log SAME routed skill id); run_agent prepends matched skill (manifest + prompt); review artifacts posted.
