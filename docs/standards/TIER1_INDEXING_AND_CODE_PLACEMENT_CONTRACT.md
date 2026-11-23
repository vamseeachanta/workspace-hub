# Tier-1 Indexing and Code-Placement Contract

## Purpose

This contract defines the minimum trusted routing, indexing, and code-placement surfaces for tier-1 repositories. It keeps issue work anchored to curated routing surfaces instead of raw inventories, stale product-doc references, or broad generated indexes.

Tier-1 scope for this contract follows `docs/BUSINESS_BRAIN.md`:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `aceengineer-website`

MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority. Scorecards may be cited as local attestation only; they do not replace this standards contract, repo entry points, or issue-approved plans.

## Upstream Authority

- `docs/standards/CONTROL_PLANE_CONTRACT.md` is the authority for canonical repo entry points and routing surfaces.
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md` is the authority for baseline top-level repo anatomy.
- `docs/standards/DATA_PLACEMENT.md` is the binding threshold authority for repo-vs-bulk-artifact-store placement.

## Required Trusted Routing Surfaces

Each tier-1 repository must expose the following trusted routing surfaces. Optional repo-specific extensions may exist, but they do not replace these surfaces.

| Surface | Requirement | Authority / role |
|---|---|---|
| `AGENTS.md` | Required canonical worker entry point | `docs/standards/CONTROL_PLANE_CONTRACT.md` is the authority for canonical repo entry points and routing surfaces |
| `README.md` | Required human overview and top-level navigation | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` is the authority for baseline top-level repo anatomy |
| `docs/README.md` | Required documentation discovery surface where a repo has docs | Curated docs navigation |
| `docs/maps/<repo>-operator-map.md` | Required operator map for repo-specific work routing | Repo-specific curated routing surface |
| `docs/registry/module-routing.yaml` | Required canonical machine-readable registry for tools/agents to resolve canonical modules, domains, or surfaces | Machine-readable routing contract |
| code/tests/docs routing table | Required mapping from code areas to test and documentation surfaces | Issue planning and implementation routing |
| source-hygiene rules | Required rules for backup/cache/runtime/generated noise and legacy references | Prevents stale or noisy surfaces from becoming active authority |

The canonical machine-readable registry path is fixed as `docs/registry/module-routing.yaml` for every tier-1 repo. A child repo may add supplementary registries, but `docs/registry/module-routing.yaml` is the only canonical routing registry for this contract unless this standard is amended.

## Code / Tests / Docs Routing Table

Every tier-1 repository must maintain a code/tests/docs routing table that answers:

| Code or domain surface | Tests | Docs | Notes |
|---|---|---|---|
| package/module path | targeted test path or validator | canonical docs path | owner, issue link, or caveat |

The routing table may live in the operator map, docs README, or registry, but it must be discoverable from the required trusted routing surfaces.

## Repo-vs-Bulk-Artifact-Store Placement Rule

The universal placement rule is repo-vs-bulk-artifact-store.

A bulk-artifact-store is a non-repo storage target for large, generated, binary, or fast-growing artifacts. `/mnt/ace/data` is the current workspace-hub implementation example, not a universal hard-coded path for every machine or repo.

The binding threshold authority: docs/standards/DATA_PLACEMENT.md.

Operational thresholds copied from that authority:

- If a directory meets or will exceed `>= 10 MB` total, it belongs in the bulk-artifact-store rather than the repo.
- If a directory meets or will exceed `>= 1000 files`, it belongs in the bulk-artifact-store rather than the repo.

Small curated documentation, source, tests, registries, and operator maps belong in the repository. Large generated reports, raw crawls, caches, logs, and intermediate extraction outputs belong in the bulk-artifact-store unless a plan explicitly approves a small curated artifact for version control.

## Curated Routing Surfaces vs Raw Inventory

Curated routing surfaces are the authority for issue work. They are intentionally small, maintained, and reviewed. Examples:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- the repo's canonical `docs/registry/module-routing.yaml` registry
- the repo's code/tests/docs routing table

Raw inventory surfaces are discovery aids only. They can be broad, generated, stale, or noisy. `docs/CONTENT_INDEX.md` is a raw inventory example and must not be treated as a trusted issue-routing index by itself.

Workers may use raw inventory to discover candidate files, but must confirm final routing through curated routing surfaces before changing code, tests, docs, or registries.

## Legacy Product-Doc Retirement Rule

Legacy product-doc references may appear only as explicit migration or retirement notes. They are banned as active navigation authority, active routing authority, or required implementation sources.

Allowed:

- A migration note that says a legacy path was retired and points to the current canonical surface.
- A short historical note explaining why a reference was removed.
- A test fixture intentionally validating stale-reference detection.

Banned signature categories:

- [x] `legacy filenames` used as current navigation authority, such as obsolete product roadmap or decision filenames.
- [x] `legacy path fragments` used as current routing authority, such as retired product-doc directory fragments.
- [x] `legacy reference blocks` copied into active docs as if they still define the current workflow.
- [x] `provider-specific stale navigation` that bypasses `AGENTS.md`, `README.md`, `docs/README.md`, or the operator map.

Any active reference to a retired product-doc surface must be replaced with a current canonical routing surface or moved into an explicit retirement note.

## Daily Freshness Review

Tier-1 routing/indexing must receive a daily freshness review every 24 hours. Once per day is the minimum cadence.

The daily freshness review must include refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md` and checking whether the required trusted routing surfaces are present, current, and still linked from the expected discovery points.

#2465 is the follow-through issue for implementing the daily freshness review automation and report refresh path.

## Child Issue Linkage

This contract defines the shared rule set. Repo-specific and automation follow-through stays in child issues:

- #2461 — `assetutilities` canonical routing surfaces and source-hygiene cleanup
- #2462 — `digitalmodel` repo-wide operator map and canonical routing surfaces
- #2463 — `aceengineer-website` canonical routing surfaces and legacy product-doc reference cleanup
- #2464 — `workspace-hub` curated routing index split and routing-noise cleanup
- #2465 — daily freshness review automation and scorecard/report refresh

## Implementation Boundary

This issue creates the contract and checklist. It does not complete the repo-specific remediation work in #2461-#2464 and does not implement the daily automation in #2465.

Implementation of this contract must remain TDD-first and must keep source-hygiene rules focused on curated routing docs, tests, and approved standards artifacts.
