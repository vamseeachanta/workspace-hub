# Plan for #3190: Provider-neutral skill router + when_to_use (full-tree coverage, first-class agy dispatch)

> **Status:** draft (re-planned for expanded scope; adversarial review PENDING)
> **Complexity:** T3
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3190
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3190-claude.md | ...-codex.md | ...-gemini.md

> **Operator decisions (2026-06-17) folded in:** (1) FULL-tree coverage — router covers all 3113 SKILL.md, not the 51 curated nodes; (2) FIRST-CLASS agy dispatch wrapper (agy as its own lane, not via codex).

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/run_agent.py` (215) — `WRAPPERS` (44-48) = codex/gemini/claude only; `materialize_prompt()` (145-160) is the prepend seam; `dispatch_run()` shells `bash <wrapper> --file --prompt` with per-provider env; `--provider` is `choices=sorted(WRAPPERS)` so adding a key auto-extends the CLI. No `--query`/skill input today.
- `scripts/review/submit-to-gemini.sh` — the wrapper contract to mirror (`--file`/`--prompt`, execs `$GEMINI_CMD -p ... --yolo --output-format json`). agy has no equivalent.
- `config/agents/skill-graph-index.yaml` (curated 51-node projection) + `.planning/skills/skills-knowledge-graph.yaml` (51 hand-authored nodes) — cover **51 of 3113** SKILL.md; no `when_to_use`.
- `scripts/coordination/routing/lib/skill_graph.sh` — awk index generator from the 51-node graph (does NOT scan `.claude/skills/`); extending awk to 3113 is brittle.
- `scripts/agents/soul-runtime-lib.sh:4-43` — the ONLY `.claude/skills/` scanner, deliberately FAMILY-level (~46 lines), explicitly "NOT one line per nested SKILL.md (1000+)". Precedent: per-SKILL data lives in a SEPARATE generated artifact, never inlined into runtime.
- `scripts/agents/set-antigravity-default-model.sh` + `scripts/ai/assessment/agy-usage-snapshot.py` — agy = Antigravity CLI, Gemini-backed, **interactive TUI**: model pinned via settings file "read on launch", quota only in the `/usage` panel. No headless/exec/`-p`/stdin mode anywhere.

### Standards / LLM Wiki
Not applicable / none.

### Evidence (live counts 2026-06-17, supersede prior draft)
46 families; **3113** SKILL.md; **329** with `## When to Use`; **33** with `## Trigger`; **3** with `when_to_use:` frontmatter; ~2751 with neither. agy headless grep → only model-pin + usage-snapshot; **no dispatch invocation exists**. Sources: 9.

### Gaps
Source graph + index cover 51/3113; `when_to_use` near-absent (3 frontmatter); no `.claude/skills/`-scanning per-SKILL index generator; **no agy dispatch path** (absent from WRAPPERS + provider-capabilities + no headless CLI); run_agent.py has no `--query`/prepend.

---

## Approach / Deliverable
Provider-neutral `scripts/ai/skill_router.py` ranking ALL skills for `(query, provider, context_tags)` from a NEW generated `config/agents/skill-index-full.yaml` (one flat entry per SKILL.md: id/family/domain/when_to_use/when_to_use_source), produced by a new `scripts/ai/build_skill_index.py` that scans `.claude/skills/`; a `materialize_prompt` prepend in `run_agent.py`; and **`agy` added as a first-class `WRAPPERS` provider**.

### 1. Full-tree coverage
- **New artifact `config/agents/skill-index-full.yaml`** (NOT extending the curated graph — that would destroy its edge/feed-chain semantics + break awk regen). Router reads the full index; curated graph stays the source for edge queries.
- **Generator `build_skill_index.py` (Python, not awk):** walk `.claude/skills/**/SKILL.md` (exclude `_archive*`/`_*` families per soul-runtime precedent); `when_to_use` by 3-tier precedence, each tagged `when_to_use_source`: (1) `when_to_use:` frontmatter (3); (2) `## When to Use` section (329); (3) `## Trigger` (33); (4) **backfill** from frontmatter name+description+family (~2751). Idempotent: sorted by id, date-pinned `generated_at` (not timestamp), normalized whitespace → byte-stable unless a SKILL.md changes. ~1-2s build, on-demand (not at dispatch).
- Curated 51 get authored `when_to_use` in `skills-knowledge-graph.yaml` (survives rebuild); full tree derived at build time. Progressive curation: an author adds `when_to_use:`/`## When to Use` → picked up next build (no mass edit).

### 2. First-class agy wrapper — with an honest infeasibility fallback
- Add `agy` → `scripts/review/submit-to-agy.sh` to `WRAPPERS` + an `agy` env branch in `dispatch_run()`. `--provider` choices auto-extend; `materialize_prompt` prepends identically → matched skill prepended for agy **directly, not via codex**.
- **INFEASIBILITY FLAG:** agy has NO documented headless dispatch (interactive TUI only). So `submit-to-agy.sh` **cannot** mirror `submit-to-gemini.sh`'s `-p` exec today.
- **Fallback (ship this):** `submit-to-agy.sh` materializes the skill-prepended prompt to a tracked artifact and **fails closed (exit 3)** with a clear message ("agy has no headless dispatch; prompt written to <path> for manual paste"). agy is first-class in WRAPPERS + router (skill IS prepended), honest about the limitation, one-line flip to real exec when agy ships a headless flag. Verify `agy --help` at build time; if a headless mode exists, wire it and drop the fallback. File a follow-on for real agy headless dispatch.

### 3. Router + 4. integration
- `skill_router.py`: rank by query↔when_to_use overlap + context_tags↔domain/family; **down-weight `source: backfill`**; provider recorded for audit, NOT used to re-rank; None on no match (fail-open); deterministic tie-break by id (cross-provider determinism).
- `run_agent.py`: add `--query`/`--context-tags`; on match prepend `# Routed skill: <id> — read .claude/skills/<id>/SKILL.md`; record `routed_skill`+source+top-k in manifest. **No-`--query` path byte-identical to today.**

## Files to change
Create: `scripts/ai/skill_router.py`, `scripts/ai/build_skill_index.py`, `scripts/review/submit-to-agy.sh`, `config/agents/skill-index-full.yaml` (generated), `tests/ai/test_skill_router.py`, `tests/ai/test_build_skill_index.py`.
Modify: `scripts/ai/run_agent.py` (agy wrapper+env, --query/--context-tags, prepend, manifest), `tests/ai/test_run_agent.py`, `config/agents/provider-capabilities.yaml` (add agy to capability_bindings, advisory, mirrors gemini), `.planning/skills/skills-knowledge-graph.yaml` (when_to_use for curated 51), `docs/plans/README.md`. Regenerate `config/agents/skill-graph-index.yaml`.
NOT changing: `soul-runtime-lib.sh` (family index stays compact); `skill_graph.sh` awk NOT extended to 3113 (separate Python generator).

## TDD test list
**build_skill_index:** scans-all (count==find); prefers-frontmatter; falls-back-to-section; falls-back-to-Trigger; backfills (source: backfill); excludes _archive/_; sorted-by-id; idempotent-byte-stable.
**skill_router:** loads-full-index; ranks-by-overlap; context-boost; backfill-down-weighted; no-match-None; **provider-neutral identical top id across codex/gemini/claude/agy**; tie-break-by-id.
**run_agent:** agy-valid-provider; agy-uses-submit-to-agy.sh (NOT codex); prepends-matched-skill; no-query-byte-identical; manifest-records-routed_skill+source; agy-wrapper-fails-closed-with-artifact (asserts exit 3 + message). Red first.

## Risks / open questions
- **HIGH — agy headless infeasibility:** all evidence = interactive TUI. Fail-closed wrapper + verify `agy --help` + follow-on for real exec. **Operator: accept fail-closed agy (artifact + manual paste) for now, or descope agy until it ships headless?**
- **HIGH — backfill quality:** ~88% (~2751/3113) when_to_use auto-derived → noisy matches. `source` tagging + down-weight + progressive curation; acceptance must not require high-fidelity matches for backfilled skills.
- **MED — index churn** (3000-line YAML): sorted/date-pinned/normalized; regenerate only on SKILL.md change.
- **MED — two index artifacts** (curated graph vs full index): document the split.
- **Open:** provider affects ranking? NO (audit only; only source-tier scores). Top-1 prepend (manifest records top-k).

## Adversarial review (T3 — 3 providers) — PENDING (re-plan not yet reviewed)
Force: agy-headless fail-closed acceptable vs block; backfill-noise acceptance threshold; two-index coherence; churn/idempotency at 3113; back-compat byte-identical; provider-neutral determinism across all FOUR providers incl. agy.

## Acceptance criteria
Both expansions: tests pass; no-query byte-identical; `skill-index-full.yaml` one entry per non-archived SKILL.md with when_to_use+source for ALL (idempotent); curated 51 authored in graph + index regenerated; **agy first-class in WRAPPERS, prepends skill via submit-to-agy.sh (not via codex), cross-provider top-id identical across codex/gemini/claude/agy**; agy headless infeasibility documented + fail-closed verified (or real exec wired) + follow-on filed; review artifacts posted.
