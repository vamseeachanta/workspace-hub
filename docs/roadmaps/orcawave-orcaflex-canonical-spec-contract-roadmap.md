# OrcaWave / OrcaFlex Canonical Spec Contract Roadmap

Updated: 2026-04-22
Purpose: one-page roadmap for strengthening the canonical contract from `spec.yml` to semantically equivalent solver-native analysis inputs.

## Contract boundary

- OrcaWave: treat the current claim as near-equivalent for key engineering inputs and tested pathways, not strict identity across every native YAML field.
- OrcaFlex: treat the forward path (`spec.yml` -> native/modular OrcaFlex input) as the primary contract; reverse extraction (`native` -> `spec.yml`) remains best-effort only.
- Therefore the roadmap focuses on forward-generation proof, repeatability, and coverage expansion.

## Current state summary

Already delivered foundations:
- `#1588` closed — hull_library -> DiffractionSpec bridge
- `#1596` closed — DiffractionSpec-compliant spec generation from sweep definitions
- `#1598` closed — end-to-end DiffractionSpec pipeline integration test
- `#1638` closed — native OrcaWave YAML reverse parser to DiffractionSpec
- `#1597` closed — result extraction / RAODatabase population path
- `#1605` closed — OrcaWave -> OrcaFlex integration validation
- `#1592` and `#1768` closed — automated OrcaWave -> OrcaFlex handoff implementation

Remaining strategic gap:
- strongest open gap is proving OrcaFlex forward semantic fidelity on real native artifacts using committed fixtures and taxonomy-backed validation

## Priority roadmap

### Priority 1 — prove forward native fidelity
Issue cluster:
- `#1652`
- `#1788`

Goal:
- prove that canonical `spec.yml` generation produces valid OrcaFlex-native artifacts with stable, reviewable outputs

Deliverables:
- minimal non-proprietary `.sim` fixture(s)
- fixture-backed integration tests
- HTML/metadata snapshot assertions
- semantic diff classification mapped to `SEMANTIC_DIFF_TAXONOMY.md`

Success signal:
- native artifacts load and validate on licensed machine
- allowed vs blocking differences are explicit and regression-tested

### Priority 2 — harden repeatability at batch scale
Issue cluster:
- `#1586`
- fold `#1595` into `#1586` or close as duplicate

Goal:
- make the contract operationally reliable across batch execution and post-processing

Deliverables:
- hardened queue behavior
- result watcher reliability
- artifact traceability from `spec.yml` -> queued job -> solver output -> validation artifact

Success signal:
- no silent drift or silent failure path between authored spec and validated solver output

### Priority 3 — broaden canonical coverage
Issue:
- `#1637`

Goal:
- expand the range of canonical specs that can be generated and validated safely

Deliverables:
- multidimensional sweep support
- CLI entry point
- output naming convention
- `max_specs` and other guardrails

Success signal:
- parameterized canonical-spec generation is easy to run and hard to misuse

### Priority 4 — expand reference hull corpus
Issue:
- `#1591`

Goal:
- seed a stronger registry of standard hulls for canonical diffraction workflows

Deliverables:
- standard hull registry
- barge, tanker/FPSO, semi-sub, spar, supply vessel, and preferably Series 60 starters

Success signal:
- canonical diffraction workflows have a curated, reusable family of reference inputs

### Priority 5 — scale to standards-driven case generation
Issue:
- `#1594`

Goal:
- move from single-model generation to production-grade standards-driven analysis campaigns

Deliverables:
- DLC matrix generator
- standards-linked environmental/load-case combinations
- batch-manifest integration

Success signal:
- standards-compliant case libraries can be generated from canonical inputs without manual case explosion work

## Structure readiness snapshot

Ready now:
- OrcaWave L00 validation family
- OrcaWave L02/L03/L04 benchmark hulls
- OrcaFlex catenary riser baseline
- OrcaFlex 24in floating pipeline installation baseline

Partial but high-value next validations:
- turret-moored FPSO
- PLET-to-PLEM rigid jumper
- lazy-wave / steep-wave riser
- OrcaWave L03 ship benchmark full roundtrip
- named multi-body OrcaWave benchmark - promoted under #2458

## Execution order

1. `#1652` + `#1788`
2. `#1586` and de-duplicate `#1595`
3. `#1637`
4. `#1591`
5. `#1594`

## Explicit non-priority items for this roadmap

These are useful, but not core blockers for the canonical spec contract itself:
- `#2123` — wiki search auto-invocation for OrcaFlex/OrcaWave skills
- `#2124` — Orcina resources/examples/training wiki ingestion
- `#2103` — AQWA/BEMRosetta wiki ingestion

## Bottom line

The original build-out path is mostly complete. The next phase is not greenfield generation work; it is proof, repeatability, and controlled expansion:

- prove OrcaFlex native forward fidelity on real fixtures
- harden batch repeatability
- broaden sweep-driven canonical coverage
- expand curated structure inputs
- scale into standards-driven case generation
