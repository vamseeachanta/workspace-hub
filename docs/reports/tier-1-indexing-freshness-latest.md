# Tier-1 Indexing Freshness Report

Generated: 2026-05-14T03:32:16-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working tree inspected: `/mnt/local-analysis/workspace-hub`
Mode: scheduled freshness audit; no new cron jobs scheduled.

## Overall Status

Portfolio status: **red**

Status-level result: **no material drift detected at the status level** versus the 2026-05-12 tier-1 freshness baseline. The portfolio remains red because at least one tier-1 repo is missing required canonical routing/index surfaces or has active stale references in trusted routing docs.

This refresh also corrects stale content in the previously generated latest report: current false-positive-filtered evidence does **not** confirm the earlier `assetutilities` broken-link count, and `aceengineer-website` remains **red** because its machine-readable registry is still missing.

## Canonical Surfaces Checked

For each repo, this audit inspected current canonical routing/index surfaces only:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md` when applicable
- `docs/registry/module-routing.yaml` when applicable

Legacy `.agent-os` product-doc patterns were treated only as stale legacy residue when encountered. They are not recommended or used as routing surfaces.

## Repo Status Summary

| Repo | Status | Summary |
| --- | --- | --- |
| `workspace-hub` | **red** | Required operator map and registry are still missing; `docs/README.md` still has stale legacy `.agent-os/product/*` links; root/index trust remains weakened by runtime/build/cache noise and tracked root clutter. |
| `digitalmodel` | **yellow** | Required canonical surfaces exist, but `README.md` still links to missing `specs/data-needs.yaml`; repo-wide operator map still references a missing repo-local narrow-slice map whose matching file exists only at workspace level; trusted paths contain runtime/log noise. |
| `assetutilities` | **yellow** | Required canonical surfaces exist and no broken active Markdown links were confirmed after false-positive filtering; trusted paths still contain runtime/cache/log/report noise. |
| `aceengineer-website` | **red** | Required docs/operator surfaces exist, but `docs/registry/module-routing.yaml` is still missing; root contains runtime/build/cache noise. |

## Per-Repo Findings

### workspace-hub — red

Canonical surfaces:

- Present: `AGENTS.md`, `README.md`, `docs/README.md`
- Missing: `docs/maps/workspace-hub-operator-map.md`
- Missing: `docs/registry/module-routing.yaml`

Exact stale or broken references:

- `docs/README.md:300` -> `../.agent-os/product/mission.md` resolves to missing `/mnt/local-analysis/workspace-hub/.agent-os/product/mission.md`
- `docs/README.md:301` -> `../.agent-os/product/tech-stack.md` resolves to missing `/mnt/local-analysis/workspace-hub/.agent-os/product/tech-stack.md`
- `docs/README.md:302` -> `../.agent-os/product/roadmap.md` resolves to missing `/mnt/local-analysis/workspace-hub/.agent-os/product/roadmap.md`
- `docs/README.md:303` -> `../.agent-os/product/decisions.md` resolves to missing `/mnt/local-analysis/workspace-hub/.agent-os/product/decisions.md`
- `docs/README.md:264` still contains `.agent-os/` tree residue.

Noise weakening routing trust:

- Root runtime/build/cache directories or files currently present: `.cache/`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `logs/`, `node_modules/`, `reports/`, `tmp/`, `.tmp-inspect-2348/`, `.uv-cache/`, `.venv/`, `.venv-manim/`, `.venv-test/`
- Tracked root clutter still includes: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`

Concise next actions:

1. Add or restore `docs/maps/workspace-hub-operator-map.md` as the curated repo operator map.
2. Add or restore `docs/registry/module-routing.yaml` as the machine-readable registry.
3. Remove stale legacy `.agent-os/product/*` links and `.agent-os/` tree residue from `docs/README.md`, replacing them with current canonical routing surfaces.
4. Separate or ignore runtime/build/cache outputs so trusted root/index paths stay low-noise.

### digitalmodel — yellow

Canonical surfaces:

- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, `docs/registry/module-routing.yaml`
- Missing required surfaces: none confirmed.

Exact stale or broken references:

- `README.md:73` -> `specs/data-needs.yaml` resolves to missing `/mnt/local-analysis/workspace-hub/digitalmodel/specs/data-needs.yaml`
- `docs/maps/digitalmodel-operator-map.md:9` references repo-local `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`, but `/mnt/local-analysis/workspace-hub/digitalmodel/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` is missing. Matching context exists at workspace level: `/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`.

Noise weakening routing trust:

- Root runtime/build/cache directories or files currently present: `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `logs/`, `reports/`, `.venv/`
- Trusted-path log directories detected under source paths:
  - `src/digitalmodel/hydrodynamics/rao_analysis/legacy/logs/`
  - `src/digitalmodel/structural/pipe_capacity/custom/API_STD_2RD/BurstPressure/logs/`

Concise next actions:

1. Either restore `specs/data-needs.yaml` or update `README.md` to point to the current canonical data-needs surface.
2. Fix the operator-map reference so the narrow OrcaWave/OrcaFlex context is either repo-local or explicitly workspace-level.
3. Move or ignore runtime/log outputs from trusted source paths.

### assetutilities — yellow

Canonical surfaces:

- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`
- Missing required surfaces: none confirmed.

Exact stale or broken references:

- None confirmed in the checked canonical routing surfaces after false-positive filtering.

Noise weakening routing trust:

- Root runtime/build/cache directories or files currently present: `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `logs/`, `reports/`, `.venv/`
- Trusted-path log directory detected under source/test-adjacent package paths:
  - `src/assetutilities/tests/test_data/visualization/logs/`

Concise next actions:

1. Keep current canonical routing surfaces as the authority.
2. Move or ignore runtime/log/report/cache outputs so source/test-adjacent paths remain retrieval-safe.
3. Continue using false-positive filters for wildcard/example path references before reporting broken links.

### aceengineer-website — red

Canonical surfaces:

- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/aceengineer-website-operator-map.md`
- Missing: `docs/registry/module-routing.yaml`

Exact stale or broken references:

- None confirmed in the checked canonical routing surfaces after false-positive filtering.

Noise weakening routing trust:

- Root runtime/build/cache directories or files currently present: `.coverage`, `.pytest_cache/`, `dist/`, `logs/`, `node_modules/`, `reports/`, `.venv/`

Concise next actions:

1. Add `docs/registry/module-routing.yaml` for page/content/calculator/script/test routing.
2. Keep `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` aligned with that registry.
3. Move or ignore runtime/build/cache outputs so the static-site root remains retrieval-safe.

## 2026-04-22 Scorecard Assumption Check

The 2026-04-22 tier-1 indexing scorecard assumptions still hold **directionally** but need **current-state detail revision**:

- Still holds: the tier-1 portfolio is only partially ready for reliable code placement and retrieval.
- Still holds: `workspace-hub` is the richest control-plane repo, but index/root hygiene weakens routing trust.
- Still holds with revision: `digitalmodel` remains structurally strong, and now has the main required repo-wide routing surfaces; its remaining issues are stale references and runtime/log noise rather than missing canonical surfaces.
- Needs revision: `assetutilities` is no longer missing the previously noted canonical `docs/README.md`, operator map, or registry surfaces in this checkout; the current material issue is hygiene/noise, not missing routing surfaces.
- Still holds with revision: `aceengineer-website` has improved docs/operator surfaces, but durable routing remains incomplete until `docs/registry/module-routing.yaml` exists.

## Recommended Next Actions

1. Treat `workspace-hub` and `aceengineer-website` as the red blockers for portfolio green status.
2. Fix stale references in `workspace-hub/docs/README.md` and `digitalmodel` routing docs before adding more index layers.
3. Add the missing machine-readable registries/operator map where absent:
   - `workspace-hub/docs/maps/workspace-hub-operator-map.md`
   - `workspace-hub/docs/registry/module-routing.yaml`
   - `aceengineer-website/docs/registry/module-routing.yaml`
4. Clean runtime/build/cache/log noise from trusted source/index paths across all four repos.
5. Keep scheduled freshness auditing local-only unless explicitly asked to change automation.

## Verification Notes

- Report refreshed locally at `docs/reports/tier-1-indexing-freshness-latest.md`.
- No new cron jobs were scheduled.
- This report intentionally avoids legacy `.agent-os` reference patterns as recommended routing surfaces.
