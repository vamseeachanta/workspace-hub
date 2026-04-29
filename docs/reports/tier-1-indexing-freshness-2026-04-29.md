# Tier-1 Indexing Freshness Audit — Latest

Generated: 2026-04-29T08:33:20Z

Scope:
- `workspace-hub` — `/mnt/local-analysis/workspace-hub`
- `digitalmodel` — `/mnt/local-analysis/workspace-hub/digitalmodel`
- `assetutilities` — `/mnt/local-analysis/workspace-hub/assetutilities`
- `aceengineer-website` — `/mnt/local-analysis/workspace-hub/aceengineer-website`

Canonical surfaces checked:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml`

Automation baseline:
- Ran `scripts/cron/tier1-indexing-freshness.sh`; script status was red (`EXIT:2`).
- This report also includes independent checks for broken links, stale registry references, legacy navigation references, tracked backup/cache/runtime noise, and workspace-hub index/root noise.

## Executive summary

Portfolio status: **red**.

Material drift since the 2026-04-28 freshness run:
- `workspace-hub` now has tracked runtime/log artifacts under trusted routing-adjacent paths, which weakens routing trust further:
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/README.md`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-2-doris-university.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-3-doris-codes.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-4-woodfibre.pid`
  - `scripts/coordination/routing/logs/agent-ratings.jsonl`
  - `scripts/coordination/routing/logs/provider_recommendations.jsonl`
  - `scripts/coordination/routing/logs/routing-decisions.jsonl`
- `digitalmodel` still has the prior tracked temp artifact and now also shows a tracked backup-like artifact in a documentation domain path:
  - `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`
  - `docs/domains/autocad/lisp/1_example_set/cd.bak.cui`

Stable findings from the prior run still hold:
- `assetutilities` remains green for tier-1 indexing surfaces.
- `aceengineer-website` remains yellow because its operator map and docs entry point exist, but its canonical registry is still missing.
- `workspace-hub` and `digitalmodel` remain red because required canonical routing surfaces are still absent.

## Per-repo status

| Repo | Status | Summary |
|---|---:|---|
| `workspace-hub` | red | Missing operator map and canonical registry; stale legacy navigation links remain in `docs/README.md`; tracked runtime/log artifacts now exist under trusted routing-adjacent paths; raw index remains oversized. |
| `digitalmodel` | red | Missing `docs/README.md`, repo-wide operator map, and canonical registry; stale `specs/` references remain; tracked temp/backup-like artifacts exist in trusted paths. |
| `assetutilities` | green | Required canonical surfaces are present; no broken canonical-surface links or tracked backup/temp artifacts found in trusted roots. |
| `aceengineer-website` | yellow | Docs entry point and operator map exist; canonical registry is still missing; no broken canonical-surface links or trusted-path noise found. |

## `workspace-hub` — red

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing canonical surfaces:
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken or stale references in canonical surfaces:
- `docs/README.md:299` → `../.agent-os/product/mission.md`
- `docs/README.md:300` → `../.agent-os/product/tech-stack.md`
- `docs/README.md:301` → `../.agent-os/product/roadmap.md`
- `docs/README.md:302` → `../.agent-os/product/decisions.md`

Legacy navigation references found in canonical surfaces:
- `docs/README.md:263` — tree entry for `.agent-os/`
- `docs/README.md:299-302` — links to retired product-doc locations listed above

Trusted-path backup/cache/runtime noise:
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/README.md`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.pid`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-2-doris-university.pid`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-3-doris-codes.pid`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-4-woodfibre.pid`
- `scripts/coordination/routing/logs/agent-ratings.jsonl`
- `scripts/coordination/routing/logs/provider_recommendations.jsonl`
- `scripts/coordination/routing/logs/routing-decisions.jsonl`

Index/root hygiene:
- `docs/CONTENT_INDEX.md` remains a raw inventory surface at 30,086 lines. It should not be treated as curated routing authority.

Concise next actions:
1. Add `docs/maps/workspace-hub-operator-map.md`.
2. Add `docs/registry/module-routing.yaml`.
3. Replace or remove stale legacy navigation links from `docs/README.md` using current canonical routing surfaces only.
4. Move or untrack runtime/log artifacts from `docs/plans/**/logs/` and `scripts/coordination/routing/logs/` so trusted routing paths stay clean.
5. Keep `docs/CONTENT_INDEX.md` explicitly classified as raw inventory, not canonical routing authority.

## `digitalmodel` — red

Present canonical surfaces:
- `AGENTS.md`
- `README.md`

Missing canonical surfaces:
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken or stale references:
- `README.md:61` → `specs/data-needs.yaml` is missing.
- `ROADMAP.md` references `specs/module-registry.yaml`, which is missing.

Trusted-path backup/cache/runtime noise:
- `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`
- `docs/domains/autocad/lisp/1_example_set/cd.bak.cui` — backup-like filename under a documentation/domain path; classify deliberately as either a required example artifact or remove/rename it to avoid backup-noise ambiguity.

Concise next actions:
1. Add `docs/README.md`.
2. Add `docs/maps/digitalmodel-operator-map.md`.
3. Add `docs/registry/module-routing.yaml`.
4. Repair or retire stale `specs/data-needs.yaml` and `specs/module-registry.yaml` references.
5. Remove the tracked `.tmp` integration-test artifact and resolve the `.bak.cui` artifact ambiguity.
6. Link or fold the existing workspace-level `digitalmodel` OrcaWave/OrcaFlex slice map into the repo-wide routing surface once the repo-wide map exists.

## `assetutilities` — green

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:
- None found.

Broken or stale references:
- None found in inspected canonical surfaces.

Trusted-path backup/cache/runtime noise:
- None found in trusted source/test/script/docs roots.

Concise next actions:
1. Keep `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, and `docs/registry/module-routing.yaml` synchronized.
2. Keep wildcard/glob references clearly marked as intentional globs so literal-path audits do not report false positives.

## `aceengineer-website` — yellow

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing canonical surfaces:
- `docs/registry/module-routing.yaml`

Broken or stale references:
- None found in inspected canonical surfaces.

Trusted-path backup/cache/runtime noise:
- None found in trusted source/content/script/test/docs roots.

Concise next actions:
1. Add `docs/registry/module-routing.yaml`.
2. Keep deployment/content/calculator routing synchronized across `AGENTS.md`, `docs/README.md`, and the operator map.
3. Keep wildcard test references clearly marked as intentional globs where used.

## 2026-04-22 scorecard assumption check

Decision: **the 2026-04-22 assumptions still need partial revision, and the portfolio remains red.**

Still holds:
- The portfolio is not green for tier-1 routing/indexing readiness.
- `workspace-hub` remains the richest control-plane repo but lacks required curated routing surfaces and still contains stale legacy navigation links in `docs/README.md`.
- `digitalmodel` remains structurally valuable but lacks the required repo-wide docs entry point, operator map, and canonical registry.
- `docs/CONTENT_INDEX.md` remains raw inventory only, not routing authority.

Needs revision or continued revision:
- `assetutilities` should remain revised upward to green; it has the required canonical surfaces and no trusted-path backup/temp artifacts were found in this run.
- `aceengineer-website` should remain revised upward from the original 2026-04-22 assumption: it now has `docs/README.md` and its operator map; only the canonical registry is missing.
- The prior note that `workspace-hub` root/index noise examples were absent no longer fully holds: this run found tracked runtime/log artifacts under routing-adjacent `docs/` and `scripts/` paths.
- `digitalmodel` trusted-path hygiene needs stricter treatment because both the known `.tmp` test artifact and a backup-like `.bak.cui` documentation-domain artifact are currently tracked.

## Overall next actions

1. Prioritize `workspace-hub` and `digitalmodel` because they remain red and block portfolio-wide routing trust.
2. Finish `aceengineer-website` by adding its canonical registry.
3. Keep `assetutilities` in maintenance mode and prevent regression.
4. Update the freshness script to distinguish intentional globs from literal missing paths and to flag tracked runtime/log artifacts under trusted routing paths.
