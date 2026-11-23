# Archived Skill: `orcaflex-reporting-fixture-proof-pattern`

Original path: `/home/vamsee/.hermes/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/digitalmodel/orcaflex-reporting-fixture-proof-pattern`
Consolidation date: 2026-04-29

---

---
name: orcaflex-reporting-fixture-proof-pattern
description: Build and extend fixture-backed OrcaFlex reporting proof paths in digitalmodel using stable metadata baselines, normalized HTML snapshots, and reusable reporting test helpers.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# OrcaFlex Reporting Fixture Proof Pattern

Use when strengthening OrcaFlex proof/validation issues like real-fixture reporting, snapshot testing, or bounded family-level proof paths in digitalmodel.

## When to use
- You need a repo-friendly proof path for OrcaFlex reporting without requiring OrcFxAPI on every machine
- A roadmap issue needs concrete file-level implementation, not just acceptance criteria
- You want to extend a proof baseline from one fixture to additional structure families (FPSO, jumper, riser)
- You need stable artifacts that survive git review and regression testing

## Core pattern

For each fixture/family, create this artifact set:

1. Fixture metadata baseline
- `digitalmodel/tests/fixtures/reporting/<fixture>.metadata.json`
- Keep it deterministic, bounded, and reviewable
- Include fixture identity, provenance, model/object counts, stable object names, stable environment/general summary, and report-facing summary fields
- Exclude timestamps, machine-local paths, volatile IDs, and giant raw property bags

2. Snapshot baseline
- `digitalmodel/tests/fixtures/reporting/<fixture>.report.snapshot.html`
- Generate from the report codepath, then normalize via helper logic
- Snapshot should represent the normalized structural surface, not raw unstable output

3. Helper modules (shared across fixtures)
- `digitalmodel/tests/solvers/orcaflex/reporting/fixture_helpers.py`
- `digitalmodel/tests/solvers/orcaflex/reporting/snapshot_helpers.py`

4. Fixture tests
- `digitalmodel/tests/solvers/orcaflex/reporting/test_<family>_fixture_integration.py`
- `digitalmodel/tests/solvers/orcaflex/reporting/test_<family>_fixture_snapshot.py`

5. Optional semantic-diff artifact
- `digitalmodel/tests/fixtures/reporting/<fixture>.semantic_diff.json`
- Use to record the current bounded proof claim and taxonomy state even before full-model semantic closure exists

## Implementation sequence

### Phase 1: Establish the proof-standard baseline
Do this once first (for a minimal fixture):
1. Add `README.md` under `tests/fixtures/reporting/`
2. Add `<fixture>.metadata.json`
3. Build `fixture_helpers.py`
4. Build `snapshot_helpers.py`
5. Add integration test
6. Add snapshot test
7. Generate real snapshot baseline from current output
8. Run the focused fixture tests until they pass

### Phase 2: Generalize helpers before adding families
Before cloning the pattern to new families:
- refactor helper path resolution so fixtures are addressed by fixture name, not hardcoded paths
- add generic functions like:
  - `fixture_metadata_path(fixture_name)`
  - `fixture_snapshot_path(fixture_name)`
  - `load_fixture_metadata(fixture_name)`
  - `generate_fixture_report(fixture_name, tmp_path, ...)`
- keep fixture-specific branching in helper builders small and explicit

### Phase 3: Extend to new families one at a time
For each new family issue:
1. Identify the canonical spec file
2. Identify monolithic/native reference if it exists
3. Identify modular reference set if it exists
4. Add bounded metadata baseline
5. Add family integration test
6. Generate family snapshot baseline
7. Add family snapshot test
8. Run the whole reporting fixture suite, not just the new tests

## Proven family progression
This pattern was extended successfully in the following order:
1. `minimal_test` proof-standard baseline
2. `fpso_turret` generic-track flagship family
3. `jumper_plet_plem` rigid jumper family
4. `riser_lazy_wave_fpso` lazy-wave riser family

Use this same progression logic for additional families: start from the smallest bounded representative case with a clean canonical spec + reference set.

## Metadata guidance

### Good fields
- fixture name and canonical source paths
- provenance (`generated_on_machine`, `generated_from`, `orcaflex_version`, extraction mode)
- model state / structure type guess
- object counts by type
- small set of named objects (vessels, lines, constraints, buoys)
- report summary (`project_name`, `structure_id`, `structure_type`, booleans for available sections)

### Avoid
- raw OrcaFlex dumps
- giant arrays unless they are essential to the report surface
- unstable IDs
- timestamps unless normalized away
- absolute local paths

## Snapshot guidance

### Good snapshot scope
- section IDs
- titles
- stable tables
- stable rendered structure from deterministic helper-built reports

### Avoid
- brittle full-output assumptions before normalization
- volatile IDs / timestamps / path strings
- mixing multiple fixture families into one shared snapshot

## Semantic-diff scaffolding
Before full model-wide semantic equivalence is finished, add lightweight bounded artifacts like:
- `<fixture>.semantic_diff.json`
- record claim level such as `L2-bounded-reporting-path`
- set `loadability: pass` for the bounded reporting surface when true
- leave full-model physics-significant closure explicitly unresolved if not yet proven

This lets issues show progress without over-claiming full semantic identity.

## Testing commands
Prefer focused runs first:
- `PYTHONPATH=src ./.venv/bin/python -m pytest tests/solvers/orcaflex/reporting/test_fixture_integration.py tests/solvers/orcaflex/reporting/test_fixture_snapshot.py -q`

Then expand as families are added:
- run the full reporting fixture suite covering minimal + family fixtures together

If a newly added fixture causes regressions, regenerate the snapshot baseline from the deterministic helper path only after confirming the structural surface is the intended one.

## Common pitfalls and fixes

### 1. Wrong fixture path root
Symptom:
- tests look under `tests/solvers/fixtures/...` instead of `tests/fixtures/...`
Fix:
- compute fixture root from helper file location carefully; verify with a real pytest run immediately after creating the helper

### 2. Relative test imports fail during collection
Symptom:
- `ImportError: attempted relative import with no known parent package`
Fix:
- use absolute imports from `tests.solvers.orcaflex.reporting...` in the new test files

### 3. Snapshot baseline drift
Symptom:
- snapshot tests fail because helper-built output changed after helper enhancement
Fix:
- regenerate the snapshot from the current deterministic report path only after confirming the new structure is intentional

### 4. Over-specialized helpers
Symptom:
- helper code forks into one-off fixture branches too early
Fix:
- first generalize path/load/generate functions by fixture name; keep family-specific geometry/material/load mappings small and explicit

### 5. Over-claiming semantic closure
Symptom:
- a reporting-path pass is treated as full-model semantic equivalence
Fix:
- document bounded claim level explicitly (`L2-bounded-reporting-path`) and keep full-model taxonomy closure as future work

## Recommended closure wording for issues
For family issues, use language like:
- "strong bounded evidence for the reporting-facing proof path"
- "full close still requires explicit taxonomy-based difference classification if the issue is interpreted as full semantic-equivalence proof"

This keeps claims honest while still marking real progress.

## What to update in GitHub after landing code
Comment back on the issue with:
- exact files added
- exact source spec/reference set used
- exact pytest command
- pass/fail result
- bounded interpretation of what is now proven

This makes the code and issue state stay synchronized and prevents later roadmap drift.
