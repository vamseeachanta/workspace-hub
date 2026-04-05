### Verdict: REQUEST_CHANGES

### Summary
The plan is strong on section-level detail and domain intent, but not implementation-ready because core contracts, dependency boundaries, and acceptance criteria are ambiguous. Key concerns: requirement contradiction (self-contained vs CDN), architecture ambiguity (data model vs renderer inheritance conflated), and non-measurable test gates.

### Issues Found
- [P1] Critical: Requirement conflict — spec says "self-contained, single-file HTML" while requiring Plotly via CDN. CDN dependency breaks offline reproducibility.
- [P1] Critical: Architecture ambiguity — "subclassing OrcaFlexAnalysisReport per type" conflates data-model inheritance with renderer inheritance. Creates brittle coupling and potential circular imports.
- [P2] Important: Design check complexity underestimated — DNV/API/ASME checks across five structure types exceeds WRK-129 scope without explicit boundaries.
- [P2] Important: Dependency versions missing — OrcFxAPI, Plotly, Pydantic v2, Playwright compatibility constraints not stated.
- [P2] Important: Acceptance criteria not measurable — "valid HTML," "mesh quality verdict," "design checks embedded" lack objective thresholds/tolerances.
- [P2] Important: Test plan lacks negative-path coverage (missing data, failed extraction, unavailable fatigue inputs) and regression baselines (golden snapshots).
- [P3] Minor: Scope creep risk — reporting, data extractors, CLI wiring, and formula implementations bundled without de-scoping triggers.
- [P3] Minor: Review gate lacks merge criteria tied to severity thresholds (e.g., 0 open P1/P2 to proceed).

### Suggestions
- Split into MVP phase: shared schema + generator + 2 structure types only; no new design-formula engine (consume existing check outputs).
- Define strict data contract (required/optional/conditional fields) and explicit extractor boundary (OrcFxAPI → DTO → renderer).
- Resolve self-contained policy explicitly: use `include_plotlyjs=True` for offline OR `"cdn"` and rename to "single HTML with CDN dependency."
- Add objective acceptance gates: section presence checklist, numeric tolerances for key metrics, severity-based exit (0 P1, ≤2 P2 deferred).

### Questions for Author
- Should WRK-129 compute design checks itself or present checks already computed by existing analysis modules?
- Is offline/air-gapped report portability a hard requirement?
