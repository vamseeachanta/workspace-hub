# Tier-1 Indexing Freshness Report

Generated: 2026-05-11T03:31:33-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working directory: `/mnt/local-analysis/workspace-hub`
Source baseline: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

No new cron jobs were scheduled. This refresh is local-only.

## Executive Summary

Portfolio status: **red**

No status-level material drift detected relative to the latest 2026-05-10 evidence baseline: `workspace-hub` and `aceengineer-website` remain red; `digitalmodel` and `assetutilities` remain yellow. The report timestamp was refreshed and the current evidence was re-scanned.

Primary blockers:
- `workspace-hub` is missing required canonical routing surfaces and still has active stale legacy `.agent-os` links in `docs/README.md`.
- `aceengineer-website` is still missing the canonical machine-readable registry at `docs/registry/module-routing.yaml`.
- `digitalmodel` has one broken active README reference and one stale repo-local map reference.
- `assetutilities` canonical routing links are currently clean, but trusted source/test paths and repo root still carry cache/runtime noise.

## Per-Repo Status

| Repo | Status | Summary |
|---|---|---|
| `workspace-hub` | **red** | Missing operator map and registry; active stale legacy links; root/index noise weakens trust. |
| `digitalmodel` | **yellow** | Required surfaces exist, but one README link and one repo-local map reference are stale; cache/runtime noise remains. |
| `assetutilities` | **yellow** | Required surfaces exist and no broken active Markdown links were confirmed; cache/runtime noise remains in trusted paths. |
| `aceengineer-website` | **red** | Required docs/operator surfaces exist, but canonical registry is still missing; cache/runtime noise remains. |

## Findings

### `workspace-hub` — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or stale surfaces:
- Missing required surface: `docs/maps/workspace-hub-operator-map.md`
- Missing required surface: `docs/registry/module-routing.yaml`
- Broken/stale legacy links in `docs/README.md`:
  - line 299: `../.agent-os/product/mission.md`
  - line 300: `../.agent-os/product/tech-stack.md`
  - line 301: `../.agent-os/product/roadmap.md`
  - line 302: `../.agent-os/product/decisions.md`
- Additional stale legacy residue in `docs/README.md`:
  - line 263: `.agent-os/` appears in the repo tree documentation.

Noise weakening routing trust:
- Root/index noise observed: `.cache/`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `logs/`, `reports/`, `tmp/`
- Trusted-path runtime/cache examples observed under `docs/` and `scripts/`, including `docs/reports/`, `docs/plans/.../logs/`, `scripts/**/__pycache__/`, and `scripts/coordination/routing/logs/`.

Concise next actions:
1. Add or restore `docs/maps/workspace-hub-operator-map.md` as the curated repo-local routing surface.
2. Add `docs/registry/module-routing.yaml` as the canonical machine-readable registry.
3. Replace the stale legacy links in `docs/README.md` with current canonical routing surfaces only.
4. Move/ignore runtime/cache/build/report noise so trusted routing paths stay low-noise.

### `digitalmodel` — yellow

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale surfaces:
- Broken active README link:
  - `README.md` → `specs/data-needs.yaml` (**missing target**)
- Stale repo-local map reference:
  - `docs/maps/digitalmodel-operator-map.md`, line 9 references `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` as if repo-local.
  - Missing repo-local target: `digitalmodel/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`
  - Matching workspace-level map still exists at: `/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

Noise weakening routing trust:
- Root noise observed: `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `build/`, `dist/`, `logs/`, `reports/`
- Trusted source path noise examples: many `src/digitalmodel/**/__pycache__/` entries.

Concise next actions:
1. Remove or retarget `README.md` → `specs/data-needs.yaml`.
2. Decide whether the OrcaWave/OrcaFlex operator map is repo-local or workspace-level, then update `docs/maps/digitalmodel-operator-map.md` accordingly.
3. Clean or ignore cache/runtime artifacts under source paths and repo root.

### `assetutilities` — yellow

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or missing surfaces:
- No missing required canonical surfaces detected.
- No broken active local Markdown links confirmed in the inspected canonical surfaces after false-positive filtering.

Noise weakening routing trust:
- Root noise observed: `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `build/`, `dist/`, `htmlcov/`, `logs/`, `reports/`
- Trusted source/test path noise examples: `src/assetutilities/**/__pycache__/`, `tests/**/__pycache__/`, and several test `logs/` directories.

Concise next actions:
1. Keep `AGENTS.md`, `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, and `docs/registry/module-routing.yaml` aligned as the canonical routing set.
2. Clean or ignore cache/runtime artifacts under `src/`, `tests/`, and repo root.
3. Continue treating prior broad path/table false positives as non-blocking unless they are actual Markdown targets or explicit current file references.

### `aceengineer-website` — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or missing surfaces:
- Missing required surface: `docs/registry/module-routing.yaml`
- No broken active local Markdown links confirmed in the inspected canonical surfaces after false-positive filtering.

Noise weakening routing trust:
- Root noise observed: `.coverage`, `.pytest_cache/`, `dist/`, `logs/`, `reports/`
- Trusted-path cache examples: `tests/**/__pycache__/`, `scripts/**/__pycache__/`

Concise next actions:
1. Add `docs/registry/module-routing.yaml` with canonical page/content/calculator/script/test routing.
2. Keep `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` as the human routing surfaces linked to the registry.
3. Clean or ignore runtime/cache output under root, `tests/`, and `scripts/`.

## 2026-04-22 Scorecard Assumption Check

Status: **the 2026-04-22 assumptions still hold directionally, but the point-in-time evidence needs current-state revision.**

Still holds:
- Overall verdict remains partial readiness only; the portfolio is not green.
- `workspace-hub` remains the richest control-plane repo, but routing trust is weakened by missing curated surfaces and root/index noise.
- `digitalmodel` remains the strongest engineering source/test structure, but stale references still reduce repo-wide retrieval trust.
- `aceengineer-website` remains understandable for direct edits but weak for durable issue routing until the canonical registry exists.
- `assetutilities` still needs source/test/root hygiene cleanup to reduce future code-placement ambiguity.

Needs revision from the 2026-04-22 point-in-time scorecard:
- `assetutilities` now has the required canonical surfaces (`docs/README.md`, operator map, registry); current yellow status is driven by cache/runtime hygiene, not missing routing surfaces or confirmed broken canonical links.
- `digitalmodel` now has repo-wide canonical surfaces and registry, but has a stale `README.md` target and stale repo-local reference to the OrcaWave/OrcaFlex map.
- `aceengineer-website` now has `docs/README.md` and an operator map, but remains red because `docs/registry/module-routing.yaml` is missing.
- The daily scorecard should continue using `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` as current authority rather than treating the 2026-04-22 report as canonical authority.

## Verification Notes

- Local report refreshed at: `docs/reports/tier-1-indexing-freshness-latest.md`
- No new cron jobs were scheduled.
- This report intentionally avoids recommending legacy `.agent-os` routing/reference patterns and uses current canonical routing surfaces only.
