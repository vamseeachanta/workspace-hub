# OpenFOAM GitHub issues review and execution prompts

Goal: review the currently open OpenFOAM-related GitHub issues in `vamseeachanta/digitalmodel`, identify what is actually actionable now, and prepare execution-ready prompts for coding agents.

Repo reviewed: `vamseeachanta/digitalmodel`
Date: 2026-04-02

## Issues reviewed

### Relevant and actionable
1. `#139` — `WRK-047: OpenFOAM CFD analysis capability for digitalmodel`
2. `#154` — `WRK-1250: OpenFOAM deep solver workflows — tutorial reproduction, marine templates, convergence automation`
3. `#155` — `WRK-1252: Full CAD-to-CFD pipeline — FreeCAD → gmsh → OpenFOAM → ParaView end-to-end automation`
4. `#63` — `engg debt | openFOAM` (legacy umbrella / debt issue)

### Not actually an OpenFOAM execution candidate
- `#171` is returned by GitHub search for `openfoam`, but the issue body is about metocean aggregation in `worldenergydata`. Treat it as search noise / metadata mismatch, not an OpenFOAM execution target.

## Current codebase reality

Existing OpenFOAM implementation already present in `digitalmodel`:
- `src/digitalmodel/solvers/openfoam/`
  - `models.py`
  - `case_builder.py`
  - `domain_builder.py`
  - `marine_solvers.py`
  - `parametric.py`
  - `cli.py`
  - plus supporting files referenced by issue #139
- Existing tests:
  - `tests/solvers/openfoam/test_models.py`
  - `tests/solvers/openfoam/test_case_builder.py`
  - `tests/solvers/openfoam/test_marine_solvers.py`
  - `tests/solvers/openfoam/test_post_processing.py`
  - `tests/solvers/openfoam/test_parametric.py`
  - `tests/solvers/openfoam/test_mesh_pipeline.py`
- Existing pipeline prototype in workspace-hub:
  - `scripts/pipelines/gmsh_openfoam_orcaflex.py`
  - `scripts/pipelines/convert_gmsh_to_openfoam.py`
  - `scripts/pipelines/convert_openfoam_to_orcaflex.py`
  - `scripts/pipelines/test_cylinder_in_flow.py`
- Research / implementation notes already available:
  - `docs/research/openfoam-wrk047-refresh.md`
  - `docs/research/openfoam-tutorials.md`
  - `docs/research/openfoam-dict-patterns.md`

## Recommended execution order

1. `#139` first
   - It is mostly complete and can likely be finished by documentation + run/output strategy work.
   - It reduces ambiguity for all downstream work.
2. `#154` second
   - Builds operational depth on top of `#139`.
3. `#155` third
   - Capstone integration item; should consume the outputs/patterns from `#154`.
4. `#63` last
   - Treat as cleanup / closure / decomposition issue after the concrete WRKs above are updated.

## Review summary by issue

### #139 — WRK-047
Assessment:
- This is no longer a greenfield implementation issue.
- The core module and tests already exist.
- The remaining work in the issue body is mostly:
  - user-facing documentation
  - output storage strategy
  - run-management conventions
- Best execution posture: finish, document, reconcile issue text with repository reality.

### #154 — WRK-1250
Assessment:
- Good next implementation issue.
- It has clear acceptance criteria and aligns with existing research in `docs/research/openfoam-tutorials.md`.
- Should be executed in TDD slices using tutorial reproduction + convergence parsing as the backbone.

### #155 — WRK-1252
Assessment:
- Valuable capstone, but should not be first.
- It depends on stronger OpenFOAM runtime workflow maturity and probably stronger integration with gmsh / FreeCAD workstreams.
- Prompt should emphasize dry-run compatibility, diagnostics, and known-answer validation.

### #63 — engg debt | openFOAM
Assessment:
- Legacy umbrella issue that overlaps newer WRKs.
- Best handled as issue hygiene:
  - reconcile with #139 / #154 / #155
  - either close as superseded or rewrite as an explicit umbrella tracker.

## Execution prompt 1 — Issue #139 (finish and reconcile WRK-047)

Use this prompt with a coding agent:

```text
You are working in the `digitalmodel` repo on GitHub issue #139: WRK-047 OpenFOAM CFD analysis capability.

Important workspace rules:
- Plan before acting.
- TDD is mandatory.
- Use `uv run` for Python commands.
- Commit to `main` and push immediately once work is complete.
- Do not hardcode secrets.

Goal:
Finish the remaining work for WRK-047 by reconciling the issue with the codebase reality, adding the missing user-facing documentation, and implementing/documenting the output storage + run-management strategy described in the issue.

First inspect these files:
- `src/digitalmodel/solvers/openfoam/__init__.py`
- `src/digitalmodel/solvers/openfoam/models.py`
- `src/digitalmodel/solvers/openfoam/case_builder.py`
- `src/digitalmodel/solvers/openfoam/domain_builder.py`
- `src/digitalmodel/solvers/openfoam/marine_solvers.py`
- `src/digitalmodel/solvers/openfoam/parametric.py`
- `src/digitalmodel/solvers/openfoam/cli.py`
- `tests/solvers/openfoam/test_models.py`
- `tests/solvers/openfoam/test_case_builder.py`
- `tests/solvers/openfoam/test_marine_solvers.py`
- `tests/solvers/openfoam/test_post_processing.py`
- `tests/solvers/openfoam/test_parametric.py`
- `tests/solvers/openfoam/test_mesh_pipeline.py`
- `docs/research/openfoam-wrk047-refresh.md`
- `docs/research/openfoam-dict-patterns.md`
- `docs/research/openfoam-tutorials.md`

Required outcomes:
1. Write a concise user-facing OpenFOAM workflow document covering:
   - supported case types
   - setup flow
   - parametric studies
   - post-processing outputs
   - known limitations / runtime dependencies
2. Implement or formalize the output storage strategy from issue #139:
   - git-tracked inputs vs non-git-tracked CFD outputs
   - configurable output root
   - run metadata/index structure
   - log capture conventions
3. Add/extend tests first for any code changes.
4. Update issue-facing documentation artifacts in the repo so issue #139 can be accurately advanced toward closure.

Suggested implementation direction:
- Prefer adding a small configuration model / helper for output-root and run metadata rather than spreading path logic ad hoc.
- Keep current `src/digitalmodel/solvers/openfoam/` structure.
- Keep PyFoam supplementary, not foundational.

Validation commands:
- `uv run pytest digitalmodel/tests/solvers/openfoam -q`
- any additional targeted tests you add

Deliverables:
- code and tests if needed
- user-facing documentation file(s)
- short completion note summarizing what remains, if anything
```

## Execution prompt 2 — Issue #154 (deep solver workflows)

```text
You are working in the `digitalmodel` repo on GitHub issue #154: WRK-1250 OpenFOAM deep solver workflows.

Important workspace rules:
- Plan before acting.
- TDD is mandatory.
- Use `uv run` for Python commands.
- Commit to `main` and push immediately once complete.

Goal:
Move the existing OpenFOAM support from case generation to executable, monitored, validated solver workflows.

Before coding, inspect:
- `src/digitalmodel/solvers/openfoam/`
- `tests/solvers/openfoam/`
- `docs/research/openfoam-tutorials.md`
- `docs/research/openfoam-wrk047-refresh.md`
- any existing runtime / pipeline helpers already used in the repo

Implement in small TDD slices:
1. tutorial reproduction harnesses for:
   - cavity
   - damBreak
   - one steady validation case appropriate for current support
2. convergence monitor / log parser:
   - residual extraction
   - divergence detection
   - Courant number parsing if available
   - machine-readable summary
3. post-processing outputs:
   - force extraction to pandas-friendly structure
   - free-surface / probe extraction where supported
   - convergence plot artifact
4. CLI or Python API entry points for these workflows

Constraints:
- Use real OpenFOAM execution paths where feasible, but preserve testability with fixtures/mocks.
- Avoid overcoupling to a single OpenFOAM distribution layout.
- Follow the research notes that say Jinja2 + subprocess is the foundation; PyFoam may be supplementary.

Expected files to modify or add likely include:
- `src/digitalmodel/solvers/openfoam/*.py`
- `tests/solvers/openfoam/*.py`
- documentation under `docs/` as needed

Validation:
- targeted RED → GREEN tests for each slice
- `uv run pytest digitalmodel/tests/solvers/openfoam -q`
- if runtime tests are added, keep them appropriately marked / isolated

Definition of done:
- issue #154 acceptance criteria materially satisfied in code and tests
- workflow outputs are inspectable and deterministic enough for regression use
```

## Execution prompt 3 — Issue #155 (capstone CAD→CFD pipeline)

```text
You are working across `digitalmodel` and `workspace-hub` for GitHub issue #155: WRK-1252 FreeCAD → gmsh → OpenFOAM → ParaView pipeline.

Important workspace rules:
- Plan before acting.
- TDD is mandatory.
- Use `uv run` for Python commands.
- Commit to `main` and push immediately once complete.

Goal:
Build or harden a single end-to-end YAML-driven pipeline from geometry source through meshing, OpenFOAM setup/execution, and visualization artifacts.

Inspect first:
- `scripts/pipelines/gmsh_openfoam_orcaflex.py`
- `scripts/pipelines/convert_gmsh_to_openfoam.py`
- `scripts/pipelines/convert_openfoam_to_orcaflex.py`
- `scripts/pipelines/test_cylinder_in_flow.py`
- `src/digitalmodel/solvers/openfoam/`
- related gmsh / FreeCAD integration code in the repo
- `docs/research/openfoam-tutorials.md`
- `docs/research/openfoam-wrk047-refresh.md`

Required outcomes:
1. define a pipeline YAML schema
2. support dry-run mode that performs all non-solver generation steps
3. implement stage validation gates between:
   - geometry export
   - meshing
   - OpenFOAM case creation
   - solver execution
   - visualization/export artifacts
4. generate machine-readable diagnostics when a stage fails
5. provide at least one known-answer or regression-style validation case

Execution guidance:
- Reuse existing pipeline prototype code where it is solid.
- Do not build a monolith; keep stage adapters separate.
- Prefer explicit artifacts and structured result JSON/YAML over log scraping alone.
- ParaView state generation can be a thin first version if reproducible.

Validation:
- add tests first around schema, stage contracts, and dry-run behavior
- extend or reuse `scripts/pipelines/test_cylinder_in_flow.py`
- run the smallest deterministic subset in CI-friendly mode

Definition of done:
- pipeline can be executed from one config
- dry-run works without OpenFOAM installed
- failure diagnostics are explicit
- at least one end-to-end validation case passes
```

## Execution prompt 4 — Issue #63 (legacy issue cleanup)

```text
You are performing issue hygiene for GitHub issue #63 (`engg debt | openFOAM`) in `vamseeachanta/digitalmodel`.

Goal:
Determine whether #63 should be closed as superseded by newer WRKs (#139, #154, #155) or rewritten as a lightweight umbrella tracker.

Tasks:
1. inspect issues #63, #139, #154, #155
2. map each checklist item in #63 to the newer issues or to already-landed code
3. prepare a concise recommendation:
   - close as superseded, or
   - rewrite as umbrella tracker with links
4. if the repo policy/workflow supports it, draft the exact GitHub comment/body update text

Output:
- a short issue hygiene memo
- exact proposed comment text for GitHub
```

## Suggested execution queue

- Queue A: `#139`
- Queue B: `#154`
- Queue C: `#155`
- Admin cleanup after engineering execution: `#63`

## Suggested operator notes

- Exclude `#171` from OpenFOAM execution work.
- `#139` likely needs a reconciliation pass more than heavy implementation.
- `#154` is the best “real engineering execution” candidate now.
- `#155` should not lead the sequence unless you explicitly want prototype-first integration work.
