### Verdict: REQUEST_CHANGES

### Summary
The plans are directionally strong, but they are not yet implementation-ready due to dependency gaps, ambiguous acceptance criteria, and high feasibility risk in the passing-ship workstream. The biggest blockers are untracked cross-ticket dependencies, reliance on non-repo data/tools, and insufficiently testable definitions of “fixed/corrected.” With tighter scoping and measurable gates, this can be approved.

### Issues Found
- [P1] Critical: `WRK-131` has hidden external dependencies (`G:\...xlsm`, `R:\Archive...`) and legal constraints, but no explicit data-access/compliance gate in `blocked_by`; delivery is not feasible/reproducible in standard repo/CI environments.
- [P1] Critical: Cross-ticket dependency is underspecified: `WRK-131` says reporting depends on `WRK-130` “once complete,” but `blocked_by` is empty; this can cause sequencing failure and rework.
- [P1] Critical: Several acceptance criteria are not objectively measurable (e.g., “root cause identified and corrected” in `WRK-132`, “standardized report” in `WRK-130`) without numeric pass/fail thresholds per DOF/metric.
- [P2] Important: `WRK-131` scope is too broad for one ticket (reverse-engineer Excel model, build new spec/schema, solver integration, parametric engine, 5–7 historical reproductions, reporting); strong scope-creep risk.
- [P2] Important: Solver strategy is inconsistent in `WRK-131` (“AQWA integration” vs “OrcaFlex preferred”) without a single source-of-truth execution path, which risks divergent results.
- [P2] Important: `WRK-130` requirement “self-contained HTML” conflicts with “embedded Plotly CDN” (CDN is external dependency); clarify offline vs online report requirement.
- [P2] Important: Test strategy is incomplete across all three plans: no regression baseline governance, no tolerance matrix by metric/DOF, no failure-mode tests (missing headings/frequencies, sparse grids, malformed mesh/hull metadata).
- [P3] Minor: Dependency inventory omits operational dependencies (AQWA/OrcaWave license availability, compute/runtime constraints, parallel execution limits), which can affect schedule realism.

### Suggestions
- Split `WRK-131` into staged deliverables with hard gates: `131A` Excel model parity + schema, `131B` solver coupling (single solver first), `131C` benchmark reproduction + reporting; add explicit `blocked_by` links.
- Add measurable acceptance thresholds and a unified validation matrix (per hull, per DOF, per metric), plus offline/online report mode requirements for `WRK-130`.

### Questions for Author
- Which solver is the authoritative implementation target for `WRK-131` phase 1–2 (AQWA or OrcaFlex), and what is the fallback if one path is unavailable?
- Can you define explicit numeric success criteria for `WRK-132` RAO fixes (e.g., max amplitude/phase error bands by DOF and frequency range) and `WRK-130` report completeness checks?
