# Phase 1: Accelerate digitalmodel development - Context

**Gathered:** 2026-03-25 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship core calculation modules faster in digitalmodel — structural, fatigue, CP, VIV. Identify highest-value gaps, increase test coverage, streamline the standard-to-code pipeline. UAT: 3+ new calculation modules shipped with full test coverage and traceability to standards.

</domain>

<decisions>
## Implementation Decisions

### Gap Prioritization
- **D-01:** Use module registry gaps (`specs/module-registry.yaml`) as the starting pool, but filter through market signal before committing — competitor analysis (Sesam, SACS, Flexcom), industry demand patterns, and engineering judgment of what offshore clients actually need.
- **D-02:** The registry already documents specific gaps: spectral fatigue, SHEAR7/VIVA VIV, on-bottom stability, biaxial stress interaction, straked suppression. These are the candidate pool.

### Test Strategy
- **D-03:** New modules get self-contained test suites that work independently. Do NOT block new module development on fixing legacy test infrastructure (0/150 runnable in structural/analysis).
- **D-04:** Legacy test fixes (import path issues, TEST_STATUS_DASHBOARD blockers) are a separate effort, not a prerequisite for this phase.

### Standards Traceability
- **D-05:** Dual traceability — docstrings for developer readability (continue existing pattern: "DNV-RP-B401 S7.4.1, Eq 1") PLUS a per-module YAML manifest for CI validation and website showcase.
- **D-06:** YAML manifest per module should map each function to its standard, clause, equation number, and edition — machine-readable and CI-validatable.

### Module Scope Definition
- **D-07:** "New calculation module" for UAT can be either a new standard implementation (e.g., adding ASME B31.4 to wall thickness) OR a new domain capability (e.g., on-bottom stability). Mix is acceptable. 3+ total.

### assetutilities Dependency
- **D-08:** New modules use `assetutilities` for shared infrastructure (config, calculations, base solvers) via the existing editable path dependency. No duplication.

### the agent's Discretion
- Exact order of which 3+ modules to build (within the validated gap pool)
- YAML manifest schema design
- Test framework choice for new module suites (pytest assumed)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Module registry and gaps
- `digitalmodel/specs/module-registry.yaml` — Master registry of all modules, maturity levels, and documented gaps
- `digitalmodel/specs/data-needs.yaml` — Structured lifecycle tracking for data dependencies (needed -> extracted -> integrated)

### Existing code patterns (templates for new modules)
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` — Reference implementation of one-file-per-standard pattern with docstring traceability
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/` — Multiple standard implementations (DNV-ST-F101, API RP 1111, ASME B31.8) showing the pattern
- `digitalmodel/src/digitalmodel/subsea/viv_analysis/` — Existing VIV module (DNV-RP-F105)

### Test infrastructure status
- `digitalmodel/tests/structural/analysis/TEST_STATUS_DASHBOARD.md` — Documents 0/150 runnable tests, import path issues
- `digitalmodel/tests/cathodic_protection/` — Working test suite (reference for self-contained pattern)
- `digitalmodel/coverage.json` — Current coverage data

### Dependencies
- `digitalmodel/pyproject.toml` — Package config, assetutilities path dependency
- `assetutilities/src/assetutilities/` — Shared infrastructure: calculation.py, math_helpers.py, units/

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cathodic_protection/` — 3 complete standard implementations (API RP 1632, DNV-RP-B401, ISO 15589-2) — proven pattern for new modules
- `structural/analysis/wall_thickness_codes/` — 4+ code implementations showing multi-standard pattern
- `structural/fatigue/` — 221 S-N curves across 17 standards at production maturity
- `assetutilities` — shared config, calculations, math helpers, units

### Established Patterns
- One Python file per standard (e.g., `dnv_rp_b401.py`)
- Constants traced to specific table/section numbers in docstrings
- Function docstrings cite equation numbers from standards
- `specs/module-registry.yaml` as the module metadata authority

### Integration Points
- `assetutilities` editable dependency for base solvers and config
- `pyproject.toml` test configuration with `fail_under = 80.0`
- Existing test patterns in `tests/cathodic_protection/` as template

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. Module selection will be informed by market signal validation against registry gaps.

</specifics>

<deferred>
## Deferred Ideas

- Legacy test infrastructure fix (0/150 structural/analysis tests) — separate effort
- Client feedback system / CRM integration — Phase 4
- DNV-RP-F105 edition update check — nightly research (Phase 5)

</deferred>

---

*Phase: 01-accelerate-digitalmodel-development*
*Context gathered: 2026-03-25*
