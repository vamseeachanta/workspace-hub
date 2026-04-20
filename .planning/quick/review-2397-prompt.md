# Adversarial Plan Review Request: Issue #2397

You are an adversarial reviewer. Assume the plan has defects until proven otherwise.
Do not praise. Do not restate the plan. Focus only on what is wrong, missing, risky, contradictory, underspecified, or likely to cause rework.
Return APPROVE only if you can affirmatively verify there are no blocking defects.
Each finding must cite a specific plan section, file path, issue reference, or quoted claim.
If nothing is wrong, explicitly state what you checked.

## Issue context
Title: epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos
URL: https://github.com/vamseeachanta/workspace-hub/issues/2397

Issue body:
## Summary
Create a dedicated follow-up issue for repo-wide structural refactors that are broader than code cleanup alone. The current tier-1 refactor umbrella (#1962) identifies architectural debt and duplicate patterns, but it does not yet break out a canonical folder-structure and repository-layout workstream.

## Why
Refactors keep stalling at the module/file level when the underlying repo shape is still inconsistent. The next pass should explicitly normalize repository anatomy so agents, humans, tests, CI, and future automation can navigate repos the same way.

This is especially important across tier-1 repos where differences in `src/` layout, test placement, docs organization, examples, fixtures, generated outputs, and archive boundaries create avoidable friction during implementation and review.

## Scope
Define and execute a repo-organization refactor contract across tier-1 repos, including:
- canonical top-level directory layout
- source/package placement (`src/` vs flat-package decision per repo, with migration guidance)
- test directory mirroring and fixture placement
- docs/knowledge/reference placement and archival boundaries
- scripts/tools/generated-artifact separation
- examples/demo/notebook/data-sample placement
- deprecation of legacy/duplicate folders
- import-surface and public-API stability rules during moves
- migration/redirect strategy for moved files and paths

## Deliverables
1. A scored inventory of current folder-structure drift across tier-1 repos.
2. A canonical repo-layout contract with allowed variations and anti-patterns.
3. A per-repo migration matrix showing:
   - current layout
   - target layout
   - breaking-risk level
   - path moves / redirects needed
4. Child execution issues for repos where structural migration should happen separately.
5. Validation checks to prevent regressions (for example path-policy checks, stale-path detection, docs reference checks, smoke tests).

## Acceptance Criteria
- [ ] tier-1 repos have a documented target folder-structure contract
- [ ] current drift is inventoried by repo with concrete path-level findings
- [ ] structural work is separated into follow-up implementation issues instead of being buried in umbrella comments
- [ ] validation/guardrail checks are defined so future repo drift is detected automatically
- [ ] issue explicitly states which changes are safe renames vs breaking-path migrations

## Related
- #1962 Tier-1 Repo Ecosystem Refactoring
- #1567 Continuous Repo Architecture Intelligence
- #1603 Multi-repo architecture scan
- #84 aceengineer-admin repo restructure — canonical document taxonomy
- #1404 Organize /mnt/ace/docs/ subfolders and deduplicate engineering references

## Notes
This issue is intentionally about repository anatomy and navigation, not about individual feature implementations inside any one repo.


## Latest revised draft plan under review
# Plan for #2397: Canonical folder structure and refactor contract across tier-1 repos

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2397
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2397-claude.md | scripts/review/results/2026-04-20-plan-2397-codex.md | scripts/review/results/2026-04-20-plan-2397-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/standards/FILE_STRUCTURE_TAXONOMY.md` — defines workspace-hub directory classes, starter-repo taxonomy expectations, and migration recommendations for legacy surfaces.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — defines required repo entry points (`AGENTS.md`, `.claude/`, `.codex/`, `.gemini/`) and rollout expectations across starter/tier-1 repos.
- Found: `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md` — names the current canonical tier-1 repos (`assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing`) and distinguishes them from the hub.
- Gap: no canonical cross-tier-1 migration matrix exists for folder structure, test mirroring, docs placement, generated-output boundaries, child execution issue generation, or path-governance checks.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane repo entrypoint contract | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Workspace file-structure taxonomy | done | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| AI review routing policy for structural work | done | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### LLM Wiki pages consulted
- No relevant wiki pages; this is repo-governance and structure work anchored in docs/standards and issue state.

### Documents consulted
- `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md` — authoritative current tier-1 repo list for this plan: `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing`.
- `docs/reports/2026-04-20-refactor-knowledge-release-readiness-dependency-map.md` — identifies #2397 as a focused structural-design child that should feed #1962.
- Related issue #1962 — broad umbrella for tier-1 refactoring; currently lacks a dedicated folder-structure workstream.
- Related issue #1567 — architecture-intelligence umbrella that can provide evidence inputs but does not itself define the path-governance contract.
- Related issue #1603 — multi-repo architecture scan; useful evidence feeder for repo layout inventory.
- Related issue #1661 — dependency cycle/layering scanner extension; useful for detecting structural risk during normalization.
- Existing issue body for #2397 — explicitly requires safe-renames vs breaking-path migration classification, child execution issues, and automatic drift-detection guardrails.

### Scoring rubric
- `required-path coverage` (0-3) — AGENTS/adapter/source/tests/docs layout present or justified
- `layout consistency` (0-3) — source/tests/docs/scripts placement matches the contract or documented exception
- `migration risk` (0-3) — extent of import/path breakage risk
- `legacy-drift burden` (0-3) — duplicate/deprecated path cleanup burden
- Aggregate score is documented per repo alongside a separate boolean classification for `safe rename` vs `breaking-path migration`.

### Gaps identified
- No scored inventory of folder-structure drift across tier-1 repos.
- No canonical target layout contract that distinguishes required vs allowed variations.
- No migration matrix that classifies safe moves vs breaking-path migrations.
- No regression checks that detect re-introduction of path/layout drift.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-20-issue-2397-canonical-folder-structure-and-refactor-contract.md |
| Shared dependency map | docs/reports/2026-04-20-refactor-knowledge-release-readiness-dependency-map.md |
| Main report | docs/reports/2026-04-20-issue-2397-tier1-repo-structure-contract.md |
| Child issue drafts | docs/reports/2026-04-20-issue-2397-structural-migration-issue-drafts.md |
| Guardrail checker | scripts/analysis/check_tier1_repo_structure.py |
| Guardrail checker tests | tests/scripts/test_check_tier1_repo_structure.py |
| Plan review — Claude | scripts/review/results/2026-04-20-plan-2397-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-20-plan-2397-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-20-plan-2397-gemini.md |
| Docs updates | docs/plans/README.md |

---

## Deliverable

A canonical tier-1 repo-structure contract with migration matrix, child issue drafts for non-trivial repo moves, and an executable checker/test surface for future path/layout drift.

---

## Pseudocode

```
set tier_1_repo_list from `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md`
resolve each repo as an already-present local subdirectory under the workspace root
for each repo in tier_1_repo_list:
    inspect top-level directories, source layout, tests, docs, scripts, generated artifacts, legacy paths
    score observed layout using the explicit 0-3 rubric categories in this plan
    classify each drift item as required fix, allowed variation, documented exception, safe rename, or breaking-path migration
assemble target layout contract with required paths, optional paths, forbidden anti-patterns, and import-surface compatibility rules
build migration matrix with per-repo target state, score, risk level, and move strategy
emit child execution issue drafts for repos whose migration exceeds low-risk housekeeping
implement a structure-check script that validates required paths, forbidden drift patterns, and rubric-backed safe-vs-breaking classifications
add tests proving the checker flags at least one known-bad layout, catches contradiction with `FILE_STRUCTURE_TAXONOMY.md`, and passes a compliant sample
write report, child-issue draft pack, and checker/test paths for future enforcement
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/2026-04-20-issue-2397-tier1-repo-structure-contract.md | canonical structural contract + migration matrix |
| Create | docs/reports/2026-04-20-issue-2397-structural-migration-issue-drafts.md | one follow-up issue draft per repo needing non-trivial migration |
| Create | scripts/analysis/check_tier1_repo_structure.py | executable guardrail surface for future drift detection |
| Create | tests/scripts/test_check_tier1_repo_structure.py | regression coverage for the checker |
| Create | .github/workflows/tier1-repo-structure-check.yml | makes the checker automatic in CI once implemented |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_checker_passes_compliant_sample | compliant layout is accepted | sample repo fixture matching contract | exit code 0 / no violations |
| test_checker_flags_missing_required_paths | required-path drift is caught | sample fixture missing `AGENTS.md` or `tests/` | named violation |
| test_checker_flags_forbidden_legacy_paths | forbidden/legacy drift is caught | sample fixture with banned layout pattern | named violation |
| test_checker_catches_taxonomy_contradiction | checker and contract do not contradict `FILE_STRUCTURE_TAXONOMY.md` | sample contradicting taxonomy rule | named contradiction |
| test_issue_draft_pack_covers_each_non_trivial_repo | migration follow-up output is actionable | migration matrix above threshold | matching issue draft entry |
| test_safe_vs_breaking_classification_is_explicit | rename risk classification is objective | candidate path move | `safe rename` or `breaking-path migration` result |

---

## Acceptance Criteria

- [ ] A report exists at `docs/reports/2026-04-20-issue-2397-tier1-repo-structure-contract.md`
- [ ] A child-issue draft pack exists at `docs/reports/2026-04-20-issue-2397-structural-migration-issue-drafts.md`
- [ ] A structure-check script exists at `scripts/analysis/check_tier1_repo_structure.py` with regression tests in `tests/scripts/test_check_tier1_repo_structure.py`
- [ ] A CI workflow exists at `.github/workflows/tier1-repo-structure-check.yml` to make drift detection automatic once implemented
- [ ] The report inventories current structural drift across all canonical tier-1 repos
- [ ] The report defines a canonical target layout with allowed variations and anti-patterns
- [ ] The report includes a per-repo migration matrix with risk levels and likely move strategies
- [ ] The migration matrix explicitly classifies each non-trivial path move as `safe rename` or `breaking-path migration`
- [ ] The draft pack contains a follow-up issue draft for each repo whose migration exceeds low-risk housekeeping
- [ ] The checker/test suite proves future drift can be detected automatically and does not contradict `FILE_STRUCTURE_TAXONOMY.md`
- [ ] Review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Awaiting review |
| Codex | PENDING | Awaiting review |
| Gemini | PENDING | Awaiting review |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** tier-1 repo membership/rank ordering in older issues may disagree with current canonical terminology; final report must use canonical names from the ecosystem terminology reference.
- **Risk:** some repos may intentionally differ due to non-Python or mixed-purpose structure; the contract must distinguish justified exceptions from drift.
- **Open:** should the checker enforce only the canonical tier-1 contract in v1, or also support an explicit exceptions registry from day one?

---

## Complexity: T2

**T2** — multi-source structural-analysis plan producing a bounded contract/report artifact without immediate code migration.


## Review dimensions
1. Correctness
2. Completeness
3. Feasibility
4. TDD / verification adequacy
5. Scope discipline
6. Dependency handling
7. Approval readiness
8. Retrieval adequacy

## Required output format
Verdict: APPROVE | MINOR | MAJOR
Retrieval adequacy: adequate | insufficient
Findings:
- [severity] <finding>
Missing tests:
- ...
Scope creep concerns:
- ...
Weakest assumption:
- ...
Most likely implementation failure mode:
- ...
Most likely test gap:
- ...
Future issues suggested:
- ...
Review confidence: low | medium | high
