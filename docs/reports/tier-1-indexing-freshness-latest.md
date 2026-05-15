# Tier-1 Indexing Freshness Report

Generated: 2026-05-15T03:30:57-05:00
Working directory: `/mnt/local-analysis/workspace-hub`
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Mode: local scheduled freshness audit only; no cron jobs were created or modified.

## Overall Status

Portfolio status: **RED**

No material drift detected at the status level versus the 2026-05-14 freshness baseline. The portfolio remains red because `workspace-hub` and `aceengineer-website` are missing required canonical routing surfaces, and current trusted paths still contain runtime/cache/report noise.

This refresh also corrects stale content in the previous `tier-1-indexing-freshness-latest.md`: `assetutilities` is not carrying 6 confirmed broken active canonical links after false-positive filtering, and `aceengineer-website` remains **RED** because `docs/registry/module-routing.yaml` is still missing.

## 2026-04-22 Scorecard Assumption Check

The 2026-04-22 tier-1 indexing scorecard assumptions **partially still hold and need detail-level revision**:

- Still holds: the portfolio is only partially ready for reliable code placement and canonical retrieval.
- Still holds: `workspace-hub` is the strongest control-plane repo but has weak root/index hygiene.
- Still holds: `digitalmodel` is the strongest engineering source/test structure.
- Needs revision: several surfaces missing on 2026-04-22 now exist (`digitalmodel/docs/README.md`, repo-wide `digitalmodel` operator map, `assetutilities/docs/README.md`, `assetutilities` operator map/registry, `aceengineer-website/docs/README.md`, and `aceengineer-website` operator map).
- Still holds until fixed: machine-readable routing is not complete across all tier-1 repos because `workspace-hub` and `aceengineer-website` still lack `docs/registry/module-routing.yaml`.

## Per-Repo Status Summary

| Repo | Status | Current reason |
| --- | --- | --- |
| `workspace-hub` | **RED** | Missing required operator map and registry; stale legacy references remain in `docs/README.md`; root/index noise remains high. |
| `digitalmodel` | **YELLOW** | Required canonical surfaces exist, but `README.md` has a missing `specs/data-needs.yaml` link and the operator map still points to a workspace-level historical slice as if repo-local. |
| `assetutilities` | **YELLOW** | Required canonical surfaces exist and no confirmed broken active canonical Markdown links were found after false-positive filtering; trusted source/test paths still contain runtime/cache/log noise. |
| `aceengineer-website` | **RED** | Required docs/operator surfaces exist, but the required machine-readable registry is still missing. |

## Findings

### workspace-hub — RED

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**
- Existing map under `docs/maps/`: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` only; useful as a domain slice, not a workspace-hub repo-wide operator map.

Exact broken or stale references:

- `docs/README.md:300` -> `../.agent-os/product/mission.md` — stale legacy reference; target missing.
- `docs/README.md:301` -> `../.agent-os/product/tech-stack.md` — stale legacy reference; target missing.
- `docs/README.md:302` -> `../.agent-os/product/roadmap.md` — stale legacy reference; target missing.
- `docs/README.md:303` -> `../.agent-os/product/decisions.md` — stale legacy reference; target missing.

Noise weakening routing trust:

- Root/runtime/cache/build noise still includes: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`, `.cache`, `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.tmp-inspect-2348`, `.uv-cache`, `.venv`, `.venv-manim`, `.venv-test`, `dist`, `logs`, `node_modules`, `reports`, `tmp`.
- Trusted-path runtime/report noise includes `src/workspace_hub/reports` plus many `__pycache__` directories under `src/` and `tests/`.

Concise next actions:

1. Create `docs/maps/workspace-hub-operator-map.md` as the repo-wide operator map.
2. Create `docs/registry/module-routing.yaml` for machine-readable routing.
3. Remove or rewrite the stale legacy links in `docs/README.md` using current canonical routing surfaces only.
4. Clean or quarantine root/runtime/cache/report noise from trusted source and index paths.

### digitalmodel — YELLOW

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:

- `README.md:73` -> `specs/data-needs.yaml` — missing target.
- `docs/maps/digitalmodel-operator-map.md:9` references `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; the matching historical slice exists at workspace level (`/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`), not repo-local under `/mnt/local-analysis/workspace-hub/digitalmodel/docs/maps/`.

Noise weakening routing trust:

- Root/runtime/build noise includes `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`, `dist`, `logs`, `reports`.
- Source-path log directories remain under:
  - `src/digitalmodel/hydrodynamics/rao_analysis/legacy/logs`
  - `src/digitalmodel/structural/pipe_capacity/custom/API_STD_2RD/BurstPressure/logs`
- Many `__pycache__` directories remain under `src/` and `tests/`.

Concise next actions:

1. Restore, relocate, or remove the `README.md` reference to `specs/data-needs.yaml`.
2. Clarify the historical OrcaWave/OrcaFlex map reference so it is explicitly workspace-level, or add a repo-local forwarding map.
3. Remove source-path log/cache noise from trusted package paths.

### assetutilities — YELLOW

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or missing surfaces:

- No required canonical surface is missing.
- No confirmed broken active canonical Markdown links were found after resolving `docs/...` references from the repo root and filtering pattern/example false positives.

Noise weakening routing trust:

- Root/runtime/build noise includes `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`, `dist`, `logs`, `reports`.
- Trusted source/test paths still contain runtime/cache/log noise, including:
  - `src/assetutilities/tests/test_data/visualization/logs`
  - `tests/modules/csv_utilities/logs`
  - `tests/modules/data_exploration/logs`
  - `tests/modules/download_data/logs`
  - `tests/modules/excel_utilities/logs`
  - `tests/modules/file_edit/logs`
  - `tests/modules/file_management/logs`
  - `tests/modules/tests_wip/test_data/visualization/logs`
  - `tests/modules/visualization/logs`
  - `tests/modules/web_scraping/logs`
  - `tests/modules/yml_utilities/legacy/logs`
  - `tests/modules/yml_utilities/logs`
  - `tests/modules/yml_utilities/yaml_divide/logs`
  - `tests/modules/yml_utilities/yaml_to_plot/logs`
  - `tests/modules/zip_utilities/logs`
- Many `__pycache__` directories remain under `src/` and `tests/`.

Concise next actions:

1. Clean runtime/cache/log artifacts from trusted source/test paths.
2. Keep `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, and `docs/registry/module-routing.yaml` aligned as the canonical routing trio.
3. Do not reintroduce stale broken-link counts unless revalidated with root-relative `docs/...` handling.

### aceengineer-website — RED

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or stale references:

- No confirmed broken active canonical Markdown links found in the inspected canonical surfaces.

Noise weakening routing trust:

- Root/runtime/build noise includes `.coverage`, `.pytest_cache`, `.venv`, `dist`, `logs`, `node_modules`, `reports`.
- Test cache noise remains under `tests/__pycache__`, `tests/docs/__pycache__`, `tests/python/__pycache__`, and `tests/repo_structure/__pycache__`.

Concise next actions:

1. Create `docs/registry/module-routing.yaml` covering pages, content, demos, calculators, scripts, tests, and deployment/review surfaces.
2. Keep the registry aligned with `docs/maps/aceengineer-website-operator-map.md` and `docs/README.md`.
3. Clean runtime/build/cache artifacts from root and trusted test paths.

## Current Broken/Missing Surface Inventory

Required missing surfaces:

- `workspace-hub/docs/maps/workspace-hub-operator-map.md`
- `workspace-hub/docs/registry/module-routing.yaml`
- `aceengineer-website/docs/registry/module-routing.yaml`

Confirmed broken/stale active references:

- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` -> repo-local `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` assumption is stale; matching map is workspace-level.

## Next Actions, Ranked

1. **workspace-hub:** add the missing repo-wide operator map and machine-readable registry; remove stale legacy links from `docs/README.md`.
2. **aceengineer-website:** add `docs/registry/module-routing.yaml`; keep repo status red until this exists.
3. **digitalmodel:** fix the missing `specs/data-needs.yaml` reference and clarify the workspace-level historical map reference.
4. **assetutilities:** clean runtime/cache/log noise from trusted source/test paths; do not chase stale broken-link false positives.
5. **Portfolio:** continue daily local freshness refreshes; no new cron jobs should be scheduled by this audit.

## Verification Notes

- Report refreshed at `docs/reports/tier-1-indexing-freshness-latest.md`.
- Current canonical routing surfaces only were used: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/*operator-map*.md`, and `docs/registry/module-routing.yaml` where present.
- Legacy references were reported only as stale residue, not as recommended routing patterns.
