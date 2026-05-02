# Tier-1 Indexing Freshness Report

Generated: 2026-04-28T08:33:37Z
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Source baseline: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
Prior scorecard checked: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`

## Overall Status

Portfolio status: **red**

Material drift/remediation since the 2026-04-22 scorecard was detected:
- `assetutilities` now has the full required canonical routing surface set and no tracked backup/temp artifacts in trusted source paths.
- `aceengineer-website` now has `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md`, but still lacks the canonical machine-readable registry.
- `workspace-hub` and `digitalmodel` still have missing required routing surfaces, so portfolio-level assumptions remain only partially ready.

## Repo Status

### workspace-hub — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**

Broken/stale references in canonical surfaces:
- `docs/README.md` links to retired legacy product-doc paths that are not present and must not be used as current routing authority:
  - `../.agent-os/product/mission.md`
  - `../.agent-os/product/tech-stack.md`
  - `../.agent-os/product/roadmap.md`
  - `../.agent-os/product/decisions.md`

Routing/index hygiene:
- `docs/CONTENT_INDEX.md` exists and is very large (`30086` lines); it remains useful as raw inventory only, not a trusted issue-routing surface.
- Top-level tracked root-noise signature from the 2026-04-22 scorecard was not observed in the current checked top-level tracked-file sample.
- No backup/temp artifacts were found in the trusted scan roots checked for this audit.

Concise next actions:
1. Complete #2464 by adding `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`.
2. Replace the active legacy product-doc links in `docs/README.md` with current canonical routing surfaces.
3. Keep `docs/CONTENT_INDEX.md` explicitly labeled as raw inventory, not routing authority.

### digitalmodel — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — **missing**
- `docs/maps/digitalmodel-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**

Broken/stale references in canonical or active repo navigation:
- `README.md` markdown link/reference to `specs/data-needs.yaml` does not resolve.
- `README.md` references `specs/module-registry.yaml`; that registry does not exist.
- `ROADMAP.md` also references `specs/module-registry.yaml`; that registry does not exist.

Routing/index hygiene:
- A high-value slice map still exists outside the repo-wide required path: `workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`.
- No repo-wide operator map exists at the required in-repo path.
- One tracked temp artifact was found in a trusted test path: `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`.

Concise next actions:
1. Complete #2462 by adding `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml`.
2. Repair or retire the unresolved `specs/data-needs.yaml` link and stale `specs/module-registry.yaml` references.
3. Remove the tracked `.tmp` test artifact from `tests/workflows/integration/`.
4. Fold the existing OrcaWave/OrcaFlex slice map into the new repo-wide routing surface or link to it from the repo-wide operator map.

### assetutilities — green

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Broken/stale references:
- No unresolved required canonical surfaces found.
- Several wildcard code-span references in `README.md`, `docs/README.md`, and `docs/maps/assetutilities-operator-map.md` resolve as globs on disk, including:
  - `docs/sub_*`
  - `tests/unit/test_common_*.py`
  - `tests/unit/test_visualization*.py`
  - `tests/modules/**/results/`
  - `tests/unit/test_traceability*.py`

Routing/index hygiene:
- No tracked backup/temp artifacts were found in trusted source/test/script roots.
- This is a material improvement from the 2026-04-22 scorecard, which reported tracked `.bak`/`.orig` artifacts under `src/assetutilities/common/`.

Concise next actions:
1. Treat #2461 as substantially remediated from an indexing-surface perspective.
2. Optional: convert wildcard routing references to explicit examples plus a note that they are intentional globs, to avoid false positives in literal-path audits.
3. Keep the registry and operator map synchronized as modules move.

### aceengineer-website — yellow

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Broken/stale references:
- No broken markdown links found in inspected canonical surfaces.
- Wildcard test references to `tests/js/*calculator*.test.js` resolve to existing files (`tests/js/npv-calculator.test.js`, `tests/js/obs-calculator.test.js`), but literal-path audit scripts may flag them unless the glob intent is explicit.

Routing/index hygiene:
- No tracked backup/temp artifacts were found in trusted source/content/script/test/doc roots.
- Material improvement since the 2026-04-22 scorecard: `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` now exist.

Concise next actions:
1. Complete #2463 by adding `docs/registry/module-routing.yaml`.
2. Make wildcard test references explicitly marked as globs or replace with exact representative paths plus glob notes.
3. Keep deployment/content/calculator routing in sync across `AGENTS.md`, `docs/README.md`, and the operator map.

## 2026-04-22 Scorecard Assumption Check

Status: **needs partial revision**.

Still holds:
- Portfolio is not green; required surfaces are still missing in `workspace-hub`, `digitalmodel`, and `aceengineer-website`.
- `workspace-hub` remains the richest control-plane repo but still lacks required curated repo-wide routing surfaces and still has active stale legacy references in `docs/README.md`.
- `digitalmodel` remains structurally strong but lacks the required repo-wide docs entry point, operator map, and canonical registry.
- `docs/CONTENT_INDEX.md` should remain raw inventory only, not trusted routing authority.

Needs revision:
- `assetutilities` should no longer be described as missing `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`, or tracked source backup artifacts; those checks are currently green.
- `aceengineer-website` should no longer be described as missing `docs/README.md` or a repo-wide operator map; the remaining required missing surface is `docs/registry/module-routing.yaml`.
- The prior root-noise examples for `workspace-hub` were not observed in the current tracked top-level-file check; root/index trust is still weakened by raw-index size and stale references, not by those exact root artifacts in this run.

## Notes

This report intentionally avoids recommending or reinforcing legacy `.agent-os`/product-doc reference patterns. Those paths are reported only as stale active references requiring replacement with current canonical routing surfaces.
