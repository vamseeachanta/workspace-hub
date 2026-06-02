# Tier-1 Indexing Freshness Report

Generated: 2026-06-02T03:31:15-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Requested workspace checkout: `/mnt/local-analysis/workspace-hub`
Repo path resolution: use nested repos under workspace-hub when present; sibling checkout fallback used for `digitalmodel`, `assetutilities`, and `aceengineer-website` because nested checkouts are absent.
Canonical surfaces only: `AGENTS.md`, `README.md`, `docs/README.md`, repo-local `docs/maps/<repo>-operator-map.md`, and `docs/registry/module-routing.yaml` where applicable. This report intentionally does not use or recommend legacy `.agent-os` routing patterns.

## Overall Status

Portfolio status: **red**

Material drift: **yes**. `digitalmodel` now fails the freshness gate because its top-level README actively links to missing `specs/data-needs.yaml`. `assetutilities` remains yellow for source-path cache noise only. `workspace-hub` and `aceengineer-website` remain red.

## Repo Status Summary

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | red | Missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; active legacy `.agent-os` references and broken links in `docs/README.md:264,300-303`; runtime/cache noise under trusted `src/` and `tests/` paths. | Create repo-local operator map and machine-readable registry; replace active legacy `.agent-os` doc links with current canonical routing surfaces; clean cache/runtime noise from trusted source/test paths. |
| `digitalmodel` | red | No required surface missing; registry path references validate; broken active README link: `README.md:73 -> specs/data-needs.yaml`; runtime/cache noise under trusted `src/` paths. | Either restore `specs/data-needs.yaml` or remove/retarget the README link; clear cache noise from source paths; keep registry and operator map as current canonical surfaces. |
| `assetutilities` | yellow | No required surface missing; registry path references validate; no active legacy `.agent-os` references detected in canonical surfaces; runtime/cache noise under trusted `src/` paths. | Clean source-path `__pycache__` noise; keep existing operator map and registry current. |
| `aceengineer-website` | red | Missing `docs/registry/module-routing.yaml`; runtime/cache noise under trusted `tests/` paths. | Add machine-readable module/content routing registry; clean test cache noise. |

## Per-Repo Evidence

### `workspace-hub` — red

Resolved path: `/mnt/local-analysis/workspace-hub`

Canonical surface inspection:
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/workspace-hub-operator-map.md`: **missing**
- `docs/registry/module-routing.yaml`: **missing**

Confirmed broken/stale references:
- `docs/README.md:264` mentions `.agent-os/` as Agent OS configuration in the documented structure.
- `docs/README.md:300 -> ../.agent-os/product/mission.md` is an active broken legacy product-doc link.
- `docs/README.md:301 -> ../.agent-os/product/tech-stack.md` is an active broken legacy product-doc link.
- `docs/README.md:302 -> ../.agent-os/product/roadmap.md` is an active broken legacy product-doc link.
- `docs/README.md:303 -> ../.agent-os/product/decisions.md` is an active broken legacy product-doc link.

Noise affecting routing trust:
- Runtime/cache directories were detected under trusted paths, including `src/__pycache__`, package-level `src/**/__pycache__`, and many `tests/**/__pycache__` directories.
- Current workspace root/index trust is also weakened by a very large dirty/untracked state from generated provider/memory/log/report artifacts; this is not part of the tier-1 surface contract, but it makes local routing audits noisier.

Next actions:
1. Add a repo-local operator map at `docs/maps/workspace-hub-operator-map.md`.
2. Add a machine-readable routing registry at `docs/registry/module-routing.yaml`.
3. Replace active legacy `.agent-os` links in `docs/README.md` with current canonical routing surfaces.
4. Remove cache/runtime noise from trusted source/test paths and ensure it remains ignored.

### `digitalmodel` — red

Resolved path: `/mnt/local-analysis/digitalmodel` (sibling fallback)

Canonical surface inspection:
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/digitalmodel-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present

Registry check:
- `docs/registry/module-routing.yaml` path references resolved successfully for checked `entry_point`, `owner_wiki`, `key_tests`, `canonical_operator_map`, and `operator_map_row` targets.

Confirmed broken/stale references:
- `README.md:73 -> specs/data-needs.yaml` is an active broken link. No `data-needs.yaml` file was found under `/mnt/local-analysis/digitalmodel`.

Noise affecting routing trust:
- Runtime/cache directories were detected under trusted source paths, including `src/digitalmodel/__pycache__` and many package-level `src/digitalmodel/**/__pycache__` directories.

Next actions:
1. Decide whether `specs/data-needs.yaml` is still canonical. If yes, restore it. If no, remove or retarget `README.md:73`.
2. Clean `__pycache__` directories from trusted source paths.
3. Preserve current operator map and registry as canonical; they no longer appear missing.

### `assetutilities` — yellow

Resolved path: `/mnt/local-analysis/assetutilities` (sibling fallback)

Canonical surface inspection:
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/assetutilities-operator-map.md`: present
- `docs/registry/module-routing.yaml`: present

Registry check:
- `docs/registry/module-routing.yaml` path references resolved successfully for checked routing targets.

Confirmed broken/stale references:
- No active broken Markdown links or legacy `.agent-os` references detected in the inspected canonical surfaces.

Noise affecting routing trust:
- Runtime/cache directories were detected under trusted source paths, including `src/assetutilities/__pycache__` and package-level `src/assetutilities/**/__pycache__` directories.

Next actions:
1. Remove `__pycache__` directories from source paths.
2. Keep the operator map and registry synchronized as modules move or mature.

### `aceengineer-website` — red

Resolved path: `/mnt/local-analysis/aceengineer-website` (sibling fallback)

Canonical surface inspection:
- `AGENTS.md`: present
- `README.md`: present
- `docs/README.md`: present
- `docs/maps/aceengineer-website-operator-map.md`: present
- `docs/registry/module-routing.yaml`: **missing**

Confirmed broken/stale references:
- No active broken Markdown links or legacy `.agent-os` references detected in the inspected canonical surfaces.

Noise affecting routing trust:
- Runtime/cache directories were detected under trusted test paths, including `tests/__pycache__`, `tests/docs/__pycache__`, `tests/python/__pycache__`, and `tests/repo_structure/__pycache__`.

Next actions:
1. Add `docs/registry/module-routing.yaml` for machine-readable website/content routing.
2. Clean test-path cache noise.

## 2026-04-22 Tier-1 Indexing Scorecard Assumption Check

Status: **top-level assumptions still hold, but repo-specific assumptions need revision.**

- Still holds: tier-1 routing/index surfaces are not uniformly trustworthy; future issue work still needs repo-local operator maps, docs entry points, and machine-readable registries to retrieve canonical source/tests/docs paths quickly.
- Needs revision: the older assumption that `digitalmodel` and `assetutilities` lack primary canonical surfaces is stale. Both now have `AGENTS.md`, `README.md`, `docs/README.md`, repo-local operator maps, and registries.
- Needs revision: `digitalmodel` should be classified red today for an active broken README reference, not for missing routing surfaces.
- Still holds: `workspace-hub` remains a control-plane repo with root/index noise and missing local operator map/registry surfaces.
- Still holds with narrower scope: `aceengineer-website` remains red, specifically because its machine-readable routing registry is still missing, not because all surfaces are absent.

## Cron / Scheduling

No new cron jobs were scheduled. This run only refreshed the local report requested at `docs/reports/tier-1-indexing-freshness-latest.md`.
