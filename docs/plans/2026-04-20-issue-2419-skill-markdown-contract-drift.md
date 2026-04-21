# Plan for #2419: Reconcile skill markdown contract drift in dark-intelligence/doc-extraction/research-literature/parity tests

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2419
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2419-claude.md | scripts/review/results/2026-04-20-plan-2419-codex.md | scripts/review/results/2026-04-20-plan-2419-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `tests/skills/test_dark_intelligence_workflow.py` — expects old dark-intelligence contract details: namespaced `related_skills`, seven explicit `Step N` headings, legal-gate text, archive schema fields, and TDD template markers.
- Found: `tests/skills/test_doc_extraction_skill.py` — asserts content taxonomy and naval-architecture heuristics that the current doc-extraction skill tree no longer fully exposes in top-level files.
- Found: `tests/skills/test_research_literature.py` — expects a `## 5-Step Workflow` section and `query-ledger.py` references, while the current skill declares an `## 8-Step Workflow` and no longer mentions that script.
- Found: `tests/skills/test_repo_skill_parity_merges.py` — regression test for earlier parity-merges work; current failures target missing sections/phrases in repo-local copies of `writing-plans`, `dspy`, and `systematic-debugging`.
- Found: current skill files diverge materially from test expectations:
  - `.claude/skills/data/dark-intelligence-workflow/SKILL.md`
  - `.claude/skills/data/research-literature/SKILL.md`
  - `.claude/skills/engineering/doc-extraction/SKILL.md`
  - `.claude/skills/engineering/doc-extraction/naval-architecture/SKILL.md`
- Gap: there is no explicit decision record for which assertions are stale tests versus real skill regressions.

### Standards
| Standard | Status | Source |
|---|---|---|
| Harness/skill regression issue only — no external engineering standard applies | not applicable | issue/test corpus |

### LLM Wiki pages consulted
- No relevant wiki pages; this is repo skill/test maintenance.

### Documents consulted
- Issue #2080 — umbrella stale skill-test bucket; now split for content drift vs behavior regression.
- Issue #2419 — child issue scope focused on markdown/content contract reconciliation.
- Historical evidence in orchestrator/session traces shows `test_repo_skill_parity_merges.py` was updated alongside repo-side skill merge work around issue #1741, so its failures may reflect drift after that merge rather than purely bad tests.

### Gaps identified
- No documented policy for when repo-local skill variants may intentionally diverge from historical parity expectations.
- No module-by-module reconciliation note exists for dark-intelligence, doc-extraction, research-literature, and parity-merge expectations.
- The failing tests mix frontmatter contract, section-heading contract, and domain-content heuristics in one undifferentiated bucket.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-04-20 via `gh issue view`):
- `#2080` — OPEN — umbrella stale skill tests issue
- `#2419` — OPEN — markdown/content-contract drift child issue

**File existence**:
- EXISTS: `tests/skills/test_dark_intelligence_workflow.py`
- EXISTS: `tests/skills/test_doc_extraction_skill.py`
- EXISTS: `tests/skills/test_research_literature.py`
- EXISTS: `tests/skills/test_repo_skill_parity_merges.py`
- EXISTS: `.claude/skills/data/dark-intelligence-workflow/SKILL.md`
- EXISTS: `.claude/skills/data/research-literature/SKILL.md`
- EXISTS: `.claude/skills/engineering/doc-extraction/SKILL.md`
- EXISTS: `.claude/skills/engineering/doc-extraction/naval-architecture/SKILL.md`

**Observed failure excerpts from `uv run pytest tests/skills -q`**:
- `test_dark_intelligence_workflow.py`: related_skills mismatch, missing `Step 2`, missing `HARD GATE`, missing `legal_scan_passed`, missing `test_` markers
- `test_doc_extraction_skill.py`: missing `curves`, missing `naval-architecture` reference, missing naval-architecture `gm/gz/kb/bm`, missing `Cb/Cp/Cm/Cwp`
- `test_research_literature.py`: expected `## 5-Step Workflow`, current skill has `## 8-Step Workflow`; `query-ledger.py` reference missing
- `test_repo_skill_parity_merges.py`: missing `## Task Template`, missing `## Practical Workflow`, missing `Do not fix symptoms until you understand the root cause`

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2419-skill-markdown-contract-drift.md` |
| Failing tests | `tests/skills/test_dark_intelligence_workflow.py`, `tests/skills/test_doc_extraction_skill.py`, `tests/skills/test_research_literature.py`, `tests/skills/test_repo_skill_parity_merges.py` |
| Candidate skill files | `.claude/skills/data/dark-intelligence-workflow/SKILL.md`, `.claude/skills/data/research-literature/SKILL.md`, `.claude/skills/engineering/doc-extraction/SKILL.md`, `.claude/skills/engineering/doc-extraction/naval-architecture/SKILL.md`, `.claude/skills/development/planning/writing-plans/SKILL.md`, `.claude/skills/ai/prompting/dspy/SKILL.md`, `.claude/skills/development/systematic-debugging/SKILL.md` |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2419-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2419-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2419-gemini.md` |

---

## Deliverable

A documented and test-backed reconciliation of the current skill markdown contract, restoring green status for the four failing content-drift test modules without blindly forcing outdated expectations onto intentionally evolved skills.

---

## Pseudocode

```
for each failing test module in [dark_intelligence, doc_extraction, research_literature, parity_merges]:
    map each failing assertion to the current skill file line/content it expects
    classify assertion as one of:
        stale_test
        skill_regression
        ambiguous_contract
    if stale_test:
        update test to reflect current intentional contract
    if skill_regression:
        restore the missing section/phrase/field in the skill file
    if ambiguous_contract:
        pick one contract explicitly and encode it in test + file comments/issue note
run targeted pytest per module
run full tests/skills sweep to verify bucket closure impact
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/skills/test_dark_intelligence_workflow.py` | update stale assertions where current skill contract is intentional |
| Modify | `tests/skills/test_doc_extraction_skill.py` | reconcile taxonomy/sub-skill assertions |
| Modify | `tests/skills/test_research_literature.py` | reconcile workflow/script references |
| Modify | `tests/skills/test_repo_skill_parity_merges.py` | align parity-merge expectations to chosen repo-local contract |
| Modify | selected `.claude/skills/**/SKILL.md` files | restore missing sections/phrases only where the test reflects desired contract |
| Update | `docs/plans/README.md` | add this plan row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dark_intelligence_workflow_contract` | chosen contract for related_skills/steps/legal gate is explicit and passing | current dark-intelligence skill | pytest pass |
| `test_doc_extraction_taxonomy_contract` | main taxonomy and naval-architecture expectations are aligned | current doc-extraction skills | pytest pass |
| `test_research_literature_contract` | workflow-section count and script references match chosen v1 contract | current research-literature skill | pytest pass |
| `test_repo_skill_parity_merge_contract` | repo-local parity merge expectations match current repo-local skill contract | current merged skills | pytest pass |
| `test_full_skill_bucket_after_reconciliation` | no residual failures in the four-module content bucket | targeted pytest selection | all pass |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/skills/test_dark_intelligence_workflow.py -q` passes
- [ ] `uv run pytest tests/skills/test_doc_extraction_skill.py -q` passes
- [ ] `uv run pytest tests/skills/test_research_literature.py -q` passes
- [ ] `uv run pytest tests/skills/test_repo_skill_parity_merges.py -q` passes
- [ ] The resolution records which expectations were updated in tests versus restored in skills
- [ ] The chosen repo-local contract avoids reintroducing known drift in future skill merges

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

- **Risk:** blindly updating tests to green could erase intended skill-quality requirements.
- **Risk:** blindly restoring all historical phrases could reintroduce obsolete or Hermes-specific wording into repo-local skills.
- **Open:** should parity-merge regression tests enforce exact phrase parity, or only presence of the intended operational contract?
- **Open:** for doc-extraction, should top-level skill files carry all taxonomy detail, or should the tests pivot toward sub-skill decomposition reality?

---

## Complexity: T2

**T2** — multiple tests and multiple skill files may need coordinated updates, but the work is bounded to content-contract reconciliation within one subsystem family.
