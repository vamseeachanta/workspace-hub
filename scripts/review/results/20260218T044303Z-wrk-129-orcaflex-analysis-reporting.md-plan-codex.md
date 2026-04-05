### Verdict: REQUEST_CHANGES

### Summary
The plan is strong on section-level detail and domain intent, but it is not implementation-ready yet because core contracts, dependency boundaries, and acceptance criteria are still ambiguous. The largest concerns are a requirement contradiction (single-file self-contained vs Plotly CDN), underestimated extraction/check complexity, and insufficiently objective test gates.

### Issues Found
- [P1] Critical: Requirement conflict: spec says "self-contained, single-file HTML" while also requiring Plotly via CDN. CDN introduces external dependency and breaks true self-containment/offline reproducibility.
- [P1] Critical: Architecture ambiguity: plan says "subclassing OrcaFlexAnalysisReport per type" but file layout suggests separate report/render classes. Data-model inheritance and renderer inheritance are conflated — can create brittle coupling and circular imports.
- [P2] Important: Design check complexity underestimated: implementing code-level checks across DNV/API/ASME plus five structure types is larger than WRK-129 scope.
- [P2] Important: Dependency versions missing: OrcFxAPI, Plotly, Pydantic v2, Playwright compatibility not stated.
- [P2] Important: Acceptance criteria not fully measurable — "valid HTML," "mesh quality verdict," "design checks embedded" lack objective thresholds.
- [P2] Important: Test plan lacks negative-path coverage (missing/partial data, failed extraction, unavailable fatigue inputs) and regression baselines.
- [P3] Minor: Scope creep risk — reporting, data extractors, CLI wiring, and design-check formulas bundled without de-scoping triggers.
- [P3] Minor: Cross-review gate lacks merge criteria tied to severity thresholds.

### Suggestions
- Split into MVP: shared schema + generator + 2 structure types, no new design-formula engine (reuse existing check outputs).
- Define strict data contract (required/optional/conditional) and extractor boundary (OrcFxAPI → normalized DTO → renderer).
- Resolve self-contained policy: embed Plotly JS inline (include_plotlyjs=True) OR rename to "single HTML with CDN dependency."
- Add objective acceptance gates: section presence list, numeric tolerances, severity-based review exit (0 P1, bounded P2).

### Questions for Author
- Should WRK-129 compute design checks itself, or only present checks already computed by existing analysis modules?
- Is offline report portability a hard requirement?
