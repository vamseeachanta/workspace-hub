# Tier-1 Indexing Freshness Audit — Latest

- **Run timestamp:** 2026-05-12 03:33:37 -0500 (CDT)
- **ISO timestamp:** 2026-05-12T03:33:37-05:00
- **Scope:** workspace-hub, digitalmodel, assetutilities, aceengineer-website
- **Mode:** scheduled local freshness audit; no cron jobs created or modified
- **Material drift summary:** no material drift detected at the status level.

## Executive Summary

No status-level material drift detected against the 2026-05-11 freshness baseline. The timestamp was refreshed and current evidence was rechecked. Portfolio status remains **RED** because workspace-hub and aceengineer-website still lack required routing/index surfaces.

The 2026-04-22 tier-1 indexing scorecard assumptions still hold **directionally**: tier-1 repos still need explicit canonical routing surfaces to support reliable GitHub issue execution. They need **current-state revision** for point-in-time details: assetutilities now has the required canonical surfaces; aceengineer-website has docs/operator surfaces but still lacks the machine-readable registry; digitalmodel remains structurally strong with a small number of stale references; workspace-hub remains the noisiest control-plane index.

## Status Table

| Repo | Status | Broken or missing surfaces | Concise next action |
|---|---:|---|---|
| `workspace-hub` | **red** | missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; 4 broken Markdown link(s); 5 stale legacy `.agent-os` reference(s); runtime/cache/build noise present | Add current operator map and registry; replace stale legacy references with canonical routing surfaces; reduce root/index noise. |
| `digitalmodel` | **yellow** | 1 broken Markdown link(s); 2 stale path reference(s); runtime/cache/build noise present | Fix stale `specs/data-needs.yaml` and repo-local operator-map reference; continue preserving source/test structure. |
| `assetutilities` | **yellow** | runtime/cache/build noise present | Clean trusted-path runtime/cache noise; keep existing registry/operator surfaces current. |
| `aceengineer-website` | **red** | missing `docs/registry/module-routing.yaml`; runtime/cache/build noise present | Add `docs/registry/module-routing.yaml`; keep docs/operator map aligned with source/docs structure. |

## workspace-hub

- **Path:** `/mnt/local-analysis/workspace-hub`
- **Status:** **red**
- **Red reasons:** missing docs/registry/module-routing.yaml; missing docs/maps/workspace-hub-operator-map.md
- **Yellow reasons:** broken/stale references in canonical surfaces; runtime/cache/build noise present
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/workspace-hub-operator-map.md`: MISSING
  - `docs/registry/module-routing.yaml`: MISSING
- **Exact broken/missing/stale evidence:**
  - Missing surface: `docs/maps/workspace-hub-operator-map.md`
  - Missing surface: `docs/registry/module-routing.yaml`
  - Broken Markdown link: `docs/README.md:299 -> ../.agent-os/product/mission.md`
  - Broken Markdown link: `docs/README.md:300 -> ../.agent-os/product/tech-stack.md`
  - Broken Markdown link: `docs/README.md:301 -> ../.agent-os/product/roadmap.md`
  - Broken Markdown link: `docs/README.md:302 -> ../.agent-os/product/decisions.md`
  - Stale legacy reference, not a recommended routing pattern: `docs/README.md:263 -> ├── .agent-os/              # Agent OS configuration`
  - Stale legacy reference, not a recommended routing pattern: `docs/README.md:299 -> - [Mission & Vision](../.agent-os/product/mission.md)`
  - Stale legacy reference, not a recommended routing pattern: `docs/README.md:300 -> - [Technical Stack](../.agent-os/product/tech-stack.md)`
  - Stale legacy reference, not a recommended routing pattern: `docs/README.md:301 -> - [Development Roadmap](../.agent-os/product/roadmap.md)`
  - Stale legacy reference, not a recommended routing pattern: `docs/README.md:302 -> - [Product Decisions](../.agent-os/product/decisions.md)`
  - Root/index noise: `.cache`, `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `dist`, `logs`, `node_modules`, `reports`, `tmp`
  - Trusted-path noise sample: `src/__pycache__/`, `src/ace/__pycache__/`, `src/config/__pycache__/`, `src/geometry/__pycache__/`, `src/knowledge_graph/__pycache__/`, `src/models/__pycache__/`, `src/solvers/__pycache__/`, `src/utilities/__pycache__/`, `src/workspace_hub/reports/`, `src/__pycache__/__init__.cpython-311.pyc`, `src/__pycache__/__init__.cpython-312.pyc`, `src/__pycache__/__init__.cpython-313.pyc`, `src/workspace_hub/math/__pycache__/`, `src/workspace_hub/workstations/__pycache__/`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-311.pyc`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-312.pyc`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-313.pyc`, `src/workspace_hub/workstations/__pycache__/__init__.cpython-311.pyc`, `src/workspace_hub/workstations/__pycache__/__init__.cpython-312.pyc`, `src/workspace_hub/workstations/__pycache__/__init__.cpython-313.pyc` ... (+30 more)
- **Next actions:**
  1. Create `docs/maps/workspace-hub-operator-map.md` as the current repo-local operator map.
  2. Create/update `docs/registry/module-routing.yaml` for machine-readable routing.
  3. Replace stale legacy `.agent-os` links in `docs/README.md` with current canonical routing surfaces; do not reintroduce legacy reference patterns.
  4. Move/cache-ignore runtime/build/report noise so root/index trust is not diluted.

## digitalmodel

- **Path:** `/mnt/local-analysis/workspace-hub/digitalmodel`
- **Status:** **yellow**
- **Yellow reasons:** broken/stale references in canonical surfaces; runtime/cache/build noise present
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/digitalmodel-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Exact broken/missing/stale evidence:**
  - Broken Markdown link: `digitalmodel/README.md:73 -> specs/data-needs.yaml`
  - Stale path/reference: `digitalmodel/README.md:73 -> specs/data-needs.yaml`
  - Stale path/reference: `digitalmodel/docs/maps/digitalmodel-operator-map.md:9 -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`
  - Root/index noise: `.benchmarks`, `.coverage`, `.hypothesis`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build`, `dist`, `logs`, `reports`
  - Trusted-path noise sample: `src/digitalmodel/__pycache__/`, `src/digitalmodel/infrastructure/__pycache__/`, `src/digitalmodel/marine_ops/__pycache__/`, `src/digitalmodel/naval_architecture/__pycache__/`, `src/digitalmodel/nde/__pycache__/`, `src/digitalmodel/orcaflex/__pycache__/`, `src/digitalmodel/orcawave/__pycache__/`, `src/digitalmodel/power/__pycache__/`, `src/digitalmodel/production_engineering/__pycache__/`, `src/digitalmodel/reservoir/__pycache__/`, `src/digitalmodel/solvers/__pycache__/`, `src/digitalmodel/specialized/__pycache__/`, `src/digitalmodel/specs/__pycache__/`, `src/digitalmodel/structural/__pycache__/`, `src/digitalmodel/subsea/__pycache__/`, `src/digitalmodel/visualization/__pycache__/`, `src/digitalmodel/web/__pycache__/`, `src/digitalmodel/well/__pycache__/`, `src/digitalmodel/workflows/__pycache__/`, `src/digitalmodel/__pycache__/engine.cpython-311.pyc` ... (+30 more)
- **Next actions:**
  1. Either restore/document `specs/data-needs.yaml` or remove the README reference.
  2. Fix `docs/maps/digitalmodel-operator-map.md` reference to the OrcaWave/OrcaFlex operator map by adding the repo-local file or pointing to the canonical workspace-level map explicitly.
  3. Keep `docs/registry/module-routing.yaml` synced as modules move.

## assetutilities

- **Path:** `/mnt/local-analysis/workspace-hub/assetutilities`
- **Status:** **yellow**
- **Yellow reasons:** runtime/cache/build noise present
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/assetutilities-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Exact broken/missing/stale evidence:**
  - Root/index noise: `.benchmarks`, `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build`, `dist`, `htmlcov`, `logs`, `reports`
  - Trusted-path noise sample: `src/assetutilities/__pycache__/`, `src/modules/web-contextualization/__pycache__/`, `src/modules/web-contextualization/__pycache__/content_indexer.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/pdf_processor.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/resource_fetcher.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/web_contextualizer.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/web_contextualizer_enhanced.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/`, `src/modules/agent_os/enhanced_create_specs/__pycache__/ai_persistence_system.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/cross_repository_integration.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/cross_repository_integration.cpython-313.pyc`, `src/assetutilities/calculations/__pycache__/`, `src/assetutilities/common/__pycache__/`, `src/assetutilities/constants/__pycache__/`, `src/assetutilities/devtools/__pycache__/`, `src/assetutilities/modules/__pycache__/`, `src/assetutilities/units/__pycache__/`, `src/assetutilities/__pycache__/engine.cpython-311.pyc`, `src/assetutilities/__pycache__/engine.cpython-312.pyc`, `src/assetutilities/__pycache__/math_helpers.cpython-311.pyc` ... (+30 more)
- **Next actions:**
  1. Remove or ignore runtime/cache noise under trusted paths.
  2. Continue using `docs/registry/module-routing.yaml` and the operator map as the canonical placement surfaces.

## aceengineer-website

- **Path:** `/mnt/local-analysis/workspace-hub/aceengineer-website`
- **Status:** **red**
- **Red reasons:** missing docs/registry/module-routing.yaml
- **Yellow reasons:** runtime/cache/build noise present
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/aceengineer-website-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: MISSING
- **Exact broken/missing/stale evidence:**
  - Missing surface: `docs/registry/module-routing.yaml`
  - Root/index noise: `.benchmarks`, `.coverage`, `.pytest_cache`, `dist`, `logs`, `node_modules`, `reports`
  - Trusted-path noise sample: `tests/__pycache__/`, `tests/docs/__pycache__/`, `tests/python/__pycache__/`, `tests/repo_structure/__pycache__/`, `tests/__pycache__/__init__.cpython-312.pyc`, `tests/__pycache__/__init__.cpython-313.pyc`, `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`, `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_content_sync.cpython-313-pytest-9.0.3.pyc`, `tests/python/__pycache__/test_wrk146_positioning.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_wrk146_positioning.cpython-313.pyc`, `tests/python/__pycache__/__init__.cpython-312.pyc`, `tests/python/__pycache__/__init__.cpython-313.pyc`, `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
- **Next actions:**
  1. Add `docs/registry/module-routing.yaml` covering website content/source/test routing.
  2. Keep `docs/maps/aceengineer-website-operator-map.md` aligned with actual source/docs paths.
  3. Re-run freshness audit after registry lands.

## 2026-04-22 Scorecard Assumption Check

- **Still holds directionally:** Yes. The repo set still depends on explicit README/docs/operator-map/registry surfaces for reliable code placement and retrieval.
- **Needs current-state revision:** Yes. Some point-in-time findings from 2026-04-22 are stale: assetutilities now has required canonical surfaces; aceengineer-website now has docs/operator surfaces but lacks the machine-readable registry; digitalmodel has narrow stale references rather than broad routing absence.
- **Portfolio status:** RED until workspace-hub and aceengineer-website have the missing registry/operator surfaces and workspace-hub root/index noise is reduced.

## Verification

- Report was written locally only.
- No new cron jobs were scheduled.
- Report file: `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`
- File existence, size, mtime, and checksum were verified after refresh in the cron run output.
