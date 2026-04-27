# Tier-1 Routing Index

Updated: 2026-04-27
Owner issue: #2464
Source contract: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

This is the curated workspace-hub routing surface for tier-1 issue execution. Use it to map issue type to repo and canonical path before using broad search or raw inventories.

## Portfolio Matrix

| Issue type | Repo | Canonical path | First validation surface |
|---|---|---|---|
| `cat:harness` / GSD workflow | `workspace-hub` | `docs/plans/`, `.claude/get-shit-done/`, `scripts/enforcement/` | `tests/docs/`, `tests/enforcement/` |
| `cat:documentation` / control-plane docs | `workspace-hub` | `docs/README.md`, `docs/standards/`, `docs/maps/` | `tests/docs/` |
| `cat:data-pipeline` / document intelligence | `workspace-hub` | `data/document-index/`, `docs/document-intelligence/`, `scripts/data/document-index/` | `tests/data/`, `tests/docs/` |
| `cat:engineering` / OrcaWave or diffraction | `digitalmodel` | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/`, `digitalmodel/src/digitalmodel/orcawave/` | `digitalmodel/tests/hydrodynamics/diffraction/`, `digitalmodel/tests/orcawave/` |
| `cat:engineering` / OrcaFlex workflows | `digitalmodel` | `digitalmodel/src/digitalmodel/solvers/orcaflex/`, `digitalmodel/src/digitalmodel/orcaflex/` | `digitalmodel/tests/solvers/orcaflex/`, `digitalmodel/tests/orcaflex/` |
| `cat:engineering-calculations` / reusable utilities | `assetutilities` | `assetutilities/src/assetutilities/` | `assetutilities/tests/` |
| `cat:website` / public site content | `aceengineer-website` | `aceengineer-website/` root pages and `aceengineer-website/docs/` | `aceengineer-website` build and link checks |
| Security, dependency, or CI workflow triage | Owning repo first, `workspace-hub` for portfolio plan evidence | `.github/`, `pyproject.toml`, `package.json`, `docs/security/` | targeted CI/test commands named in the issue plan |
| Cross-repo coordination or tier-1 freshness | `workspace-hub` | `docs/standards/TIER1_INDEXING_CHECKLIST.md`, `docs/reports/tier-1-indexing-freshness-latest.md` | `tests/docs/test_tier1_indexing_contract.py`, freshness audit tests |
| Large generated or raw artifacts | Owning repo plus bulk-artifact-store boundary | keep small curated references in repo; move large/generated outputs per `docs/standards/DATA_PLACEMENT.md` | data-placement checks named in the issue plan |

## Per-Repo Routing

### workspace-hub

- Role: portfolio control plane, issue planning, agent harness, durable standards, and document-intelligence registries.
- Entry points: `AGENTS.md`, `README.md`, `docs/README.md`, this file, and `data/document-index/intelligence-accessibility-registry.yaml`.
- Use `docs/plans/` for issue-approved implementation plans and `docs/standards/` for durable routing contracts.
- Do not place transient session output, dated email packets, or raw crawl output at repo root.

### digitalmodel

- Role: numerical models, offshore engineering calculation pipelines, OrcaWave, OrcaFlex, hydrodynamics, and solver workflows.
- Current strongest operator map: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`.
- Route OrcaWave and OrcaFlex implementation work to `digitalmodel/src/digitalmodel/` and matching `digitalmodel/tests/` surfaces after checking the repo's own `AGENTS.md` and README.
- Licensed solver execution remains machine-bound; use local tests first and route live solver proof through the approved solver queue or licensed-machine plan.

### assetutilities

- Role: shared Python utilities used by engineering repositories.
- Route reusable library work to `assetutilities/src/assetutilities/` with matching tests in `assetutilities/tests/`.
- Treat package structure and source-hygiene remediation as owned by #2461 until its canonical operator map and registry are complete.

### aceengineer-website

- Role: public website, marketing content, demos, calculators, and deployment assets.
- Route direct site edits to `aceengineer-website/` and supporting docs under `aceengineer-website/docs/`.
- Treat durable site routing and legacy product-doc reference cleanup as owned by #2463 until its operator map is complete.

## Curated vs Raw Inventory

Curated routing surfaces are the authority for issue work. They are intentionally small, reviewed, and linked from stable entry points:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml` where present
- this `docs/ROUTING_INDEX.md`
- `data/document-index/intelligence-accessibility-registry.yaml`

Raw inventory surfaces are discovery aids only. `docs/CONTENT_INDEX.md` is a machine-generated raw inventory and is not a curated routing index. Workers may use it to discover candidate files, but final code, test, docs, and registry placement must be confirmed through curated routing surfaces and the approved issue plan.

MUST NOT treat any tier-1 indexing scorecard under `docs/reports/` as required canonical authority. The current scorecard, `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`, is local attestation for #2464 and not a replacement for `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`.
