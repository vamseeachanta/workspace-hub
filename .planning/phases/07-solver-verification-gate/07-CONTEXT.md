# Phase 7: Solver Verification Gate - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Confirm the license boundary architecture works: OrcFxAPI loads, solves, and exports on licensed-win-1, while all other pipeline work runs license-free on any machine. Go/no-go gate for v1.1 — no development proceeds until this passes.

Additionally, enforce solver/non-solver module separation in codebase and establish remote Claude Code execution from dev-primary to licensed-win-1.

</domain>

<decisions>
## Implementation Decisions

### Machine Topology
- **D-01:** Three-machine architecture: licensed-win-1 (acma-ansys05, OrcaFlex/OrcaWave license), win-2 (ws014, backup/overflow), dev-primary (Linux, orchestration/processing)
- **D-02:** dev-primary is the primary processing machine for all non-license work. win-2 is backup/overflow only — not part of the primary pipeline
- **D-03:** Direct network path exists between licensed-win-1 and win-2

### Result Transfer
- **D-04:** Git push through all three machines — licensed-win-1 commits and pushes solver results (.owr + Excel), dev-primary and win-2 pull. Versioned and traceable
- **D-05:** Smoke test artifacts (L00 + L01 .owr and Excel) committed to digitalmodel repo as permanent test fixtures for downstream phases

### Remote Execution Model
- **D-06:** Claude Code on licensed-win-1 as the solver execution agent, polled via Windows Task Scheduler every 30 minutes
- **D-07:** Remote CC trigger from dev-primary is a HARD REQUIREMENT for Phase 7 — satisfied via git-based pull queue (corporate firewall blocks inbound SSH)
- **D-08:** Phase 7 has two verification gates: (1) OrcFxAPI functional on licensed-win-1, (2) queue-based CC trigger works (dev-primary submits job → licensed-win-1 pulls and processes)
- **D-18:** Pull-based queue architecture — dev-primary commits job YAML to queue/pending/, licensed-win-1 polls via git pull + Task Scheduler, no inbound connections needed

### Smoke Test Scope
- **D-09:** Run L00 (simplest) and L01 (moderate) benchmark cases through solver, producing reference .owr + Excel artifacts
- **D-10:** Binary pass/fail criteria: OrcFxAPI imports, loads .owd, runs calculation, extracts at least one result set = pass. No physics sanity checks at this gate
- **D-11:** Artifacts committed to digitalmodel repo as permanent test fixtures for later phases to consume without solver access

### Module Separation (License Boundary)
- **D-12:** Separate entry points pattern — solver-dependent code in its own subpackage (e.g., `diffraction/solver/`), everything outside is license-free. No conditional `try/except import` hacks
- **D-13:** Phase 7 enforces this separation now (refactor), not just verifies it's possible. Clean boundary before development phases begin

### uv & Python Environment
- **D-14:** uv already installed on licensed-win-1 — verify `uv sync` works with OrcFxAPI wheel compatibility as primary concern
- **D-15:** Python version follows OrcFxAPI compatibility requirements (currently supports 3.8-3.12). Align all machines to the highest version OrcFxAPI supports

### Test Strategy
- **D-16:** Create `@pytest.mark.solver` marker for tests requiring OrcFxAPI. CI skips solver-marked tests on Linux
- **D-17:** pytest fixtures providing .owr/.xlsx reference data so solver-free tests can use real results without needing OrcFxAPI installed

### Claude's Discretion
- Remote CC trigger mechanism (SSH + CC, native remote dispatch, or other approach)
- Exact subpackage structure for solver-dependent code separation
- Python version selection within OrcFxAPI's supported range

### Folded Todos
- **Automate OrcaWave vessel hull analysis on licensed machine** — broader milestone goal, Phase 7 verifies the execution foundation
- **Automate OrcaFlex model generation on licensed machine** — Phase 12 goal, Phase 7 confirms the license boundary that enables it

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Infrastructure requirements
- `.planning/REQUIREMENTS.md` — INFRA-01 (license-free pipeline) and INFRA-02 (solver on licensed-win-1 only)

### Architecture & pitfalls
- `.planning/research/ARCHITECTURE.md` — Layer map of existing diffraction components, solver execution layer, result extraction
- `.planning/research/SUMMARY.md` — Phase 0 rationale, pitfall 4 (solver not verified), pitfall 6 (cross-platform failures)
- `.planning/research/PITFALLS.md` — Frequency unit convention mismatch, cross-platform DLL failures, OrcFxAPI import patterns

### OrcaWave analysis patterns
- `.claude/skills/engineering/marine-offshore/orcawave-analysis/SKILL.md` — OrcFxAPI Python API reference, prerequisites, existing automation patterns

### Benchmark data
- `docs/domains/orcawave/` — L00-L04 benchmark data, hull forms, example YAML specs (in digitalmodel repo)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `diffraction/orcawave_runner.py` — RunConfig, RunResult, RunStatus for solver execution orchestration
- `diffraction/result_extractor.py` — Raw solver output to DiffractionResults extraction
- `diffraction/orcawave_converter.py` — OrcFxAPI data to unified schema conversion
- `diffraction/output_validator.py` — Physics-based validation checks on results
- `diffraction/orcawave_batch_runner.py` — Multi-job orchestration with parallel execution

### Established Patterns
- Pydantic v2 schemas for input/output (DiffractionSpec, DiffractionResults)
- Section-based reporting in `orcawave/reporting/` (7 section modules)
- Click CLI entry points in `diffraction/cli.py`

### Integration Points
- OrcFxAPI is consumed by: orcawave_runner.py, result_extractor.py, orcawave_converter.py, orcawave/reporting/builder.py
- Non-license code: spec_converter.py, orcawave_backend.py, report_data_models.py, comparison_framework.py
- Benchmark data at docs/domains/orcawave/ feeds smoke test

</code_context>

<specifics>
## Specific Ideas

- Remote Claude Code trigger from dev-primary to licensed-win-1 is the execution model for the entire v1.1 milestone — Phase 7 proves this works
- WRK-031 benchmark previously stalled at this exact point — Phase 7 is designed to surface and resolve blockers before any development begins

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

### Reviewed Todos (not folded)
All matched todos were folded into scope.

</deferred>

---

*Phase: 07-solver-verification-gate*
*Context gathered: 2026-03-30*
