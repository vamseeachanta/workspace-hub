# Tier-1 Indexing Freshness Audit — Latest

- **Generated:** 2026-05-22T03:34:26-05:00
- **Scope:** workspace-hub, digitalmodel, assetutilities, aceengineer-website
- **Mode:** scheduled local freshness audit; no cron jobs created or modified.
- **Material drift:** no material drift detected at the status level; timestamp and evidence refreshed.

## Status Summary

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **RED** | missing docs/maps/workspace-hub-operator-map.md<br>missing docs/registry/module-routing.yaml<br>broken docs/README.md:300 -> ../.agent-os/product/mission.md<br>broken docs/README.md:301 -> ../.agent-os/product/tech-stack.md<br>broken docs/README.md:302 -> ../.agent-os/product/roadmap.md<br>legacy ref docs/README.md:264<br>legacy ref docs/README.md:300<br>legacy ref docs/README.md:301<br>trusted-path noise (30 sample paths) | Create/refresh docs/maps/workspace-hub-operator-map.md and docs/registry/module-routing.yaml.<br>Retire active legacy .agent-os/product-doc references from canonical docs/README.md. |
| `digitalmodel` | **YELLOW** | broken README.md:73 -> specs/data-needs.yaml<br>stale docs/maps/digitalmodel-operator-map.md:9 -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md<br>trusted-path noise (30 sample paths) | Fix stale active README.md/specs reference and either restore/move the OrcaWave/OrcaFlex slice or mark it explicitly as workspace-level historical context.<br>Clean trusted-path cache/runtime/report noise; keep registry/operator map current. |
| `assetutilities` | **YELLOW** | trusted-path noise (30 sample paths) | Clean trusted-path runtime/cache/log/report noise; keep existing operator map and module routing registry current. |
| `aceengineer-website` | **RED** | missing docs/registry/module-routing.yaml<br>trusted-path noise (22 sample paths) | Add docs/registry/module-routing.yaml or explicitly document the canonical machine-readable registry alternative.<br>Clean minor trusted-path runtime/build noise. |

## 2026-04-22 Tier-1 Indexing Scorecard Assumptions

- Status-level assumptions still hold: `workspace-hub` RED, `digitalmodel` YELLOW, `assetutilities` YELLOW, `aceengineer-website` RED.
- The 2026-04-22 scorecard remains historical context, not current routing authority; live canonical surfaces are authoritative. Any old all-red or legacy product-doc framing needs revision where it conflicts with current live surfaces.

## workspace-hub

- **Status:** RED
- **Inspected path:** `/mnt/local-analysis/workspace-hub`
- **Present canonical surfaces:** `AGENTS.md`, `README.md`, `docs/README.md`
- **Missing canonical surfaces:** `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`

### Broken Markdown references
- `docs/README.md:300` -> `../.agent-os/product/mission.md` (missing Markdown target)
- `docs/README.md:301` -> `../.agent-os/product/tech-stack.md` (missing Markdown target)
- `docs/README.md:302` -> `../.agent-os/product/roadmap.md` (missing Markdown target)
- `docs/README.md:303` -> `../.agent-os/product/decisions.md` (missing Markdown target)

### Stale canonical-path references
- None detected.

### Active legacy routing references to retire
- `docs/README.md:264`: ├── .agent-os/              # Agent OS configuration
- `docs/README.md:300`: - [Mission & Vision](../.agent-os/product/mission.md)
- `docs/README.md:301`: - [Technical Stack](../.agent-os/product/tech-stack.md)
- `docs/README.md:302`: - [Development Roadmap](../.agent-os/product/roadmap.md)
- `docs/README.md:303`: - [Product Decisions](../.agent-os/product/decisions.md)

### Backup/cache/runtime noise in trusted paths
- `src/__pycache__`
- `src/ace/__pycache__`
- `src/ace/__pycache__/cli.cpython-311.pyc`
- `src/ace/__pycache__/cli.cpython-312.pyc`
- `src/ace/__pycache__/completion.cpython-311.pyc`
- `src/ace/__pycache__/completion.cpython-312.pyc`
- `src/ace/__pycache__/router.cpython-311.pyc`
- `src/ace/__pycache__/router.cpython-312.pyc`
- `src/ace/__pycache__/__init__.cpython-311.pyc`
- `src/ace/__pycache__/__init__.cpython-312.pyc`
- `src/config/__pycache__`
- `src/config/__pycache__/config_loader.cpython-311.pyc`
- `src/config/__pycache__/config_loader.cpython-312.pyc`
- `src/config/__pycache__/config_manager.cpython-311.pyc`
- `src/config/__pycache__/config_manager.cpython-312.pyc`
- `src/config/__pycache__/schema_validator.cpython-311.pyc`
- `src/config/__pycache__/schema_validator.cpython-312.pyc`
- `src/config/__pycache__/__init__.cpython-311.pyc`
- `src/config/__pycache__/__init__.cpython-312.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/models.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_allowable_length.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_fatigue_damage.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_natural_frequency.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_natural_frequency.cpython-313.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_onset_screening.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_viv_response.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/wave_velocity.cpython-311.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/wave_velocity.cpython-313.pyc`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__/weibull_current.cpython-311.pyc`

### Next actions
- Create/refresh docs/maps/workspace-hub-operator-map.md and docs/registry/module-routing.yaml.
- Retire active legacy .agent-os/product-doc references from canonical docs/README.md.
- Clean trusted-path runtime/cache/report noise that weakens root/index trust.

## digitalmodel

- **Status:** YELLOW
- **Inspected path:** `/mnt/local-analysis/digitalmodel`
- **Present canonical surfaces:** `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, `docs/registry/module-routing.yaml`
- **Missing canonical surfaces:** None detected

### Broken Markdown references
- `README.md:73` -> `specs/data-needs.yaml` (missing Markdown target)

### Stale canonical-path references
- `docs/maps/digitalmodel-operator-map.md:9` -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` (missing referenced canonical path)

### Active legacy routing references to retire
- None detected.

### Backup/cache/runtime noise in trusted paths
- `src/digitalmodel/__pycache__`
- `src/digitalmodel/citations/__pycache__`
- `src/digitalmodel/citations/__pycache__/registry.cpython-311.pyc`
- `src/digitalmodel/citations/__pycache__/registry.cpython-313.pyc`
- `src/digitalmodel/citations/__pycache__/resolver.cpython-311.pyc`
- `src/digitalmodel/citations/__pycache__/schema.cpython-311.pyc`
- `src/digitalmodel/citations/__pycache__/schema.cpython-313.pyc`
- `src/digitalmodel/citations/__pycache__/__init__.cpython-311.pyc`
- `src/digitalmodel/citations/__pycache__/__init__.cpython-313.pyc`
- `src/digitalmodel/hydrodynamics/__pycache__`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_dat_files.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_lis_files.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_post_process.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_pre_process.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_reader.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_router.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/aqwa_utilities.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/mes_files.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/aqwa/__pycache__/__init__.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/__pycache__`
- `src/digitalmodel/hydrodynamics/bemrosetta/converters/__pycache__`
- `src/digitalmodel/hydrodynamics/bemrosetta/converters/__pycache__/base.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/converters/__pycache__/to_orcaflex.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/converters/__pycache__/__init__.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/core/__pycache__`
- `src/digitalmodel/hydrodynamics/bemrosetta/core/__pycache__/exceptions.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/core/__pycache__/interfaces.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/core/__pycache__/runner.cpython-311.pyc`
- `src/digitalmodel/hydrodynamics/bemrosetta/core/__pycache__/__init__.cpython-311.pyc`

### Next actions
- Fix stale active README.md/specs reference and either restore/move the OrcaWave/OrcaFlex slice or mark it explicitly as workspace-level historical context.
- Clean trusted-path cache/runtime/report noise; keep registry/operator map current.

## assetutilities

- **Status:** YELLOW
- **Inspected path:** `/mnt/local-analysis/assetutilities`
- **Present canonical surfaces:** `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`
- **Missing canonical surfaces:** None detected

### Broken Markdown references
- None detected.

### Stale canonical-path references
- None detected.

### Active legacy routing references to retire
- None detected.

### Backup/cache/runtime noise in trusted paths
- `src/assetutilities/__pycache__`
- `src/assetutilities/common/__pycache__`
- `src/assetutilities/common/download_data/__pycache__`
- `src/assetutilities/common/download_data/__pycache__/dwnld_from_zipurl.cpython-311.pyc`
- `src/assetutilities/common/readers/__pycache__`
- `src/assetutilities/common/readers/__pycache__/csv_reader.cpython-311.pyc`
- `src/assetutilities/common/readers/__pycache__/data_getter.cpython-311.pyc`
- `src/assetutilities/common/readers/__pycache__/data_reader.cpython-311.pyc`
- `src/assetutilities/common/readers/__pycache__/excel_reader.cpython-311.pyc`
- `src/assetutilities/common/readers/__pycache__/__init__.cpython-311.pyc`
- `src/assetutilities/common/visualization/__pycache__`
- `src/assetutilities/common/visualization/__pycache__/visualization_common.cpython-311.pyc`
- `src/assetutilities/common/visualization/__pycache__/visualization_polar.cpython-311.pyc`
- `src/assetutilities/common/visualization/__pycache__/visualization_templates_matplotlib.cpython-311.pyc`
- `src/assetutilities/common/visualization/__pycache__/visualization_xy.cpython-311.pyc`
- `src/assetutilities/common/visualization/__pycache__/__init__.cpython-311.pyc`
- `src/assetutilities/common/webscraping/__pycache__`
- `src/assetutilities/common/webscraping/__pycache__/bs4_router.cpython-311.pyc`
- `src/assetutilities/common/webscraping/__pycache__/loopnet_scraper.cpython-311.pyc`
- `src/assetutilities/common/webscraping/__pycache__/scrapper_scrapy.cpython-311.pyc`
- `src/assetutilities/common/webscraping/__pycache__/web_scraping.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/ApplicationManager.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/attribute_dict.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/data.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/data_management.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/datetime_utils.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/file_edit.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/file_edit_concatenate.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/file_edit_split.cpython-311.pyc`
- `src/assetutilities/common/__pycache__/file_management.cpython-311.pyc`

### Next actions
- Clean trusted-path runtime/cache/log/report noise; keep existing operator map and module routing registry current.

## aceengineer-website

- **Status:** RED
- **Inspected path:** `/mnt/local-analysis/aceengineer-website`
- **Present canonical surfaces:** `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/aceengineer-website-operator-map.md`
- **Missing canonical surfaces:** `docs/registry/module-routing.yaml`

### Broken Markdown references
- None detected.

### Stale canonical-path references
- None detected.

### Active legacy routing references to retire
- None detected.

### Backup/cache/runtime noise in trusted paths
- `tests/__pycache__`
- `tests/docs/__pycache__`
- `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
- `tests/python/__pycache__`
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
- `tests/python/__pycache__/__init__.cpython-311.pyc`
- `tests/python/__pycache__/__init__.cpython-312.pyc`
- `tests/python/__pycache__/__init__.cpython-313.pyc`
- `tests/repo_structure/__pycache__`
- `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`
- `tests/__pycache__/__init__.cpython-311.pyc`
- `tests/__pycache__/__init__.cpython-312.pyc`
- `tests/__pycache__/__init__.cpython-313.pyc`

### Next actions
- Add docs/registry/module-routing.yaml or explicitly document the canonical machine-readable registry alternative.
- Clean minor trusted-path runtime/build noise.

## Audit Notes

- Used current canonical routing surfaces only: `AGENTS.md`, `README.md`, `docs/README.md`, repo-local `docs/maps/<repo>-operator-map.md`, and `docs/registry/module-routing.yaml`.
- Legacy `.agent-os` / product-doc references were not used as routing authority. Explicit warnings that say not to use retired product-doc paths were not counted as active stale references.
- Markdown/backtick path checks filter external URLs, anchors, wildcard patterns, and placeholders.
- No new cron jobs were scheduled.
