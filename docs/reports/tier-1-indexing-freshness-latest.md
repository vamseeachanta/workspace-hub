# Tier-1 Indexing Freshness Audit — Latest

- **Generated:** 2026-06-07T03:33:01-05:00
- **Scope:** `/mnt/local-analysis/workspace-hub`; sibling fallback checkouts used for tier-1 repos absent under the workspace root
- **Repos:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
- **Cron changes:** none scheduled

## Summary

No material drift detected at the status level; timestamp refreshed and current evidence revalidated. The RED/YELLOW baseline from the latest prior audits still holds.

| Repo | Status | Checkout used | Exact broken or missing surfaces | Concise next action |
|---|---:|---|---|---|
| `workspace-hub` | **red** | requested workspace root: `/mnt/local-analysis/workspace-hub` | Missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; active broken legacy product-doc links in `docs/README.md:300-303`; root/index/runtime noise present | Create/curate repo-local operator map and module-routing registry; remove active legacy product-doc links; clean trusted-path/root runtime noise |
| `digitalmodel` | **red** | sibling fallback checkout: `/mnt/local-analysis/digitalmodel` | Required canonical surfaces present; broken `README.md:73 -> specs/data-needs.yaml`; source/docs cache/runtime noise present | Fix the broken README routing link; clean cache/runtime noise from trusted paths |
| `assetutilities` | **yellow** | sibling fallback checkout: `/mnt/local-analysis/assetutilities` | Required canonical surfaces present; no confirmed broken canonical links; trusted-path cache/runtime/reportgen noise present | Clean Python cache/runtime noise from trusted paths; keep canonical links stable |
| `aceengineer-website` | **red** | sibling fallback checkout: `/mnt/local-analysis/aceengineer-website` | Missing `docs/registry/module-routing.yaml`; no confirmed broken canonical links; test/script cache noise present | Add machine-readable module-routing registry; clean test/script cache noise |

## 2026-04-22 scorecard assumption verdict

The 2026-04-22 tier-1 indexing scorecard assumptions still hold at the portfolio/status level and still need the same repo-specific revisions already identified:

- `workspace-hub` remains the richest control plane, but routing trust is weakened by missing repo-local operator/registry surfaces, active legacy product-doc links, and root/index/runtime noise.
- `digitalmodel` remains structurally strong for source/test engineering, but it remains red until the active broken README routing reference is fixed and trusted-path cache noise is cleaned.
- `assetutilities` remains yellow rather than red: primary canonical routing surfaces are present and scanned links are clean, but hygiene noise remains in trusted paths.
- `aceengineer-website` remains red until it has a canonical machine-readable `docs/registry/module-routing.yaml`.

## Per-repo evidence

### workspace-hub — red

- **Path:** `/mnt/local-analysis/workspace-hub` (requested workspace root)
- **Canonical surfaces inspected:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/workspace-hub-operator-map.md`: **MISSING**
  - `docs/registry/module-routing.yaml`: **MISSING**
- **Confirmed broken/stale references in scanned canonical surfaces:**
  - `docs/README.md:300` -> `../.agent-os/product/mission.md`
  - `docs/README.md:300` -> `.agent-os/product active reference`
  - `docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
  - `docs/README.md:301` -> `.agent-os/product active reference`
  - `docs/README.md:302` -> `../.agent-os/product/roadmap.md`
  - `docs/README.md:302` -> `.agent-os/product active reference`
  - `docs/README.md:303` -> `../.agent-os/product/decisions.md`
  - `docs/README.md:303` -> `.agent-os/product active reference`
- **Backup/cache/runtime/report noise in trusted paths:** 1468 items detected, primarily docs plan/session logs and Python `__pycache__` / `.pyc` under `scripts/`.
- **Top-level root noise observed:** `.cache/`, `.mypy_cache/`, `claude_smoke.log`, `.pytest_cache/`, `.ruff_cache/`, `logs/`, `output/`.
- **Next action:** create/curate `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace active legacy product-doc references with current canonical routing surfaces; clean trusted-path and root runtime noise.

### digitalmodel — red

- **Path:** `/mnt/local-analysis/digitalmodel` (sibling fallback checkout)
- **Canonical surfaces inspected:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/digitalmodel-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Confirmed broken/stale references in scanned canonical surfaces:**
  - `README.md:73` -> `specs/data-needs.yaml`
- **Backup/cache/runtime/report noise in trusted paths:** 1208 items detected, primarily docs/script/source `__pycache__` / `.pyc` artifacts and report-related source paths such as `src/digitalmodel/ansys/report_generator.py` and `src/digitalmodel/asset_integrity/assessment/ffs_report.py` flagged by the broad noise scanner.
- **Next action:** fix or remove the broken README link to `specs/data-needs.yaml`; clean generated/cache artifacts from trusted docs/source/script paths.

### assetutilities — yellow

- **Path:** `/mnt/local-analysis/assetutilities` (sibling fallback checkout)
- **Canonical surfaces inspected:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/assetutilities-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Confirmed broken/stale references in scanned canonical surfaces:** none confirmed in scanned canonical Markdown surfaces.
- **Backup/cache/runtime/report noise in trusted paths:** 79 items detected, primarily `src/assetutilities/**/__pycache__/`, `.pyc` files, and `src/assetutilities/common/reportgen/*` / `src/assetutilities/base_configs/modules/reportgen/reportgen.yml` flagged by the broad report-noise heuristic.
- **Next action:** clean Python cache/runtime noise from trusted paths; keep current canonical routing surfaces stable.

### aceengineer-website — red

- **Path:** `/mnt/local-analysis/aceengineer-website` (sibling fallback checkout)
- **Canonical surfaces inspected:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/aceengineer-website-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: **MISSING**
- **Confirmed broken/stale references in scanned canonical surfaces:** none confirmed in scanned canonical Markdown surfaces.
- **Backup/cache/runtime/report noise in trusted paths:** 33 items detected, primarily `scripts/**/__pycache__/`, `tests/**/__pycache__/`, and `.pyc` artifacts.
- **Next action:** add `docs/registry/module-routing.yaml`; clean test/script cache noise.

## Sibling fallback note

`digitalmodel`, `assetutilities`, and `aceengineer-website` were inspected from sibling fallback checkouts under `/mnt/local-analysis/<repo>` because nested checkouts under `/mnt/local-analysis/workspace-hub/<repo>` were absent. This is not itself counted as material drift, but it remains important audit context for interpreting local report paths.

## Guardrails followed

- Used current canonical routing surfaces only: `AGENTS.md`, `README.md`, `docs/README.md`, repo-local `docs/maps/*-operator-map.md`, and `docs/registry/module-routing.yaml` where applicable.
- Did **not** use or recommend legacy `.agent-os` reference patterns; active legacy product-doc references were reported as stale drift.
- Did **not** schedule any new cron jobs.
