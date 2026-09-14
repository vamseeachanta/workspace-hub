# Plan for #3810: Two independent calculation-report systems — pick a canonical one

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-09-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3810
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-09-plan-3810-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

**System A (YAML/script) — workspace-hub:**
- Found: `scripts/reporting/generate-calc-report.py` (21,850 bytes, 582 lines) — YAML pipeline, "warm parchment" HTML design, LaTeX rendered via KaTeX CDN, interactive charts via Chart.js CDN. Outputs use optional `pass_fail` booleans; no `Confidence` concept.
- Found: `.claude/skills/data/calculation-report/SKILL.md` (4,514 bytes) — documents System A usage including 13 example YAML files. No mention of System B, no routing guidance for new work.
- Found: `config/reporting/calculation-report-schema.yaml` (2,361 bytes) — validates System A YAML structure. Sections: metadata, inputs, methodology, outputs, assumptions, references.
- Found: `examples/reporting/` — 13 worked examples (fatigue girth weld, SCR touchdown, spectral fatigue, geotechnical pile/anchor/scour, pipeline stability, etc.) as YAML inputs.

**System B (typed Python) — digitalmodel:**
- Found: `digitalmodel/src/digitalmodel/reporting/calc_report.py` (792 lines) — pydantic models: `CalcReport`, `ResultBlock`, `Confidence` enum (validated/analytical/pending). CSP-safe — no CDN. Fixed seven-section order (Objective, Design data, Analysis methodology, Results, Validation status, Way forward, References).
- Found: `digitalmodel/src/digitalmodel/reporting/` — 8 sibling modules (`_backbone.py`, `_base.py`, `brief.py`, `__init__.py`, `__main__.py`, `provenance.py`, `_renderer.py`, `skeleton.py`).
- Found: 5+ live production consumers inside digitalmodel: `seismic/response_spectrum/render.py`, `floating_wind/economics_report.py`, `floating_wind/report.py`, `fatigue/fatigue_reporting.py`, `hydrodynamics/diffraction/report_generator.py`.
- Found: `digitalmodel/tests/reporting/test_calc_report.py` (491 lines) + 3 sibling test files (`test_provenance.py`, `test_reporting_library.py`, `test_skeleton.py`) — active TDD coverage.
- Gap: No `report-claim-discipline` skill exists in `.claude/skills/` — the issue names this as the second routing destination.
- Gap: `.claude/rules/report-audience-and-surface.md` is referenced in the issue body as a new rule being written; not found in `.claude/rules/` as of 2026-09-09.

### Standards
Not applicable — internal governance/routing decision.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- Issue #3810 body (2026-08-21) — provides a complete side-by-side comparison of both systems, names three reasons the fork matters (honesty guardrails, design divergence, improvement isolation), and lists three realistic resolution options. Authored by code owner; concludes "Owner picks a direction."
- `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md` — established the citation/provenance requirement for every output claim. System B's required `Confidence` enum satisfies this; System A's optional `pass_fail` boolean does not.
- `docs/plans/2026-05-14-issue-2152-reporting-golden-fixture-plan.md` — established golden-fixture test patterns for the reporting surface; System B's 4-file test suite builds on this lineage.

### Gaps identified
- `.claude/skills/data/calculation-report/SKILL.md` has no routing guidance — agents picking System A do so by accident.
- No `report-claim-discipline` skill exists; it must be created as part of this plan.
- System A has no `Confidence` concept and no test coverage — two deficiencies relative to the citation contract and emerging claim-discipline requirements.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-09T~09:00Z via `gh issue view`):
- `#3810` — OPEN — Two independent calculation-report systems (YAML/script vs typed-Python) — pick a canonical one

**File existence** (`ls -la` 2026-09-09 in workspace-hub clone at main 90596e79b):
- EXISTS: `.claude/skills/data/calculation-report/SKILL.md` (4,514 bytes)
- EXISTS: `scripts/reporting/generate-calc-report.py` (21,850 bytes)
- EXISTS: `config/reporting/calculation-report-schema.yaml` (2,361 bytes)
- MISSING (new — this plan creates): `.claude/skills/development/report-claim-discipline/SKILL.md`

**Gap proofs**:
- `ls .claude/rules/ | grep report-audience` → not found → `report-audience-and-surface.md` not committed
- `ls .claude/skills/ | grep -i "report-claim\|claim-discipline"` → no match → skill does not exist

**Reproduction proofs**: N/A — this is a governance/routing decision issue, not a runtime failure. Mark intentional skip.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-09-09-issue-3810-calc-report-canonical-system.md` |
| Routing update | `.claude/skills/data/calculation-report/SKILL.md` |
| New skill | `.claude/skills/development/report-claim-discipline/SKILL.md` |
| Deprecation notice | `scripts/reporting/generate-calc-report.py` header docstring |
| Plan review — Claude | `scripts/review/results/2026-09-09-plan-3810-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-09-09-plan-3810-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-09-09-plan-3810-agy.md` |

---

## Deliverable

System B (`digitalmodel.reporting.CalcReport`) is declared canonical for all issued engineering deliverables via routing statements in the `calculation-report` skill and a new `report-claim-discipline` skill; System A's YAML generator carries a deprecation notice pointing to System B.

---

## Decision rationale (for user review at plan-approved gate)

**Recommendation: System B canonical.** This plan presents the recommendation; user approval of this plan constitutes the routing decision.

Evidence for System B:

1. **Real production consumers.** Five live import consumers inside digitalmodel (`seismic`, `floating_wind` x2, `fatigue`, `hydrodynamics/diffraction`). System A has 13 example YAMLs but no live import consumers. Improvements to System B reach real analysis paths; improvements to System A remain isolated.

2. **Honesty guardrail.** System B's `Confidence` enum is a **required field** on every `ResultBlock` (no default). System A uses optional `pass_fail` booleans — a client report with a `pass_fail=True` output can silently omit confidence level. The citation contract (`docs/plans/2026-04-24-issue-2481`) established that every output claim must carry provenance; System B satisfies this by construction; System A does not.

3. **CSP-safety.** System A loads KaTeX (LaTeX) and Chart.js from CDN. Both are blocked by corporate CSP policies common in O&G client deployments. System B renders equations as numbered cards with variable-definition tables — no external dependencies.

4. **Active test coverage.** System B: 491-line `test_calc_report.py` + 3 sibling test files. System A: no test file.

**Permitted System A use after this plan:** The 13 worked examples remain valid as quick-calculation references and screening tools. A future follow-on issue should create a YAML-to-System-B bridge so examples remain runnable. That bridge is out of scope for this issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/skills/data/calculation-report/SKILL.md` | Add DEPRECATED block at top + routing statement: "Use `digitalmodel.reporting.CalcReport` for issued deliverables" |
| Create | `.claude/skills/development/report-claim-discipline/SKILL.md` | Document canonical system, routing rule, `Confidence` enum requirement, and when System A remains permitted |
| Modify | `scripts/reporting/generate-calc-report.py` | Add deprecation notice to header docstring with pointer to System B |

---

## TDD Test List

This is a governance/documentation issue — no runtime code logic is changed. Tests are not applicable.

**N/A** — skill files and docstring updates carry no executable logic. Acceptance is by inspection per the criteria below.

---

## Acceptance Criteria

- [ ] `.claude/skills/data/calculation-report/SKILL.md` begins with a clear routing block: "DEPRECATED for new issued deliverables. Use `digitalmodel.reporting.CalcReport` (System B). See `report-claim-discipline` skill."
- [ ] New `.claude/skills/development/report-claim-discipline/SKILL.md` exists and documents: (a) System B is canonical for issued deliverables, (b) System A remains permitted for screening/quick-calc YAML workflows, (c) every `ResultBlock` in System B must carry an explicit `Confidence` level, (d) the `Confidence.PENDING` level is required for any claim awaiting client data.
- [ ] `scripts/reporting/generate-calc-report.py` header docstring includes a deprecation notice: "DEPRECATED: This YAML pipeline is no longer the canonical calc-report path. For issued engineering deliverables, use `digitalmodel.reporting.CalcReport`."
- [ ] No existing System B consumers are modified — this plan does not migrate existing code.
- [ ] No existing System A examples are deleted — the 13 YAML examples remain available.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Agy | PENDING | — |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk — LaTeX users stranded:** System A uses KaTeX for LaTeX rendering. System B renders equations as numbered variable-definition cards (no MathJax/KaTeX). Clients requiring PDF-grade LaTeX output in non-CSP-restricted environments may need System A to remain available beyond the deprecation notice. Flag at approval: user must confirm that System B's equation-card rendering is acceptable for all current deliverable contexts.
- **Risk — 13 example YAMLs become non-runnable:** Deprecating System A without a YAML bridge means existing YAML calc inputs cannot run via System B. The plan scopes this as a follow-on issue, but it creates a gap. At implementation time, file the follow-on issue (#NNNN) and cross-link from both skill files.
- **Open — `report-audience-and-surface.md` rule:** Issue body references this as a new rule being written in parallel. At implementation time, check whether it has been committed; if so, add a routing cross-reference from the new `report-claim-discipline` skill to it.
- **Open — follow-on issue scope:** The YAML bridge ("a thin YAML front-door that deserialises into the typed models") should be a separate issue. Should this plan file that issue, or leave it to the user post-approval? Recommend filing at implementation time with a link in the `report-claim-discipline` skill under "See also."

---

## Complexity: T1

**T1** — two existing file edits (SKILL.md deprecation header, generate-calc-report.py docstring) plus one new skill file. No executable logic changes. Single repo (workspace-hub). The digitalmodel side (System B) is unchanged by this plan.
