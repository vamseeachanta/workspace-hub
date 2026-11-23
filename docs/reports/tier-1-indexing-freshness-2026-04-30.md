# Tier-1 Indexing Freshness Report

Generated: 2026-04-30T03:30:50-05:00 / 2026-04-30T08:30:50Z
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Source baseline: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
Prior scorecard checked: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
Automation script run: `scripts/cron/tier1-indexing-freshness.sh` returned portfolio red and refreshed the dated/latest artifacts before this richer manual verification pass.

## Overall Status

Portfolio status: **red**

No material drift detected in the canonical surface set since the latest remediation posture: `assetutilities` remains green, `aceengineer-website` remains yellow for the missing registry, and `workspace-hub` + `digitalmodel` remain red for missing required routing surfaces. One correction to the previous latest report: the old workspace-hub root-noise signature is still present in tracked top-level files, so root/index trust remains weakened by both raw-index/stale-reference issues and root noise.

## Repo Status

### workspace-hub — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**
- Supplementary/stale registry note: `specs/module-registry.yaml` exists but is **not** the canonical tier-1 registry path required by the current contract.

Exact broken or stale references in canonical surfaces:
- `docs/README.md:299` -> `../.agent-os/product/mission.md` — missing retired legacy product-doc path; must not be used as current routing authority.
- `docs/README.md:300` -> `../.agent-os/product/tech-stack.md` — missing retired legacy product-doc path.
- `docs/README.md:301` -> `../.agent-os/product/roadmap.md` — missing retired legacy product-doc path.
- `docs/README.md:302` -> `../.agent-os/product/decisions.md` — missing retired legacy product-doc path.
- `docs/README.md:263-264` still describes the retired `.agent-os/product/` tree in the active repository-structure block.

Routing/index hygiene:
- `docs/CONTENT_INDEX.md` still exists and remains a raw inventory surface only, not a trusted issue-routing surface.
- Tracked top-level root-noise files are present: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`.
- No tracked backup/temp artifacts were found in trusted source/doc/script scan roots by the refined check.

Concise next actions:
1. Complete #2464 by adding `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`.
2. Replace active retired product-doc links/structure text in `docs/README.md` with current canonical routing surfaces.
3. Remove or properly relocate the tracked root-noise files.
4. Keep `docs/CONTENT_INDEX.md` explicitly labeled as raw inventory, not routing authority.

### digitalmodel — red

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — **missing**
- `docs/maps/digitalmodel-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**
- `specs/module-registry.yaml` — missing; referenced as stale/non-canonical in active repo docs.
- `specs/data-needs.yaml` — missing; linked from active `README.md`.

Exact broken or stale references:
- `README.md:61` -> `specs/data-needs.yaml` — broken markdown link.
- `README.md:46` references `specs/module-registry.yaml` and explicitly says it is stale/not canonical; this remains unresolved until the current canonical registry exists.
- `ROADMAP.md:9` references `specs/module-registry.yaml` as the module ID authority, but that path does not exist and is not the current canonical tier-1 registry path.
- `ROADMAP.md:50` still instructs adding an entry to `specs/module-registry.yaml`, which is stale relative to the current `docs/registry/module-routing.yaml` contract.

Routing/index hygiene:
- High-value slice map still exists outside the repo-wide required path: `workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`.
- No repo-wide in-repo operator map exists at the required path.
- Tracked temp/runtime artifact found in trusted test path: `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`.
- Tracked coverage helper path observed under tests: `tests/test_automation/coverage/coverage_tracker.py`; this is not necessarily a backup artifact, but the `coverage/` placement should stay explicit so audits do not confuse it with generated coverage output.

Concise next actions:
1. Complete #2462 by adding `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml`.
2. Repair or retire the unresolved `specs/data-needs.yaml` link.
3. Replace stale `specs/module-registry.yaml` authority/instruction references with the current canonical registry path or an explicit retirement note.
4. Remove the tracked `.tmp` test artifact.
5. Link or fold the existing OrcaWave/OrcaFlex slice map into the new repo-wide operator map.

### assetutilities — green

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:
- No unresolved required canonical surfaces found.
- No broken markdown links found in inspected canonical surfaces.
- The existing audit script still reports six broken active references because it treats path-like code spans/globs literally. Manual verification classifies these as non-material false positives or examples, not broken required surfaces.

Routing/index hygiene:
- No tracked backup/temp artifacts were found in trusted source/test/script/docs scan roots by the refined check.
- This continues the material improvement from the 2026-04-22 scorecard: the repo is no longer missing `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`, or tracked source backup artifacts.

Concise next actions:
1. Treat #2461 as substantially remediated from an indexing-surface perspective.
2. Harden `scripts/cron/tier1-indexing-freshness.sh` to distinguish intentional globs/examples from broken literal paths.
3. Keep the operator map and `docs/registry/module-routing.yaml` synchronized as modules move.

### aceengineer-website — yellow

Canonical surfaces inspected:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or stale references:
- No broken markdown links found in inspected canonical surfaces.
- The existing audit script reports two broken active references because it treats wildcard/glob-style references literally; manual verification did not find those as broken canonical markdown links.

Routing/index hygiene:
- No tracked backup/temp artifacts were found in trusted source/content/script/test/doc roots by the refined check.
- Material improvement from 2026-04-22 still holds: `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` exist.

Concise next actions:
1. Complete #2463 by adding `docs/registry/module-routing.yaml`.
2. If wildcard test references remain in canonical surfaces, mark them explicitly as globs so literal-path audits do not produce false positives.
3. Keep deployment/content/calculator routing synchronized across `AGENTS.md`, `docs/README.md`, and the operator map.

## 2026-04-22 Scorecard Assumption Check

Status: **needs partial revision**.

Still holds:
- Portfolio is not green; required surfaces are still missing in `workspace-hub`, `digitalmodel`, and `aceengineer-website`.
- `workspace-hub` remains the richest control-plane repo but lacks required curated repo-wide routing surfaces and still has active retired product-doc references in `docs/README.md`.
- `digitalmodel` remains structurally strong but lacks the required repo-wide docs entry point, repo-wide operator map, and canonical machine-readable registry.
- `docs/CONTENT_INDEX.md` should remain raw inventory only, not trusted routing authority.
- `assetutilities` is no longer the highest-risk tier-1 repo from an indexing-surface perspective; it is currently green.

Needs revision / correction:
- `assetutilities` should not be described as missing `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`, or tracked source backup artifacts.
- `aceengineer-website` should not be described as missing `docs/README.md` or a repo-wide operator map; its remaining required missing surface is `docs/registry/module-routing.yaml`.
- The previous latest report's statement that the old workspace-hub tracked root-noise signature was not observed needs correction: the tracked top-level files `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, and `**Status:**` are currently present.
- The current freshness script needs refinement for wildcard/glob code-span handling; otherwise it overstates `assetutilities` and `aceengineer-website` as having broken references.

## Notes

This report intentionally avoids recommending or reinforcing legacy `.agent-os` product-doc reference patterns. Such paths are listed only as stale active references requiring replacement with current canonical routing surfaces.
