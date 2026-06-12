# Tier-1 Indexing Freshness Audit — Latest

**Generated:** 2026-06-12T03:33:47-05:00

**Scope:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` under `/mnt/local-analysis/workspace-hub` with sibling checkout fallback only when nested checkout is absent.

**Cron note:** No new cron jobs were scheduled.

**Material drift:** no material drift detected at the status level; timestamp refreshed and live evidence revalidated.

## Status Summary

| Repo | Status | Current blockers / drift | Next action |
|---|---:|---|---|
| `workspace-hub` | red | missing docs/registry/module-routing.yaml; missing docs/maps/workspace-hub-operator-map.md; 4 confirmed broken canonical Markdown link(s); 4 active legacy .agent-os/product reference line(s); 40 trusted-path/root cache-runtime artifact(s) detected | Add/refresh repo-local operator map and registry; remove active legacy routing links; clean root/source cache-runtime noise. |
| `digitalmodel` | red | 1 confirmed broken canonical Markdown link(s); 40 trusted-path/root cache-runtime artifact(s) detected | Fix confirmed broken README route(s); clean trusted src cache noise. |
| `assetutilities` | yellow | 40 trusted-path/root cache-runtime artifact(s) detected | Clean trusted src cache/runtime noise; keep registry/operator map current. |
| `aceengineer-website` | red | missing docs/registry/module-routing.yaml; 22 trusted-path/root cache-runtime artifact(s) detected | Add canonical `docs/registry/module-routing.yaml`; clean test cache noise. |

## Exact Surfaces Checked

### workspace-hub
- Checkout inspected: `/mnt/local-analysis/workspace-hub`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/workspace-hub-operator-map.md`: MISSING
- `docs/registry/module-routing.yaml`: MISSING
- Confirmed broken canonical Markdown links:
  - `docs/README.md:300` → `../.agent-os/product/mission.md` (resolved `/mnt/local-analysis/workspace-hub/.agent-os/product/mission.md`)
  - `docs/README.md:301` → `../.agent-os/product/tech-stack.md` (resolved `/mnt/local-analysis/workspace-hub/.agent-os/product/tech-stack.md`)
  - `docs/README.md:302` → `../.agent-os/product/roadmap.md` (resolved `/mnt/local-analysis/workspace-hub/.agent-os/product/roadmap.md`)
  - `docs/README.md:303` → `../.agent-os/product/decisions.md` (resolved `/mnt/local-analysis/workspace-hub/.agent-os/product/decisions.md`)
- Confirmed broken registry path references: none
- Legacy `.agent-os` / product-doc references observed in canonical surfaces:
  - `docs/README.md:300` — - [Mission & Vision](../.agent-os/product/mission.md)
  - `docs/README.md:301` — - [Technical Stack](../.agent-os/product/tech-stack.md)
  - `docs/README.md:302` — - [Development Roadmap](../.agent-os/product/roadmap.md)
  - `docs/README.md:303` — - [Product Decisions](../.agent-os/product/decisions.md)
- Trusted-path/root backup/cache/runtime noise detected:
  - `.mypy_cache`
  - `.pytest_cache`
  - `.ruff_cache`
  - `claude_smoke.log`
  - `src/__pycache__`
  - `src/__pycache__/__init__.cpython-311.pyc`
  - `src/__pycache__/__init__.cpython-312.pyc`
  - `src/__pycache__/__init__.cpython-313.pyc`
  - `src/ace/__pycache__`
  - `src/ace/__pycache__/cli.cpython-311.pyc`
  - `src/ace/__pycache__/cli.cpython-312.pyc`
  - `src/config/__pycache__`
  - `src/config/__pycache__/__init__.cpython-311.pyc`
  - `src/config/__pycache__/__init__.cpython-312.pyc`
  - `src/config/__pycache__/config_loader.cpython-311.pyc`
  - `src/config/__pycache__/config_loader.cpython-312.pyc`
  - `src/config/__pycache__/config_manager.cpython-311.pyc`
  - `src/config/__pycache__/config_manager.cpython-312.pyc`
  - `src/config/__pycache__/schema_validator.cpython-311.pyc`
  - `src/config/__pycache__/schema_validator.cpython-312.pyc`
  - `src/digitalmodel/subsea/pipeline/free_span/__pycache__`
  - `src/digitalmodel/subsea/pipeline/free_span/__pycache__/__init__.cpython-311.pyc`
  - `src/digitalmodel/subsea/pipeline/free_span/__pycache__/__init__.cpython-313.pyc`
  - `src/digitalmodel/subsea/pipeline/free_span/__pycache__/_bilinear_sn.cpython-311.pyc`
  - `src/digitalmodel/subsea/pipeline/free_span/__pycache__/models.cpython-311.pyc`
  - ... 15 more omitted

### digitalmodel
- Checkout inspected: `/mnt/local-analysis/digitalmodel`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/digitalmodel-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present
- Confirmed broken canonical Markdown links:
  - `README.md:73` → `specs/data-needs.yaml` (resolved `/mnt/local-analysis/digitalmodel/specs/data-needs.yaml`)
- Confirmed broken registry path references: none
- Legacy `.agent-os` / product-doc references in canonical surfaces: none
- Trusted-path/root backup/cache/runtime noise detected:
  - `src/digitalmodel/__pycache__`
  - `src/digitalmodel/ansys/__pycache__`
  - `src/digitalmodel/asset_integrity/__pycache__`
  - `src/digitalmodel/benchmarks/__pycache__`
  - `src/digitalmodel/cathodic_protection/__pycache__`
  - `src/digitalmodel/citations/__pycache__`
  - `src/digitalmodel/drilling_riser/__pycache__`
  - `src/digitalmodel/fatigue/__pycache__`
  - `src/digitalmodel/field_development/__pycache__`
  - `src/digitalmodel/geotechnical/__pycache__`
  - `src/digitalmodel/gis/__pycache__`
  - `src/digitalmodel/hydrodynamics/__pycache__`
  - `src/digitalmodel/infrastructure/__pycache__`
  - `src/digitalmodel/marine_ops/__pycache__`
  - `src/digitalmodel/marine_ops/artificial_lift/__pycache__`
  - `src/digitalmodel/marine_ops/ct_hydraulics/__pycache__`
  - `src/digitalmodel/marine_ops/installation/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/analysis/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/catenary/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/environmental_loading/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/extraction/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/hydrodynamic_coefficients/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/models/__pycache__`
  - `src/digitalmodel/marine_ops/marine_analysis/parsers/__pycache__`
  - ... 15 more omitted

### assetutilities
- Checkout inspected: `/mnt/local-analysis/assetutilities`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/assetutilities-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present
- Confirmed broken canonical Markdown links: none
- Confirmed broken registry path references: none
- Legacy `.agent-os` / product-doc references in canonical surfaces: none
- Trusted-path/root backup/cache/runtime noise detected:
  - `src/assetutilities/__pycache__`
  - `src/assetutilities/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/__pycache__/engine.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__`
  - `src/assetutilities/common/__pycache__/ApplicationManager.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/attribute_dict.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/data.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/data_management.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/datetime_utils.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/file_edit.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/file_edit_concatenate.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/file_edit_split.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/file_management.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/file_ops.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/number_format.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/path_resolver.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/saveData.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/set_logging.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/string_utils.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/text_analytics.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/transform.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/update_deep.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/utilities.cpython-311.pyc`
  - `src/assetutilities/common/__pycache__/validation.cpython-311.pyc`
  - ... 15 more omitted

### aceengineer-website
- Checkout inspected: `/mnt/local-analysis/aceengineer-website`
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/aceengineer-website-operator-map.md`: present
- `docs/registry/module-routing.yaml`: MISSING
- Confirmed broken canonical Markdown links: none
- Confirmed broken registry path references: none
- Legacy `.agent-os` / product-doc references observed in canonical surfaces:
  - `docs/README.md:32` — Historical product-doc and earlier deployment references are not active
  - `docs/maps/aceengineer-website-operator-map.md:29` — - Do not use retired product-doc paths or earlier deployment notes as active
- Trusted-path/root backup/cache/runtime noise detected:
  - `tests/__pycache__`
  - `tests/__pycache__/__init__.cpython-311.pyc`
  - `tests/__pycache__/__init__.cpython-312.pyc`
  - `tests/__pycache__/__init__.cpython-313.pyc`
  - `tests/docs/__pycache__`
  - `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__`
  - `tests/python/__pycache__/__init__.cpython-311.pyc`
  - `tests/python/__pycache__/__init__.cpython-312.pyc`
  - `tests/python/__pycache__/__init__.cpython-313.pyc`
  - `tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_clean.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_wrk146_positioning.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_wrk146_positioning.cpython-313.pyc`
  - `tests/repo_structure/__pycache__`
  - `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`

## 2026-04-22 Tier-1 Indexing Scorecard Assumptions

- Portfolio-level assumption still holds: tier-1 routing/index readiness remains partial, with multiple red repos and trusted-path noise.
- Repo-specific assumptions need revision where live evidence improved since 2026-04-22: `assetutilities` should remain **yellow**, not red, when all required canonical surfaces are present and the only confirmed issue is trusted-path cache/runtime noise.
- `aceengineer-website` remains **red** until a canonical machine-readable `docs/registry/module-routing.yaml` exists.
- `workspace-hub` remains **red** because the control-plane repo still lacks repo-local map/registry surfaces and contains active legacy `.agent-os/product` references in current docs.
- `digitalmodel` remains **red** because current canonical README routing contains confirmed broken local reference(s), despite strong source/test structure.

## Concise Next Actions

1. `workspace-hub`: create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace active `.agent-os/product/*` routing links in `docs/README.md` with current canonical surfaces; clean root/source cache noise.
2. `digitalmodel`: fix broken README target(s), especially any missing `specs/data-needs.yaml`-style references; remove committed or physically present trusted-path cache artifacts under `src/`.
3. `assetutilities`: clean cache/runtime artifacts from trusted `src/` paths; no status escalation unless canonical links/registry paths become broken.
4. `aceengineer-website`: add `docs/registry/module-routing.yaml`; clean cache artifacts under tests; keep README/docs/operator-map aligned.

## Machine-readable Snapshot

```json
{
  "workspace-hub": {
    "status": "red",
    "missing": [
      "docs/maps/workspace-hub-operator-map.md",
      "docs/registry/module-routing.yaml"
    ],
    "broken_markdown_count": 4,
    "broken_registry_count": 0,
    "noise_count": 40
  },
  "digitalmodel": {
    "status": "red",
    "missing": [],
    "broken_markdown_count": 1,
    "broken_registry_count": 0,
    "noise_count": 40
  },
  "assetutilities": {
    "status": "yellow",
    "missing": [],
    "broken_markdown_count": 0,
    "broken_registry_count": 0,
    "noise_count": 40
  },
  "aceengineer-website": {
    "status": "red",
    "missing": [
      "docs/registry/module-routing.yaml"
    ],
    "broken_markdown_count": 0,
    "broken_registry_count": 0,
    "noise_count": 22
  }
}
```
