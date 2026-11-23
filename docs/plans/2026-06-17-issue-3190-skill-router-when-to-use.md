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

### 2. agy: first-class in the ROUTER, `unsupported` for DISPATCH (corrected per review)
agy has NO documented headless dispatch (interactive TUI only). The original "fake exit-3 wrapper in WRAPPERS" design was **rejected by review** — it would let a user pick `--provider agy`, get a recorded failure, yet `main()` returns 0 → *fake success*. Corrected design (architecturally consistent with how `gui_automation` etc. already fail closed):
- **Do NOT add a fake wrapper to `WRAPPERS`.** Instead mark agy `enforcement: unsupported` for the dispatch capability in `config/agents/provider-capabilities.yaml`, so `resolve_capabilities()` **raises before dispatch** (the existing fail-closed path; `tests/ai/test_run_agent.py` already covers unsupported→raise).
- agy IS first-class in the **router** (`skill_router.py` ranks identically for any provider token incl. agy) — the skill match is computed for agy; only headless *execution* is unsupported.
- **Pre-flight gate:** a Level-2 `check-agy-headless-capability.sh` probes `agy --help`; agy is promoted to a real `WRAPPERS` provider (mirroring `submit-to-gemini.sh`) ONLY when headless is detected. Follow-on issue filed for that flip.
- **Also fix `main()` exit propagation:** when `--execute` dispatches, return the wrapper's `exit_code` (today `main()` always returns 0, hiding dispatch failures) — with a test.

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
- **HIGH — agy headless infeasibility: RESOLVED (operator 2026-06-17 = accept fail-closed agy).** Ship the fail-closed `submit-to-agy.sh` (writes skill-prepended prompt artifact + exit 3 for manual paste); verify `agy --help` at build time; file a follow-on to wire real exec when agy ships a headless flag. agy stays first-class in WRAPPERS + router.
- **HIGH — backfill quality:** ~88% (~2751/3113) when_to_use auto-derived → noisy matches. `source` tagging + down-weight + progressive curation; acceptance must not require high-fidelity matches for backfilled skills.
- **MED — index churn** (3000-line YAML): sorted/date-pinned/normalized; regenerate only on SKILL.md change.
- **MED — two index artifacts** (curated graph vs full index): document the split.
- **Open:** provider affects ranking? NO (audit only; only source-tier scores). Top-1 prepend (manifest records top-k).

## Adversarial review (T3 plan-stage) — DONE, findings folded in
1 adversarial lens run 2026-06-17 (REJECT; 2 BLOCK + 1 REJECT + 2 MED). Resolutions:
- **BLOCK — agy fake-wrapper hides failure.** FIXED: agy is `enforcement: unsupported` for dispatch (raises before dispatch), NOT a fake exit-3 wrapper; first-class in the router only. (§2 rewritten.)
- **BLOCK — `main()` swallows dispatch exit code** (always returns 0). FIXED: propagate the wrapper exit_code on `--execute`; test added.
- **REJECT — backfill acceptance unmeasurable.** FIXED: concrete down-weight (backfill score ×0.2) + measurable acceptance — for a fixed sample of ~20 common queries, top-3 must include ≥1 non-backfill OR the backfill hit must have strong (>N-char) overlap; `test_backfill_top_k_quality` enforces it.
- **MED — two-index drift.** FIXED: `check-skill-index-coherence.sh` (curated 51 ⊆ full index; authored when_to_use not silently overridden) + CI check; document the split in `config/agents/README.md`.
- **MED — idempotency unverified at 3113.** FIXED: lock `yaml.safe_dump(sort_keys=True, default_flow_style=False, allow_unicode=True)` + trailing newline; `test_index_byte_stable_on_rerun` generates twice and diffs.
- **Clarify:** "no-`--query` byte-identical" = the dispatch/prompt path (CLI `--help` text changes with new args, acceptable). provider-neutral test asserts the ROUTER ignores provider in ranking (agy top-id == gemini top-id) — router-level, since agy never dispatches.
Cross-provider (Codex/Gemini) fanout recommended at code stage.

## Acceptance criteria
Both expansions: tests pass; no-query byte-identical; `skill-index-full.yaml` one entry per non-archived SKILL.md with when_to_use+source for ALL (idempotent); curated 51 authored in graph + index regenerated; **agy first-class in WRAPPERS, prepends skill via submit-to-agy.sh (not via codex), cross-provider top-id identical across codex/gemini/claude/agy**; agy headless infeasibility documented + fail-closed verified (or real exec wired) + follow-on filed; review artifacts posted.
