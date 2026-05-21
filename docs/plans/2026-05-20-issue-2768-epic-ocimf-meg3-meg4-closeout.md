# Plan for #2768: epic(ocimf) — close out MEG3/MEG4 coefficient ingestion and reference gaps

> **Status:** draft
> **Complexity:** T3 (parent/epic — coordinates 5 sub-issues across 3 repos)
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2768
> **Review artifacts:** scripts/review/results/2026-05-20-plan-2768-claude.md | ...-codex.md | ...-gemini.md (not yet produced)
> **Authorization scope:** workspace-hub writes only (docs/plans/, knowledge/wikis/, docs/governance/). This plan does NOT authorize any writes under digitalmodel/src/, digitalmodel/tests/, or llm-wiki/wikis/ — those repos require their own `status:plan-approved` gates.

---

## Resource Intelligence Summary

### Existing repo code

- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py` (826 LOC) — current `OCIMFDatabase` implementation; uses RBF interpolation on synthetic sample CSV.
- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/environmental_loading/ocimf.py` (825 LOC) — duplicate twin module differing by single `import seaborn as sns`. Hygiene gap (epic body §Medium-priority).
- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/hydrodynamics/ocimf_loading.py:79-85` — hardcoded `Cx = 0.85 * np.abs(np.cos(theta))` constants; refactor target once registry lands.
- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/citations/registry.py` — DNV-OS-E301 precedent template (per `.claude/rules/calc-citation-contract.md` pilot at workspace-hub#2685).
- **EXISTS** `/mnt/local-analysis/digitalmodel/scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py` — parser prototype for the `OCIMFExcelAdapter`; handles four sub-header grammars in the workbook.

### Standards

| Standard | Status | Source |
|---|---|---|
| OCIMF MEG3 (2008) | wiki page exists at `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg3.md` (committed llm-wiki `9b3481c9`); **not yet mirrored** into workspace-hub `knowledge/wikis/engineering/wiki/standards/` | `.claude/rules/calc-citation-contract.md`; workspace-hub#2284 |
| OCIMF MEG4 (2018) | wiki page exists at `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg4.md` (committed llm-wiki `9b3481c9`); **not yet mirrored** | same |
| OCIMF 1994 "Prediction of Wind and Current Loads on VLCCs" | not in corpus — separate digitization or licensed acquisition needed (epic body §Coverage extensions) | epic body |
| DNV-OS-E301 (mooring) | done — pilot at workspace-hub#2685 (CLOSED); `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` is the precedent file shape | `.claude/rules/calc-citation-contract.md` |

### LLM Wiki pages consulted

- `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg3.md` — MEG3 (2008) citation-resolver target; metadata-only.
- `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg4.md` — MEG4 (2018) citation-resolver target; metadata-only.
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — citation pilot precedent (workspace-hub#2685); demonstrates the `code_id`/`publisher`/`revision` frontmatter shape that MEG3/MEG4 mirror pages must adopt fail-closed per `.claude/rules/calc-citation-contract.md`.

### Documents consulted

- `/mnt/local-analysis/workspace-hub/.claude/rules/calc-citation-contract.md` — citation emission contract; fail-closed at calc time; resolver is direct file read for v1 (workspace-hub#2481 D3 decision).
- `/mnt/local-analysis/digitalmodel/docs/data/OCIMF_CORPUS_README.md` — full data-routing map; canonical sources, schema-mismatch table, coverage gaps (committed digitalmodel `9796effa`).
- `/mnt/local-analysis/digitalmodel/docs/plans/2026-05-05-issue-556-ocimf-coefficients-interpolation.md` (2335 B), `…-issue-557-…boundary-warnings.md` (2181 B), `…-issue-561-…mooring-combined-environmental.md` (2425 B), `…-issue-564-…mooring-environmental-forces-total.md` (2194 B) — **pre-existing child plans** in digitalmodel from 2026-05-05; they predate this epic by 15 days and must be reconciled (epic body §Medium-priority bullet 3 explicitly names "Add References sections" to these four files).
- Related issue `workspace-hub#2284` — wiki promotion of MEG3/MEG4 (OPEN); umbrella for the workspace-hub `knowledge/wikis/` mirror decision.
- Related issue `workspace-hub#2625` — marine-engineering domain regressions umbrella (~60 failures across catenary/wave/ocimf/RAO); overlaps with #556/#557/#561 scope.
- `.claude/skills/coordination/issue-planning-mode/references/layered-architecture-issue-planning.md` — required framing for parent/child split.

### Gaps identified

1. **No canonical epic plan file existed before this draft** — the umbrella issue body carried plan-tier content but no `docs/plans/` artifact (verified `ls docs/plans/ | grep 2768` returned empty).
2. **No `OCIMFExcelAdapter` exists** in digitalmodel — only the build-script prototype.
3. **No physical-range bounding** in `OCIMFDatabase.get_coefficients()` — RBF extrapolation can return `CYw=-3.56` (~3× outside empirical `Cyw` envelope of `abs(max)=1.165`).
4. **No `OCIMF-MEG3`/`OCIMF-MEG4` entries** in `digitalmodel/src/digitalmodel/citations/registry.py`.
5. **No workspace-hub `knowledge/wikis/engineering/wiki/standards/ocimf-meg{3,4}.md`** mirror files — the calc citation contract resolver (per the rule, v1 = direct file read) currently expects pages under workspace-hub's `knowledge/wikis/` tree, but the OCIMF wiki pages live only in the sibling `llm-wiki` repo.
6. **Duplicate `ocimf.py`** in `marine_engineering/` vs `marine_analysis/` — consolidation target.
7. **State drift on `#2278`**: epic body claims "closed 2026-05-20", but `gh issue view 2278 --repo vamseeachanta/workspace-hub` returns `state=OPEN` (verified below). Plan-review must reconcile.
8. **No child plan in this repo for #2284** — the wiki mirror decision is workspace-hub-scoped but the umbrella delegates it without naming an owner plan.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20T19:35:00Z via `gh issue view`):

- `workspace-hub#2768` — OPEN — "epic(ocimf): close out MEG3/MEG4 coefficient ingestion and reference gaps" — `status:plan-review` + `cat:engineering` + `enhancement` + `priority:medium`
- `digitalmodel#556` — OPEN — "fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_get_coefficients_interpolation — CYw=-3.56 not in [0,1.5]"
- `digitalmodel#557` — OPEN — "fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_boundary_warnings — DID NOT WARN on out-of-range query"
- `digitalmodel#561` — OPEN — "fix(marine_ops): test_ocimf_mooring_integration.py::test_combined_environmental_forces — wrong test premise (current dominates)"
- `digitalmodel#563` — OPEN — "fix(marine_ops): test_marine_eng_performance.py::test_ocimf_database_performance — needs investigation"
- `digitalmodel#564` — OPEN — "fix(marine_ops): test_ocimf_mooring_integration.py::test_environmental_forces_to_mooring_tension — needs investigation"
- `workspace-hub#2284` — OPEN — "feat(wiki): promote OCIMF MEG3 and MEG4 to mooring wiki domain"
- `workspace-hub#2278` — **OPEN** — "chore(acma-codes): reconcile OCIMF MEG fragments misfiled under Noble Denton metadata wave" → **contradicts epic body's "closed 2026-05-20" claim; flag for plan-review.**
- `workspace-hub#2625` — OPEN — "investigate(digitalmodel-tests): Cluster E — marine-engineering domain regressions (~60 failures across catenary/wave/ocimf/RAO)"
- `workspace-hub#2685` — CLOSED — "Citation pilot contradiction: rule names orcaflex/mooring_design.py but file emits no Citation"
- `workspace-hub#2481` — CLOSED — "feat(llm-wiki): calculation-output citation contract — engineering modules cite wiki-backed provenance"

**File existence** (`ls -la` 2026-05-20T19:35:00Z):

- EXISTS: `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx` (master digitization, 17 sheets)
- EXISTS: `/mnt/local-analysis/digitalmodel/docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` (committed `9796effa`)
- EXISTS: `/mnt/local-analysis/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py` (826 LOC)
- EXISTS: `/mnt/local-analysis/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/environmental_loading/ocimf.py` (825 LOC — duplicate)
- EXISTS: `/mnt/local-analysis/digitalmodel/src/digitalmodel/citations/registry.py` (DNV-OS-E301 pilot precedent)
- EXISTS: `/mnt/local-analysis/digitalmodel/scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py` (parser prototype)
- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg3.md` (committed llm-wiki `9b3481c9`)
- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg4.md` (committed llm-wiki `9b3481c9`)
- EXISTS: `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (precedent shape)
- MISSING (this plan does NOT create): `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/ocimf-meg3.md`
- MISSING (this plan does NOT create): `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`
- MISSING (this plan creates this single artifact): `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md`

**Commit excerpt** (`git show --stat 9796effa | head -4` in /mnt/local-analysis/digitalmodel):

```
commit 9796effa707e44ed1d337f70313f1cc9c7a5e3d5
Author: Vamsee Achanta <achantav@gmail.com>
Date:   Wed May 20 14:21:55 2026 -0500
    docs(ocimf): interactive coefficient explorer + cross-project prompt + corpus README
```

**Reproduction proofs** (Step 1.5): **N/A — epic-tier coordination plan.** This plan does not propose a code change; runtime claims (e.g., `CYw=-3.56` out-of-envelope at `digitalmodel#556`) must be reproduced in the child plan under `digitalmodel/docs/plans/2026-05-05-issue-556-…md`. The skip is intentional per the issue-planning-mode skill: "Skip-allowed only when: issue is documentation-only, governance-only … or otherwise has no runtime claim to verify." Per §Acceptance below, this epic explicitly delegates reproduction to the child plans and cannot close until they each carry verified reproduction citations.

Distinct sources consulted: 11 (issue body + 10 verifiable artifacts/issues above). Minimum 3 required — exceeded.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md` |
| README index row | `docs/plans/README.md` |
| Existing child plans (pre-dated by 15d, must be reconciled) | `digitalmodel/docs/plans/2026-05-05-issue-{556,557,561,564}-*.md` |
| Child plan to be drafted (not in this plan's scope) | `digitalmodel/docs/plans/<future>-issue-563-ocimf-excel-adapter.md` |
| Child plan to be drafted (not in this plan's scope) | `workspace-hub/docs/plans/<future>-issue-2284-ocimf-meg-wiki-mirror.md` |
| Plan review — Claude | `scripts/review/results/2026-05-20-plan-2768-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-20-plan-2768-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-20-plan-2768-gemini.md` |
| Wiki mirror targets (created in child plan, NOT this one) | `knowledge/wikis/engineering/wiki/standards/ocimf-meg{3,4}.md` |
| Source-of-truth wiki pages (already exist; out of scope to modify) | `llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg{3,4}.md` |

---

## Deliverable

A workspace-hub-tracked epic-plan artifact that defines the lifecycle contract for OCIMF MEG3/MEG4 closeout — naming the 8 dispatchable sub-items, their owning repos, dependency ordering, promotion gates, and the explicit boundary that no child code work begins until each child issue lands its own `status:plan-approved`. This plan adds zero functional capability; its value is preventing re-discovery and false-completion of an 8-item cross-repo cleanup.

---

## Pseudocode

T3 epic plans describe **coordination flow**, not code. The flow:

```
PHASE A — workspace-hub-scoped (this plan can authorize, after user approval):
  A1. Draft child plan for #2284 (wiki mirror decision):
        decide:  mirror-copy  OR  symlink  OR  resolver-extension
        criterion: which option keeps llm-wiki the canonical source AND
                   satisfies calc-citation-contract.md v1 direct-file-read
                   AND survives standalone-package mode (no overlay)
  A2. Execute the wiki mirror decision once #2284 is approved (separate plan).
  A3. Close #2284 with evidence.

PHASE B — digitalmodel-scoped (this plan ONLY tracks; cannot authorize):
  B1. Reconcile pre-existing child plans 2026-05-05-issue-{556,557,561,564}-*.md
        against the umbrella's empirical-bounds table (epic body §Physical ranges)
        AND against the OCIMF_CORPUS_README.md schema-mismatch table.
        Each child plan needs a References section pointing at the corpus README
        and citation contract.
  B2. Draft new child plan for digitalmodel#563 (OCIMFExcelAdapter) using
        scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py as prototype.
        TDD: ≥1033 rows, 14 figures present, A15 explicitly absent, spot-check values.
  B3. Apply physical-range bounding in #556 child plan (uses empirical bounds from
        epic body §Physical coefficient ranges).
  B4. Add OCIMF-MEG3/MEG4 entries to digitalmodel/src/digitalmodel/citations/registry.py
        once Phase A mirror lands (gating dependency).
  B5. Consolidate marine_engineering/ocimf.py vs marine_analysis/ocimf.py duplicate.
  B6. Refactor hydrodynamics/ocimf_loading.py:79-85 hardcoded constants to use
        registry (after B4 lands).
  B7. Add References sections to the 4 pre-existing child plans.

PHASE C — closeout (workspace-hub):
  C1. Verify all 8 sub-items closed; close #2768.
  C2. Reconcile #2278 state (epic body claims closed, gh says OPEN).
```

Critical dependency: **B4 and B6 are blocked by Phase A** because the citation contract resolver (per `.claude/rules/calc-citation-contract.md`) is fail-closed and needs workspace-hub-side wiki pages to resolve `OCIMF-MEG3`/`OCIMF-MEG4` codes. Don't start B4 until A2 lands.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| **Create** | `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md` | This plan (the only new artifact this plan produces) |
| **Update** | `docs/plans/README.md` | Add row for #2768 in the Plan Index table |

**Not in this plan's scope (explicitly):**

| Would-be action | Path | Why blocked |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-meg{3,4}.md` | Owned by future child plan for #2284 |
| Modify | `digitalmodel/src/digitalmodel/citations/registry.py` | Cross-repo; needs digitalmodel-side approval |
| Modify | `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py` | Cross-repo; #556 child plan |
| Create | `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf_excel_adapter.py` | Cross-repo; #563 child plan |
| Delete | `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/environmental_loading/ocimf.py` | Cross-repo; needs digitalmodel-side approval |
| Modify | `digitalmodel/src/digitalmodel/hydrodynamics/ocimf_loading.py:79-85` | Cross-repo; gated on Phase A landing |
| Update | `digitalmodel/docs/plans/2026-05-05-issue-{556,557,561,564}-*.md` | Cross-repo; each child plan amends itself |
| Modify | `llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg{3,4}.md` | Cross-repo; out of scope (canonical pages, no change planned) |

---

## TDD Test List

Epic plans do not introduce new test code. Their "tests" are **acceptance gates on child completion**, structured so the epic cannot close while any child has gaps. The table below lists each acceptance gate as a falsifiable check that a reviewer (or automated audit) can run.

| Gate | What it verifies | Verification command |
|---|---|---|
| G1: wiki mirror exists | MEG3/MEG4 resolve under workspace-hub `knowledge/wikis/` | `ls knowledge/wikis/engineering/wiki/standards/ocimf-meg{3,4}.md` → both exist |
| G2: citation contract resolves | `OCIMF-MEG3`/`OCIMF-MEG4` codes resolve fail-closed | `cd ../digitalmodel && uv run python -c "from digitalmodel.citations.registry import get_citation; print(get_citation('OCIMF-MEG3'))"` returns Citation object, not error |
| G3: adapter ingests real corpus | ≥1033 rows, 14 figures present, A15 absent | `cd ../digitalmodel && uv run pytest tests/marine_ops/test_ocimf_excel_adapter.py -v` passes |
| G4: bounding applied | RBF extrapolation outside empirical envelope returns clamped + warning | `cd ../digitalmodel && uv run pytest tests/marine_ops/test_ocimf.py::TestOCIMFDatabase::test_get_coefficients_interpolation -v` passes |
| G5: boundary warnings fire | out-of-range queries warn (closes digitalmodel#557) | `cd ../digitalmodel && uv run pytest tests/marine_ops/test_ocimf.py::TestOCIMFDatabase::test_boundary_warnings -v` passes |
| G6: duplicate file removed | `marine_analysis/ocimf.py` either deleted or `_DEPRECATED.py` suffix | `ls ../digitalmodel/src/digitalmodel/marine_ops/marine_analysis/environmental_loading/ocimf.py` → "No such file" OR file header contains "DEPRECATED" |
| G7: hardcoded constants refactored | `hydrodynamics/ocimf_loading.py:79-85` references registry | `grep -nE "0\.85 \* np\.abs\(np\.cos" ../digitalmodel/src/digitalmodel/hydrodynamics/ocimf_loading.py` returns nothing |
| G8: References sections added | 4 child plans each cite the corpus README + citation contract | `grep -l "OCIMF_CORPUS_README\|calc-citation-contract" ../digitalmodel/docs/plans/2026-05-05-issue-{556,557,561,564}-*.md` returns 4 paths |
| G9: workspace-hub#2284 closed | wiki promotion satisfied | `gh issue view 2284 --json state` returns `"state":"CLOSED"` |
| G10: #2278 state reconciled | epic body claim ("closed 2026-05-20") matches gh state | `gh issue view 2278 --json state` matches what the epic body claims, OR epic body is corrected |

---

## Acceptance Criteria

- [ ] This plan file exists at `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md` (G0 — verifiable now).
- [ ] `docs/plans/README.md` has a Plan Index row for #2768 in `draft` status.
- [ ] Adversarial review wave has produced ≥2 artifacts under `scripts/review/results/2026-05-20-plan-2768-*.md` (Claude + Codex minimum; Gemini if quota allows).
- [ ] All MAJOR findings (if any) addressed by plan revision before label moves to `status:plan-review`.
- [ ] User has explicitly approved this plan (`status:plan-approved` label + `.planning/plan-approved/2768.md` marker present) before any child plan is dispatched.
- [ ] Gates G1–G10 above pass before #2768 is closed.
- [ ] #2278 state-drift reconciliation: either the epic body is updated to reflect the live OPEN state, or #2278 is actually closed with evidence.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | _pending_ | _not yet run_ |
| Codex | _pending_ | _not yet run_ |
| Gemini | _pending_ | _not yet run_ |

**Overall result:** _not yet reviewed_ — this plan is **draft**, not approval-ready. Per `feedback_adversarial_review_stance`, the next step is to dispatch the 3-provider review wave with adversarial-stance prompts; this plan must not be surfaced for user approval until that completes.

---

## Risks and Open Questions

- **Risk (state drift):** epic body claims `workspace-hub#2278` closed 2026-05-20; `gh issue view 2278` returns OPEN. Either the epic body is wrong or there is a race-condition timing issue. Reconcile during plan-review.
- **Risk (cross-repo authorization confusion):** because the epic body lists work items that live in 3 different repos (workspace-hub, digitalmodel, llm-wiki), there is risk an implementing agent reads the epic and starts writing code in digitalmodel without that repo's own plan + approval. This plan's §Files-to-Change "Not in this plan's scope" table is the explicit guardrail.
- **Risk (resolver coupling):** the calc-citation-contract resolver path is fail-closed AND v1 is direct file read. Until the workspace-hub `knowledge/wikis/` mirror lands (Phase A), digitalmodel registrations for `OCIMF-MEG3`/`OCIMF-MEG4` will fail at runtime in workspace-hub context. Strict B4-after-A2 ordering is required.
- **Risk (pre-dated child plans):** `digitalmodel/docs/plans/2026-05-05-issue-{556,557,561,564}-*.md` were drafted 15 days before this epic; they may carry assumptions that conflict with the empirical-bounds table the epic body adds (e.g., they may not yet reference the schema-mismatch table). Each child plan must be re-examined as part of Phase B1.
- **Risk (mirror-vs-symlink ambiguity):** workspace-hub#2284 has not yet decided whether `knowledge/wikis/engineering/wiki/standards/ocimf-meg{3,4}.md` should be a content-copy mirror, a symlink to the sibling llm-wiki repo, or a resolver-extension that reads from the llm-wiki tree. This is a meaningful design choice (affects standalone-package mode behavior — see `.claude/rules/calc-citation-contract.md` "standalone-package mode degrades gracefully" pilot note). The Phase A child plan must surface this as a domain decision for user approval, not pick silently.
- **Open:** Should #2625 (marine-engineering domain regressions umbrella, ~60 failures) be cross-linked back to this epic? Overlaps with #556/#557/#561 but is a broader cluster.
- **Open:** Should Figure A15's absence be tracked as a separate sub-issue or accepted as a permanent data gap?
- **Open:** Does the legal/source classification of `OCIMF Coef.xlsx` (vendor-licensed under `/mnt/ace/acma-codes/`) permit mirroring its derived metadata into a workspace-hub `knowledge/wikis/` mirror? Per `.claude/rules/calc-citation-contract.md`, vendor-derivative content under `knowledge/wikis/*/wiki/sources/` is deny-list; the standards-page (under `standards/`) is allowed, but the mirror decision must respect this boundary.

---

## Complexity: T3

**T3** — parent/epic coordinating 8 sub-items across 3 repos (workspace-hub, digitalmodel, llm-wiki); cross-repo dependency ordering with a hard gate between Phase A (workspace-hub wiki mirror) and Phase B4/B6 (digitalmodel citation registry adoption); falls under `cat:engineering` so the `engineering-issue-workflow` skill applies for any child-stage code work.
