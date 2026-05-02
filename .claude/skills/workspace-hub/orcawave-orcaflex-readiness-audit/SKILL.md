---
name: orcawave-orcaflex-readiness-audit
description: Audit the real readiness of digitalmodel OrcaWave/OrcaFlex spec-driven workflows by reconciling workspace-hub issues, source/tests, semantic-equivalence boundaries, and wiki synthesis gaps.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [workspace-hub, digitalmodel, orcawave, orcaflex, readiness-audit, semantic-equivalence, llm-wiki]
    related_skills: [digitalmodel-orcawave-orcaflex-workflow, github-issues, llm-wiki, knowledge-source-recon]
---

# OrcaWave / OrcaFlex Readiness Audit

Use this when the user asks questions like:
- what is actually ready in OrcaWave/OrcaFlex?
- where does `spec.yml` generate semantically equivalent solver inputs?
- which issues are stale vs real gaps?
- what structures/families are already represented?
- what do the LLM-wikis still lack for this domain?

## Core lesson

Do NOT treat old issue bodies as current truth.
This domain has multiple issues that still read like greenfield work even though the code, tests, and fixtures already exist.

## Audit sequence

1. Read the three anchor docs first:
   - `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`
   - `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md`
   - `docs/reports/digitalmodel-orcawave-orcaflex-issue-reconciliation.md`

2. Query issues from `workspace-hub`, not from `digitalmodel/`.
   - The canonical issue tracker for this domain is the workspace-hub repo.
   - `gh issue view` from `digitalmodel/` may fail with “Could not resolve to an issue” for valid issue numbers.

3. Reconcile issue state against source + tests.
   Important historically stale / already-implemented issues to verify first:
   - `#1588`, `#1596`, `#1598` — DiffractionSpec / parametric-spec pipeline
   - `#1597` — RAO extractor and DB population
   - `#1592`, `#1605`, `#1768` — OrcaWave -> OrcaFlex handoff and validation

4. Verify readiness with focused tests before making claims.
   High-signal test slice:
   - `tests/hydrodynamics/diffraction/test_parametric_spec_generator.py`
   - `tests/hydrodynamics/diffraction/test_orcawave_to_orcaflex_pipeline.py`
   - `tests/hydrodynamics/diffraction/test_orcawave_to_orcaflex_integration.py`
   - `tests/solvers/orcaflex/modular_generator/test_semantic_roundtrip.py`

   In digitalmodel, a strong local command is:
   `PYTHONPATH=src ./.venv/bin/python -m pytest <focused files> -q`

5. Inventory current structure/template families from `docs/domains/orcaflex/` and `docs/domains/orcawave/` rather than relying on roadmap counts alone.

6. Review the wikis separately for:
   - breadth of raw/source coverage
   - synthesis quality for operator use

## Claim-boundary rules

Keep semantic-equivalence claims conservative and solver-specific.

### OrcaWave
Say:
- strong for engineering-significant round-trip fidelity
- not guaranteed literal identity across every strict OrcaWave YAML field

Back this by checking:
- `docs/domains/orcawave/README.md`
- roundtrip/semantic tests in `tests/hydrodynamics/diffraction/`

### OrcaFlex
Say:
- forward `spec.yml -> modular/single YAML` is the strong path
- reverse extraction remains best-effort only

Back this by checking:
- `docs/domains/orcaflex/QUICKSTART_FILE_CONVERSION.md`
- `docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md`
- semantic roundtrip tests under `tests/solvers/orcaflex/modular_generator/`

### Distinguish these four claims explicitly
Never blur them:
1. engineering-equivalent behavior
2. strict YAML parity
3. solver-loadable parity
4. benchmark-validated parity

## What “ready” usually means in this domain

Classify each workstream into one of these buckets:

1. Ready now
   - implemented in source
   - backed by tests and/or committed fixtures

2. Ready but needs stronger evidence
   - code exists
   - tests exist but mainly benchmark/fixture-based
   - needs licensed-machine or real-project proof

3. Real gap
   - still requires substantive implementation

## Common real gaps even when the core pipeline exists

These often remain open after the base `spec.yml` pipeline is implemented:
- standards-driven DLC matrix generation
- richer hull/structure registries
- more real project families and golden models
- licensed-machine fixture and snapshot proof
- clearer wiki synthesis of the canonical-contract boundary

## LLM-wiki audit shortcut

The engineering wiki already tends to contain seed pages such as:
- OrcaFlex Solver
- OrcaWave Solver
- Diffraction Analysis System
- OrcaWave-to-OrcaFlex Pipeline

But these audits should assume the synthesis layer is still incomplete.

Typical missing pages / weakly synthesized topics:
- `DiffractionSpec` as a first-class canonical contract
- OrcaFlex `ProjectInputSpec` / modular-generator contract
- semantic-equivalence claim-boundary comparison page
- `RAODatabase` provenance page
- hull-registry / structure-registry readiness page
- case-study pages for risers, jumpers, semisubs, turret mooring, and installation families

Specific wiki drift found in the April 2026 readiness review:
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` may still describe the handoff as `.owr -> RAO extraction`; the current dev-primary bridge is xlsx sidecar -> `RAOData` -> `DiffractionResults` -> OrcaFlex export.
- The engineering wiki has seed pages for OrcaFlex, OrcaWave, Diffraction Analysis System, and OrcaWave-to-OrcaFlex Pipeline, but it lacks operator-ready pages for the canonical spec contract and structure readiness matrix.
- Recommended wiki synthesis pages: `Canonical Spec Contract: OrcaWave vs OrcaFlex`, `DiffractionSpec Canonical Contract`, `ProjectInputSpec Canonical Contract`, `Semantic Equivalence Taxonomy for Marine Solver Inputs`, `RAODatabase Provenance and xlsx Sidecar Workflow`, `Structure Readiness Matrix`, and case studies for turret-moored FPSO, PLET-to-PLEM rigid jumper, lazy/steep-wave riser, L03 ship benchmark, CALM/SPM, and semi-sub/FOWT.

So always report wiki findings in two layers:
1. raw/source breadth exists
2. operator-ready synthesis does not yet exist

## Good final-output structure

For user-facing readiness reviews, produce:
1. the canonical `spec.yml -> native input` workstreams
2. what is ready now
3. the most important remaining gaps
4. which structure families already exist
5. which structure families should be added next
6. LLM-wiki coverage vs synthesis gaps
7. a ranked next-step issue list

## Recently discovered issue anchors for canonical-spec proof

When auditing current work, include these newer proof-expansion issues if present:
- `#2454` — flagship generic-track OrcaFlex mooring case / turret-moored FPSO semantic proof
- `#2455` — rigid jumper family / PLET-to-PLEM semantic proof
- `#2456` — lazy-wave / steep-wave riser semantic proof
- `#2457` — OrcaWave L03 ship benchmark explicit roundtrip proof

Use these alongside the older foundation issues. The practical order is usually:
1. `#1652` + `#1788` for real OrcaFlex `.sim` fixture/report/snapshot proof
2. `#2454`, `#2455`, `#2456` for OrcaFlex family-level semantic proof
3. `#2457` for named OrcaWave flagship proof
4. `#1586` for queue traceability/repeatability
5. `#1637`, `#1591`, `#1594` for scalable sweeps, hull registry, and standards-driven DLC campaigns
