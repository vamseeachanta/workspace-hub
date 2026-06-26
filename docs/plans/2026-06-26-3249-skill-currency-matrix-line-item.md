# Plan for #3249: cross-provider skill-currency matrix line item (PRIMARY)

> Epic: #3248 · Client: N/A · Project: N/A · Status target: `status:plan-review`
> Future-tense plan. **Revised after T1-adversarial review (2026-06-26) — verdict was NON-APPROVE on
> the v1 naive count+hash model; this v2 redesigns around expected-divergence set-diff.** Nothing
> below exists yet unless cited as existing.

## Resource Intelligence Summary

Closes gaps #2/#4 of epic #3248: nothing currently audits whether each AI provider's skill surface
still matches canonical, so skills drift per provider with no alert. This adds a `skill_currency`
line item to the matrix — sibling to `session_curation` (#3246) for *wiring*, but with a
fundamentally different verdict model (set-diff vs canonical with an expected-divergence allowlist,
**not** a naive count/hash).

### Existing repo code (reuse)
- `scripts/readiness/build-equality-matrix.py` — verdict engine. TWO patterns to mirror: (a) the
  `session_curation` dimension wiring (group/CSS/severity/OK/remediate/legend); (b) **critically**,
  the `provider_harness` `expected_divergence` model (`:54` `EXPECTED_DIVERGENCE_REASONS`, `:250-252`)
  — the skill-currency verdict reuses this *concept* so legitimate provider-specific skills don't red.
- `scripts/readiness/collect-equality.sh:138` — existing `skills` cell counts `find -maxdepth 3`
  → **416** first-class skills. The new audit MUST use the same counting unit (family-level), not
  full-depth (which yields 3189 vendored/nested leaves).
- `collect-equality.sh:212` — provenance `MEASURED` allowlist includes `.claude/skills` + `.codex/skills`.
- `config/scheduled-tasks/...`, `.claude/skills-index.yaml` (lists every skill `path:`), `harness-config.yaml`.

### Evidence (verified on dev-primary, 2026-06-26 — corrected per review)
- `.claude/skills/` = 3189 leaf SKILL.md / **416 at maxdepth-3** (canonical).
- `.agents/skills/` (Gemini) has **7 top-level families canonical lacks** —
  `source-command-{compound-extended,gsd-from-gsd2,gsd-join-discord,gsd-review-backlog,gsd-workstreams,
  learn-extended}`, `workspace_hub_learned` — these are **legitimate Gemini-CLI command-sourced
  skills**, the same class already encoded as `gemini_skill_dispatch_unsupported` expected-divergence.
  The net −33 leaf delta is **NOT staleness** → must NOT grade red. (This corrects v1's false premise.)
- `.codex/skills` is a **tracked symlink → ../.claude/skills**; `find -name SKILL.md` (no `-L`) and
  `os.walk` (no `followlinks`) return **0** under it. On Windows (`core.symlinks=false`, unset here →
  false on the Windows boxes) the symlink materializes as a ~17-byte text file → also 0.
- Hermes external dir = `<ws>/.claude/skills` (`harness-config.yaml:120`) = **canonical itself** →
  a hermes-vs-canonical cell is tautological.
- `.claude/skills-index.yaml` enumerates `categories→skills→{name,description,path}` for every skill.

### Gaps identified (in the v1 design, now fixed)
- Naive count/hash can't separate "stale" from "legitimate provider extras" → permanent false red.
- Symlinked / symlink-as-text surfaces under-count to 0 → false drift.
- mtime-based index freshness is non-deterministic on fresh checkouts.
- `is_stale` masks the cell exactly during skill development (when drift matters most).

## Deliverable
A `skill_currency` matrix cell per machine grading the worst of:
- **Gemini surface drift** vs canonical, computed as a *set-difference of skill-family relpaths*,
  with `EXPECTED_SKILL_DIVERGENCE` (per-provider allowlist of permitted extra/missing prefixes,
  sourced from `harness-config.yaml`) subtracted first. Red only on **unexpected** differences.
- **Index integrity**: `set(index paths)` vs `set(tree skill relpaths)` — non-empty symmetric
  difference ⇒ index stale. (mtime is never used.)
- **Codex / Hermes**: graded `present`/`absent` only (both alias or curate-subset canonical) —
  never count-compared.

Verdicts: `SKILLS-CURRENT` (green), `SKILLS-DRIFTED` (red, unexpected diff), `SKILLS-INDEX-STALE`
(orange), `EXPECTED-DIVERGENCE` (purple, allowlisted extras), `MISSING-EVIDENCE`.

## Pseudocode (engine — scripts/curation/audit_skill_currency.py)
```
def families(dir):  # family-level, symlink-safe, Windows-safe
    if not isdir(dir) or is_symlink_materialized_as_text(dir): return None  # → MISSING-EVIDENCE
    return { relpath of each dir containing a SKILL.md, walked with followlinks=True,
             to maxdepth 3 }                       # matches the existing skills cell unit

canon = families(.claude/skills FROM COMMITTED TREE)   # `git show HEAD` view, not working tree,
                                                       # so uncommitted WIP can't blind the compare
gemini = families(.agents/skills)
allow  = harness-config EXPECTED_SKILL_DIVERGENCE[gemini]   # e.g. ["source-command-", "workspace_hub_learned"]
unexpected = (gemini ^ canon) minus anything matching an allow prefix
index_paths = { path in skills-index.yaml }
index_diff  = index_paths ^ { tree skill relpaths }
state = { machine, audited_at, canon_count,
          gemini:{present, unexpected_count, expected_count},
          codex:{present}, hermes:{present},
          index_stale: bool, worst_verdict }
```
Verdict precedence: MISSING-EVIDENCE > SKILLS-DRIFTED(unexpected≠∅) > SKILLS-INDEX-STALE >
EXPECTED-DIVERGENCE(only allowlisted extras) > SKILLS-CURRENT.

## Files to Change
- NEW `scripts/curation/audit_skill_currency.py`
- EDIT `scripts/readiness/build-equality-matrix.py` (dimension, `skill_currency_verdict`, group, CSS, severity, OK set, remediate, legend)
- EDIT `scripts/readiness/collect-equality.sh` **AND `collect-equality.ps1`** (§6c emit block — the `.ps1` contract test requires parity) + fixture + `test_collect_equality_ps1_schema.py` (EXPECTED_DIMS → 12)
- EDIT `config/readiness/harness-config.yaml` (add `expected_skill_divergence:` allowlist)
- EDIT `config/scheduled-tasks/schedule-tasks.yaml` (fold audit into the session-curation wrapper — same 6h cadence)
- EDIT `.gitignore` (allowlist `skill-currency-*.json`)
- NEW `tests/readiness/test_skill_currency.py`

## TDD Test List
1. SKILLS-CURRENT when gemini surface == canonical (after allowlist) + index integral.
2. SKILLS-DRIFTED only on an **unexpected** family diff (an allowlisted `source-command-*` extra ⇒ NOT red).
3. EXPECTED-DIVERGENCE when the only diffs are allowlisted prefixes.
4. SKILLS-INDEX-STALE on index-path-set ≠ tree-path-set (mtime never consulted).
5. Symlinked surface (followlinks) counts correctly; symlink-materialized-as-text ⇒ MISSING-EVIDENCE (not 0-drift).
6. Codex/Hermes graded present/absent, never count-compared.
7. Compare uses committed tree (`git show HEAD`) — an uncommitted new skill does NOT flip the verdict.
8. Wiring: dimension in DISPLAY_DIMS, group present, severity/OK ordering.

## Acceptance Criteria
- Matrix renders a `skill_currency` cell + group + legend (5-verdict family).
- On dev-primary today, the Gemini delta grades **EXPECTED-DIVERGENCE (purple)** — NOT red — because
  every extra family is allowlisted. (Corrects v1's wrong "33 drift = red success".)
- A deliberately-introduced *unexpected* skill removal grades `SKILLS-DRIFTED` in a test.
- Symlinked `.codex/skills` does not produce false drift.
- All existing readiness tests stay green; no abs-path/token leak.

## Adversarial Review Summary
**v1 verdict: NON-APPROVE** (T1, Claude; codex/gemini wrappers CPU-starved → T2 degraded to T1, logged).
Must-fixes folded into v2:
1. ✅ Expected-divergence-aware set-diff replaces count+hash (Blocker 1+4); allowlist in harness-config.
2. ✅ Drop Hermes + repo-`.codex` as graded surfaces (alias canonical); `followlinks=True` + symlink-as-text guard (Blocker 2).
3. ✅ Index freshness = index-paths-vs-tree set-diff, mtime removed (Blocker 3).
4. ✅ Family-level counting (maxdepth-3, matches existing `skills` cell) not 3189 leaves (Major 4).
5. ✅ Codex present/absent not count-baseline (Major 5).
6. ✅ Compare committed tree (`git show HEAD`) so skill-dev WIP doesn't blind it; document grey≠fine (Major 6).
7. ✅ `.ps1` added to Files-to-Change; complexity raised (Minor 7).
**v2 needs a fresh adversarial pass before implementation.**

## Risks and Open Questions
- Q1: allowlist maintenance — when Gemini adds a new command-sourced family, the cell reds until the
  allowlist is updated. Acceptable (an intentional review prompt) or auto-learn? (lean: manual, it's the point.)
- Q2: `git show HEAD` view adds git calls per run — bound/cached; confirm cost on the 6h cadence.
- Q3: cross-machine comparability — `skill_currency` is a per-box "this box's surfaces vs its own
  canonical" signal; it is NOT voted across machines (like cold dims). Document as per-box.

## Complexity: T3 (raised from T2 per review)
Wiring is T2, but the engine (committed-tree diff, allowlist, symlink/Windows-safe family walk,
index set-diff) is materially more than the `session_curation` log-scan. Needs the full T2/T3 review depth.
