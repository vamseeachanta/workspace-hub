# Plan for #2420: Restore repo-portfolio-steering balance snapshot contract and threshold behavior

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2420
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2420-claude.md | scripts/review/results/2026-04-20-plan-2420-codex.md | scripts/review/results/2026-04-20-plan-2420-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/repo-portfolio-steering/compute-balance.py` — parser currently looks for a `##/### By Category` table and `| harness | N |` rows in `.claude/work-queue/INDEX.md`.
- Found: `tests/skills/test_repo_portfolio_steering.py` — failing assertions expect `categories["harness"]`, `categories["engineering"]`, and threshold-driven `harness_status` behavior.
- Found: `.claude/work-queue/INDEX.md` currently contains only a compact legacy compatibility index with `Pending/Working/Done` counts and NO `By Category` table.
- Gap: the script's input contract and the actual current index format have drifted apart, so the parser returns `{}` for categories and the threshold tests become meaningless.

### Standards
| Standard | Status | Source |
|---|---|---|
| Repo skill/runtime issue only — no external engineering standard applies | not applicable | issue/test corpus |

### LLM Wiki pages consulted
- No relevant wiki pages; this is a local script/test contract issue.

### Documents consulted
- Issue #2080 — umbrella stale-skill-test bucket.
- Issue #2420 — behavioral regression child issue scoped to repo-portfolio-steering.
- `tests/skills/test_repo_portfolio_steering.py` — documents the expected output contract as acceptance tests.
- `.claude/work-queue/INDEX.md` — current input file does not match what the parser expects.

### Gaps identified
- No explicit contract says whether `compute-balance.py` should still parse the legacy index, the new canonical queue surface, or a fallback chain.
- No fixture-backed test covers the current real-world `INDEX.md` compatibility shape.
- Current threshold assertions are coupled to category parsing success, so one parser miss cascades into multiple failures.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-04-20 via `gh issue view`):
- `#2080` — OPEN — umbrella stale skill tests issue
- `#2420` — OPEN — repo-portfolio-steering behavior child issue

**File existence**:
- EXISTS: `scripts/skills/repo-portfolio-steering/compute-balance.py`
- EXISTS: `tests/skills/test_repo_portfolio_steering.py`
- EXISTS: `.claude/work-queue/INDEX.md`

**Line excerpts / observed facts**:
- `compute-balance.py` parses only a `By Category` table via regex `| <word> | <number> |` after a `##/### By Category` heading.
- `tests/skills/test_repo_portfolio_steering.py` expects `harness` and `engineering` counts and threshold-based `harness_status` changes.
- `.claude/work-queue/INDEX.md` currently contains:
  - `# Legacy Work Queue Index`
  - `## Pending (1)`
  - `## Working (0)`
  - `## Done (1)`
  and no `By Category` heading or `| harness | ... |` rows.

This proves the current parser/input contract is broken on current repo state.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2420-repo-portfolio-steering-contract.md` |
| Source module | `scripts/skills/repo-portfolio-steering/compute-balance.py` |
| Tests | `tests/skills/test_repo_portfolio_steering.py` |
| Current input surface | `.claude/work-queue/INDEX.md` |
| Canonical queue surface reference | `notes/agent-work-queue.md` (named in current INDEX compatibility header) |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2420-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2420-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2420-gemini.md` |

---

## Deliverable

A corrected repo-portfolio-steering contract in which `compute-balance.py` and its tests agree on the current source-of-truth input format and produce meaningful category/threshold results on present-day repo state.

---

## Pseudocode

```
inspect current queue data sources
choose one contract explicitly:
    option A: keep INDEX.md as source and regenerate/parse a category section reliably
    option B: switch compute-balance to the current canonical queue surface
    option C: support fallback chain with explicit precedence
encode the chosen source contract in code comments and tests
add/adjust fixture or real-file assumptions so parser success is test-covered
verify threshold behavior only after category extraction is proven valid
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/repo-portfolio-steering/compute-balance.py` | align parser and threshold logic to current source contract |
| Modify | `tests/skills/test_repo_portfolio_steering.py` | make the expected contract explicit and fixture-backed |
| Optional modify | `.claude/work-queue/INDEX.md` or queue-refresh generator | only if the chosen fix restores a required category surface there |
| Update | `docs/plans/README.md` | add this plan row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_balance_source_contract_matches_current_queue_surface` | parser reads the chosen real source correctly | current queue source or fixture | non-empty category map |
| `test_balance_snapshot_parses_categories` | `harness` and `engineering` are extracted when present by contract | fixture/current source | both keys present |
| `test_harness_threshold_default` | default threshold returns deterministic status | parsed category map | expected status |
| `test_harness_threshold_custom` | threshold override changes status only as intended | same parsed category map | OVER-INVESTED at 0.0, HEALTHY at 1.0 or documented equivalent |
| `test_missing_source_is_handled_gracefully` | absent/legacy source yields explicit fallback behavior | missing/empty source | documented fallback result |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/skills/test_repo_portfolio_steering.py -q` passes
- [ ] The chosen input source for category counts is explicit in code and tests
- [ ] Category extraction works against current repo state or an explicitly maintained fixture representing current repo state
- [ ] `harness_status` threshold behavior is tested independently of parser failure noise
- [ ] The fix does not silently depend on a vanished `By Category` section without documenting how that section is produced

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not run yet |
| Codex | PENDING | not run yet |
| Gemini | PENDING | not run yet |

**Overall result:** PENDING — review not yet run.

---

## Risks and Open Questions

- **Risk:** fixing only the test could preserve a useless parser that still does nothing on real repo state.
- **Risk:** fixing only the parser without declaring a source-of-truth contract could rebreak on the next queue refresh change.
- **Open:** should this skill consume `notes/agent-work-queue.md` instead of the legacy compatibility `INDEX.md`?
- **Open:** if `INDEX.md` must remain supported, where is the authoritative generator for the `By Category` section now?

---

## Complexity: T2

**T2** — one script, one test module, and possibly one generated-input contract need coordinated correction, but the issue is bounded to a single behavioral subsystem.
