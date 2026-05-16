# Tier-1 Indexing Freshness Audit — Latest

- **Generated:** 2026-05-16T03:34:01-05:00
- **Scope:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
- **Working tree inspected:** `/mnt/local-analysis/workspace-hub`
- **Cron action:** no new cron jobs scheduled
- **Portfolio status:** **RED**
- **Material status drift:** no material drift detected at the status level; timestamp refreshed and current evidence revalidated

## Per-repo status

| Repo | Status | Exact broken/missing/stale surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **RED** | missing `docs/maps/workspace-hub-operator-map.md`<br>missing `docs/registry/module-routing.yaml`<br>broken `docs/README.md:300 -> ../.agent-os/product/mission.md`<br>broken `docs/README.md:301 -> ../.agent-os/product/tech-stack.md`<br>broken `docs/README.md:302 -> ../.agent-os/product/roadmap.md`<br>broken `docs/README.md:303 -> ../.agent-os/product/decisions.md`<br>legacy `docs/README.md:264: ├── .agent-os/              # Agent OS configuration`<br>legacy `docs/README.md:300: - [Mission & Vision](../.agent-os/product/mission.md)`<br>legacy `docs/README.md:301: - [Technical Stack](../.agent-os/product/tech-stack.md)`<br>legacy `docs/README.md:302: - [Development Roadmap](../.agent-os/product/roadmap.md)`<br>legacy `docs/README.md:303: - [Product Decisions](../.agent-os/product/decisions.md)`<br>root/index noise: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`, `CAD-DEVELOPMENTS/`, `Defines`, `GEMINI.md`, `MEMORY.md`, `OGManufacturing/`, `Planning`, `_archive/` (+81 more)<br>trusted-path noise (30 sample(s)): `src/__pycache__/__init__.cpython-311.pyc`, `src/__pycache__/__init__.cpython-312.pyc`, `src/__pycache__/__init__.cpython-313.pyc`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-311.pyc`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-312.pyc`, `src/workspace_hub/workstations/__pycache__/resolver.cpython-313.pyc`, `src/workspace_hub/workstations/__pycache__/__init__.cpython-311.pyc`, `src/workspace_hub/workstations/__pycache__/__init__.cpython-312.pyc`, … | Add/curate `docs/maps/workspace-hub-operator-map.md`; add `docs/registry/module-routing.yaml`; remove stale legacy references from `docs/README.md`; reduce root/index noise. |
| `digitalmodel` | **YELLOW** | broken `README.md:73 -> specs/data-needs.yaml`<br>stale `README.md:73 -> specs/data-needs.yaml`<br>stale `docs/maps/digitalmodel-operator-map.md:9 -> repo-local docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md missing; workspace-level map exists`<br>trusted-path noise (30 sample(s)): `src/digitalmodel/__pycache__/engine.cpython-311.pyc`, `src/digitalmodel/__pycache__/sections.cpython-311.pyc`, `src/digitalmodel/__pycache__/units.cpython-311.pyc`, `src/digitalmodel/__pycache__/units.cpython-312.pyc`, `src/digitalmodel/__pycache__/_compat.cpython-311.pyc`, `src/digitalmodel/__pycache__/_compat.cpython-312.pyc`, `src/digitalmodel/__pycache__/_compat.cpython-313.pyc`, `src/digitalmodel/__pycache__/__init__.cpython-311.pyc`, … | Fix/remove `specs/data-needs.yaml` reference; either add repo-local OrcaWave/OrcaFlex map or update map reference to canonical workspace-level path. |
| `assetutilities` | **YELLOW** | trusted-path noise (30 sample(s)): `src/modules/web-contextualization/__pycache__/content_indexer.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/pdf_processor.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/resource_fetcher.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/web_contextualizer.cpython-311.pyc`, `src/modules/web-contextualization/__pycache__/web_contextualizer_enhanced.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/ai_persistence_system.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/cross_repository_integration.cpython-311.pyc`, `src/modules/agent_os/enhanced_create_specs/__pycache__/cross_repository_integration.cpython-313.pyc`, … | Quarantine or ignore runtime/cache/log/report noise from trusted `src`/`tests`/`docs` paths; keep current operator map and registry fresh. |
| `aceengineer-website` | **RED** | missing `docs/registry/module-routing.yaml`<br>trusted-path noise (14 sample(s)): `tests/__pycache__/__init__.cpython-312.pyc`, `tests/__pycache__/__init__.cpython-313.pyc`, `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`, `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`, … | Add `docs/registry/module-routing.yaml` matching the repo operator map and current app/content routes. |

## Canonical surfaces inspected

### `workspace-hub`
- Path: `/mnt/local-analysis/workspace-hub`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/workspace-hub-operator-map.md`: MISSING
- `docs/registry/module-routing.yaml`: MISSING

### `digitalmodel`
- Path: `/mnt/local-analysis/workspace-hub/digitalmodel`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/digitalmodel-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present

### `assetutilities`
- Path: `/mnt/local-analysis/workspace-hub/assetutilities`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/assetutilities-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present

### `aceengineer-website`
- Path: `/mnt/local-analysis/workspace-hub/aceengineer-website`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/aceengineer-website-operator-map.md`: present
- `docs/registry/module-routing.yaml`: MISSING

## 2026-04-22 scorecard assumption check

The 2026-04-22 tier-1 indexing scorecard assumptions **partially still hold but need detail-level revision**.

Still holds:
- Portfolio remains only partially ready for reliable code placement and canonical retrieval because required routing registries are still missing in `workspace-hub` and `aceengineer-website`.
- `workspace-hub` remains the strongest control-plane repo but root/index hygiene and missing current routing surfaces keep trust weak.
- `digitalmodel` remains the strongest engineering source/test structure, with only stale-reference/map-locality issues in the inspected routing surfaces.

Needs revision:
- Several surfaces assumed absent in the original scorecard now exist: `digitalmodel/docs/README.md`, `digitalmodel/docs/maps/digitalmodel-operator-map.md`, `digitalmodel/docs/registry/module-routing.yaml`, `assetutilities/docs/README.md`, `assetutilities/docs/maps/assetutilities-operator-map.md`, `assetutilities/docs/registry/module-routing.yaml`, and `aceengineer-website/docs/maps/aceengineer-website-operator-map.md`.
- `assetutilities` no longer has confirmed active canonical Markdown broken links after false-positive filtering in this scan; its remaining issue is trusted-path runtime/cache/log/report noise.

## Scanner notes

- Markdown-link checks were limited to current canonical routing surfaces and filtered for wildcard/example/placeholders to avoid stale false positives.
- Legacy `.agent-os` references were detected only as stale legacy references and are not recommended as routing surfaces.
- Historical scorecards were treated as context, not authority; current files under the requested checkout were inspected.
