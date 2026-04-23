# Tier-1 Repo Indexing Scorecard

Date: 2026-04-22
Repo: workspace-hub
Scope: workspace-hub, digitalmodel, assetutilities, aceengineer-website
Purpose: assess whether tier-1 repos are indexed well enough that ongoing GitHub issue work lands in the right place and can be retrieved reliably later.

## Executive Summary

Overall verdict: partial readiness only.

The tier-1 portfolio is not yet consistently indexed well enough to guarantee either:
1. new code lands in the correct location without rediscovery, or
2. future GitHub issue work can retrieve the canonical target path quickly and reliably.

Current portfolio pattern:
- workspace-hub has the richest control-plane documentation, but its retrieval/index surfaces are noisy.
- digitalmodel has the strongest engineering source/test structure, but important canonical navigation surfaces are incomplete or stale.
- assetutilities has the weakest package information architecture and the highest misplacement risk.
- aceengineer-website is understandable for direct edits, but weak for durable issue-routing and canonical retrieval.

## Scoring Rubric

Each repo is scored 1-5 on:
- Mission clarity: can a worker quickly understand what belongs in the repo?
- Code placement guidance: are there trusted routing surfaces that say where code should go?
- Retrieval readiness: can a future issue quickly find canonical code/tests/docs surfaces?
- Index hygiene: are the indexing/navigation surfaces current, curated, and low-noise?

## Scorecard

| Repo | Mission clarity | Code placement guidance | Retrieval readiness | Index hygiene | Total / 20 | Assessment |
| --- | --- | --- | --- | --- | --- | --- |
| digitalmodel | 4 | 4 | 3 | 2 | 13 | Strong codebase structure, incomplete/stale repo-wide indexing |
| workspace-hub | 4 | 3 | 3 | 2 | 12 | Strong control plane, weak curation hygiene |
| aceengineer-website | 3 | 2 | 2 | 2 | 9 | Fine for direct static-site edits, weak canonical retrieval |
| assetutilities | 3 | 2 | 2 | 1 | 8 | Highest risk of putting code in the wrong place |

## Repo Findings

### 1. digitalmodel

Strengths
- `digitalmodel/AGENTS.md` is concise and useful: purpose, entry points, test command, dependency on assetutilities.
- `digitalmodel/README.md` gives meaningful engineering context and points to major module families.
- Source/test domain parity is strong: 30 overlapping top-level source/test domains.
- `docs/domains/README.md` correctly points active OrcaWave/OrcaFlex work to the workspace operator map.
- The OrcaWave/OrcaFlex operator map is a high-value retrieval surface:
  - `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

Weaknesses
- No `digitalmodel/docs/README.md` master documentation entry point exists.
- `digitalmodel/README.md` explicitly says the earlier module registry reference is stale/not present.
- `digitalmodel/ROADMAP.md` still references `specs/module-registry.yaml` as if it were canonical.
- The strongest routing artifact is only for the OrcaWave/OrcaFlex slice, not the repo as a whole.
- Search results show many local navigation/index files under `docs/domains/`, but no single repo-wide canonical operator map.

Evidence
- `digitalmodel/README.md`
- `digitalmodel/ROADMAP.md`
- `digitalmodel/docs/domains/README.md`
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

Assessment
- Best tier-1 repo for structural engineering code placement.
- Still needs a repo-wide canonical routing/index layer.

### 2. workspace-hub

Strengths
- Strong portfolio/control-plane context:
  - `docs/BUSINESS_BRAIN.md`
  - `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
  - `docs/README.md`
  - `docs/standards/FILE_STRUCTURE_TAXONOMY.md`
  - `docs/standards/DATA_PLACEMENT.md`
- Strong workflow/reporting surfaces:
  - `docs/plans/`
  - `docs/handoffs/`
  - `docs/reports/`
  - `docs/maps/`
- Strong skill/knowledge discovery surface:
  - `docs/SKILLS_INDEX.md`

Weaknesses
- `docs/CONTENT_INDEX.md` is too broad/noisy to serve as a trusted issue-routing index.
- It includes archive, environment, and cross-repo spillover, which weakens path trust.
- The repo root contains clearly misplaced tracked artifacts, including files named:
  - `**Complexity:**`
  - `**Date:**`
  - `**Issue:**`
  - `**Review`
  - `**Source`
  - `**Status:**`
  - `-`
  - `Compatibility`
  - `Comprehensive`
  - `This`
- The accessibility registry explicitly records discoverability gaps for assets not linked from `docs/README.md`.

Evidence
- `docs/CONTENT_INDEX.md`
- `docs/README.md`
- `data/document-index/intelligence-accessibility-registry.yaml`
- top-level tracked file inventory from `git ls-files`

Assessment
- Strongest repo for ecosystem-level orientation.
- Not yet clean enough to be the trusted portfolio routing index for future issue execution.

### 3. aceengineer-website

Strengths
- `aceengineer-website/README.md` explains deployment, root-page layout, and overall site structure.
- `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` provides a short current-state map.
- Static site structure is straightforward for obvious page edits.

Weaknesses
- `aceengineer-website/AGENTS.md` is only a pointer, not a repo-specific routing contract.
- `README.md` and `docs/DEPLOYMENT_GUIDE.md` still point to legacy missing product-doc references.
- No `docs/README.md` canonical entry point exists.
- No repo-wide operator map exists for page/content/calculator/script/test routing.
- `.github/workflows/` exists but currently contains no workflow files.

Evidence
- `aceengineer-website/AGENTS.md`
- `aceengineer-website/README.md`
- `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md`
- `aceengineer-website/docs/DEPLOYMENT_GUIDE.md`

Assessment
- Good enough for direct page edits.
- Not strong enough for repeatable issue-routing across content, demos, calculators, scripts, and tests.

### 4. assetutilities

Strengths
- `assetutilities/AGENTS.md` is concise and points to current package entry points.
- `assetutilities/MODULE_STRUCTURE.md` attempts to define placement guidance.
- The repo has substantial real source under `src/assetutilities/`.

Weaknesses
- `assetutilities/README.md` is stale and not trustworthy as a current architecture guide.
- No `assetutilities/docs/README.md` exists.
- `MODULE_STRUCTURE.md` does not align cleanly enough with the observed package layout to serve as authoritative routing guidance.
- Source/test parity is weak: only two overlapping top-level source/test domains.
- Source tree contains backup artifacts directly in package paths:
  - `src/assetutilities/common/ApplicationManager.py.bak`
  - `src/assetutilities/common/ApplicationManager.py.orig`
  - `src/assetutilities/common/file_management.py.bak`
  - `src/assetutilities/common/file_management.py.orig`
- Source inventory shows substantial runtime/cache noise under package paths, which hurts retrieval clarity.

Evidence
- `assetutilities/README.md`
- `assetutilities/MODULE_STRUCTURE.md`
- `assetutilities/AGENTS.md`
- `src/assetutilities/` inventory and tracked backup files

Assessment
- Highest risk tier-1 repo for misplaced future work.
- Needs canonical code-placement surfaces before more issue execution accumulates.

## Portfolio-Level Gaps

1. Canonical entry points are inconsistent.
- Some repos have usable `AGENTS.md` + `README.md`.
- Some rely on partial or stale navigation.
- Only one high-value operator map exists today, and it covers a single slice.

2. Trusted machine-readable routing is missing.
- No consistent repo-level module/operator registry exists across all tier-1 repos.
- digitalmodel still has stale registry references without a restored canonical registry.

3. Retrieval surfaces are too noisy.
- workspace-hub root hygiene is poor.
- workspace-hub content index is too broad for routing.
- assetutilities contains backup artifacts in package paths.

4. Documentation freshness is not yet operationalized.
- There is no daily curation job dedicated to tier-1 routing/index freshness.
- Several broken or stale references remain live in tier-1 repos.

## Recommended Target Contract for Every Tier-1 Repo

Each tier-1 repo should have exactly these trusted routing surfaces:

1. `AGENTS.md`
- repo-specific purpose
- exact entry points
- exact test command
- common issue type -> target path hints

2. `README.md`
- current architecture only
- no broken links
- no stale legacy references

3. `docs/README.md`
- canonical repo documentation entry point
- code/tests/docs routing table
- common issue type -> path map

4. `docs/maps/<repo>-operator-map.md`
- module -> source path
- tests path
- related docs path
- common issue labels / work types
- key dependencies

5. machine-readable registry
- one canonical YAML/JSON mapping for module/domain ownership and retrieval

6. hygiene rules
- no backup artifacts under source paths
- no cache/runtime noise in tracked source locations
- no broken legacy references
- no raw-inventory files masquerading as curated routing indexes

## Priority Order

1. assetutilities
- highest risk of code landing in the wrong place

2. digitalmodel
- highest value from a repo-wide canonical index because the codebase is already mature and broad

3. aceengineer-website
- quick trust win by removing legacy broken references and adding canonical routing docs

4. workspace-hub
- strongest overall context already exists; main need is curation, discoverability, and root/index hygiene

## Proposed Follow-On Issue Set

1. Portfolio contract issue
- define a tier-1 indexing and code-placement contract used by all tier-1 repos

2. assetutilities remediation issue
- canonical docs entry point, operator map, structure cleanup, and source-hygiene cleanup

3. digitalmodel remediation issue
- repo-wide operator map, restore/replace module registry, align roadmap/readme/docs

4. aceengineer-website remediation issue
- remove legacy product-doc references, add canonical docs entry point and operator map

5. workspace-hub remediation issue
- split curated routing index from raw inventory, improve discoverability, and clean top-level routing noise

## Daily Maintenance Requirement

This report should not remain point-in-time only.

Requirement:
- tier-1 repo curation/index freshness should be checked at least daily
- stale references, broken canonical links, missing operator maps, and source-hygiene drift should be surfaced in a daily maintenance loop
- repo curation must avoid legacy product-doc conventions and use current canonical routing surfaces only
