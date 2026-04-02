# Phase G — Per-Repo Ecosystem Audit

**Date**: 2026-04-02
**Issue**: #1720
**Repos Scanned**: 24 (all with `.claude/` directories)
**Tier-1 Repos**: assetutilities, digitalmodel, worldenergydata, assethold

---

## 1. Full 24-Repo Ecosystem Inventory

| # | Repo                        | Skills | Cmds | Docs | Rules | WQ     | AGENTS   | CLAUDE    | Git 90d | Tier   |
|---|------------------------------|--------|------|------|-------|--------|----------|-----------|---------|--------|
| 1 | workspace-hub               | 2,879  | 2    | 30   | Y     | 1p     | standalone | 8L      | 2,477   | tier-2 |
| 2 | CAD-DEVELOPMENTS            | 296    | 2    | 8    | Y     | 54p    | MISSING  | 99L       | 265     | tier-2 |
| 3 | aceengineer-website         | 0      | 0    | 0    | -     | -      | pointer  | 9L        | 111     | tier-2 |
| 4 | digitalmodel                | 3      | 9    | 19   | -     | Y      | standalone | 15L     | 92      | tier-1 |
| 5 | assetutilities              | 4      | 1    | 4    | -     | -      | standalone | 15L     | 82      | tier-1 |
| 6 | assethold                   | 0      | 1    | 4    | -     | -      | standalone | 746L*   | 62      | tier-1 |
| 7 | sabithaandkrishnaestates    | 0      | 1    | 0    | -     | -      | pointer  | 740L*     | 35      | tier-2 |
| 8 | teamresumes                 | 0      | 1    | 6    | -     | -      | pointer  | 740L*     | 32      | tier-2 |
| 9 | acma-projects               | 0      | 0    | 4    | -     | -      | pointer  | 9L        | 30      | tier-2 |
| 10| achantas-data               | 13     | 1    | 0    | -     | -      | pointer  | 44L       | 27      | tier-2 |
| 11| worldenergydata             | 33     | 7    | 8    | -     | -      | standalone | 19L     | 21      | tier-1 |
| 12| investments                 | 0      | 1    | 0    | -     | -      | pointer  | 740L*     | 17      | tier-2 |
| 13| sd-work                     | 0      | 1    | 0    | -     | -      | pointer  | 9L        | 16      | tier-2 |
| 14| hobbies                     | 0      | 0    | 0    | -     | -      | pointer  | 752L*     | 13      | tier-2 |
| 15| aceengineer-admin           | 1      | 1    | 0    | -     | -      | pointer  | 9L        | 5       | tier-2 |
| 16| client_projects             | 0      | 1    | 0    | -     | -      | pointer  | 9L        | 5       | tier-2 |
| 17| OGManufacturing             | 0      | 1    | 0    | -     | -      | standalone | 9L      | 4       | tier-2 |
| 18| doris                       | 0      | 1    | 2    | -     | -      | pointer  | 9L        | 4       | tier-2 |
| 19| frontierdeepwater           | 0      | 1    | 0    | -     | -      | pointer  | 9L        | 4       | tier-2 |
| 20| rock-oil-field              | 0      | 0    | 4    | -     | -      | pointer  | 32L       | 4       | tier-2 |
| 21| saipem                      | 0      | 1    | 4    | -     | -      | pointer  | 9L        | 4       | tier-2 |
| 22| seanation                   | 0      | 1    | 0    | -     | -      | pointer  | 9L        | 4       | tier-2 |
| 23| aceengineer-strategy        | 0      | 0    | 0    | -     | -      | MISSING  | MISSING   | 3       | tier-2 |
| 24| simpledigitalmarketing      | 0      | 0    | 0    | -     | -      | pointer  | 32L       | 1       | tier-2 |

**Legend**: WQ = Work Queue (p = pending items). CLAUDE column: L = lines, * = has unresolved merge conflict.

**Summary**:
- Skills total: 3,229 across ecosystem (89.2% in workspace-hub, 9.2% in CAD-DEVELOPMENTS)
- Commands: 32 total across repos
- Repos with standalone AGENTS.md: 6
- Repos with pointer AGENTS.md: 16
- Repos missing AGENTS.md: 2 (CAD-DEVELOPMENTS, aceengineer-strategy)
- Repos with rules: 2 (workspace-hub, CAD-DEVELOPMENTS)
- Repos with work queue: 3 (workspace-hub, CAD-DEVELOPMENTS, digitalmodel)

---

## 2. AGENTS.md Consistency Check

### Standalone AGENTS.md (6 repos)

| Repo              | Lines | Entry Points | Test Command | Depends On | Issues |
|-------------------|-------|-------------|--------------|------------|--------|
| workspace-hub     | 19    | No          | No           | No         | Minimal — serves as canonical contract |
| digitalmodel      | 12    | Yes         | Yes          | Yes        | CLEAN |
| assetutilities    | 12    | Yes         | Yes          | Yes        | CLEAN |
| assethold         | 12    | Yes         | Yes          | Yes        | CLEAN |
| worldenergydata   | 13    | Yes         | Yes          | Yes        | CLEAN |
| OGManufacturing   | 12    | Yes         | Yes          | Yes        | **WARNING**: has test_command but tests/ has 0 test files |

### Pointer AGENTS.md (16 repos)

All pointer repos use the standard 10-line template referencing workspace-hub/AGENTS.md as canonical. This is correct — they inherit the contract.

### Missing AGENTS.md (2 repos)

| Repo                  | Git Activity | Impact |
|-----------------------|-------------|--------|
| CAD-DEVELOPMENTS      | 265 commits | **HIGH** — 2nd most active repo, 296 skills, has its own rules |
| aceengineer-strategy  | 3 commits   | LOW — private strategy repo, minimal activity |

**Recommendation**: CAD-DEVELOPMENTS urgently needs an AGENTS.md. As the second most active repo with 296 skills and its own rules, it operates without a defined contract.

---

## 3. CLAUDE.md Freshness Analysis

### Unresolved Merge Conflicts (CRITICAL)

**6 repos have unresolved git merge conflict markers in CLAUDE.md**:

| Repo                       | CLAUDE.md Lines | Last Modified |
|----------------------------|-----------------|---------------|
| achantas-data              | 44              | 2026-03-26    |
| assethold                  | 746             | 2026-03-25    |
| hobbies                    | 752             | 2026-03-25    |
| investments                | 740             | 2026-03-26    |
| sabithaandkrishnaestates   | 740             | 2026-03-25    |
| teamresumes                | 740             | 2026-03-26    |

These files contain `<<<<<<< Updated upstream` markers, meaning Claude agents reading them get broken context with duplicate/conflicting instructions. The inflated line counts (740-752 lines vs normal 9-15 lines) are caused by the merge conflict including both upstream and local versions of the full file.

**Impact**: HIGH — These repos are giving agents malformed instructions, likely leading to inconsistent behavior.

### WRK References

| Repo                 | References WRK? | Staleness Risk |
|----------------------|-----------------|----------------|
| digitalmodel         | Yes             | MEDIUM — check if referenced WRKs are still open |
| assetutilities       | Yes             | MEDIUM |
| assethold            | Yes             | MEDIUM (also has merge conflict) |
| hobbies              | Yes             | LOW (personal repo, merge conflict masks content) |
| rock-oil-field       | Yes             | LOW (4 commits in 90d) |
| simpledigitalmarketing | Yes           | LOW (1 commit in 90d) |

### Repo Overrides

15 repos have "Repo Overrides" sections in CLAUDE.md. This is the expected pattern for pointer repos to customize behavior while inheriting the base contract.

### Missing CLAUDE.md

| Repo                  | Impact |
|-----------------------|--------|
| aceengineer-strategy  | LOW — private strategy repo |

---

## 4. Command Staleness Analysis

### Stale Command References (file paths that no longer exist)

**digitalmodel** (9 commands, 8 stale references):
- `analyze.md` → `scripts/bash/check-prerequisites.sh` — MISSING
- `clarify.md` → `scripts/bash/check-prerequisites.sh` — MISSING
- `constitution.md` → `docs/quickstart.md` — MISSING
- `implement.md` → `scripts/bash/check-prerequisites.sh` — MISSING
- `plan.md` → `scripts/bash/setup-plan.sh` — MISSING
- `specify.md` → `scripts/bash/create-new-feature.sh` — MISSING
- `tasks.md` → `scripts/bash/check-prerequisites.sh` — MISSING
- `today.md` → `scripts/productivity/daily_today.sh` — MISSING
- `today.md` → `scripts/productivity/daily-reflect-report.sh` — MISSING

**worldenergydata** (7 commands, 7 stale references):
- Same pattern as digitalmodel — references `scripts/bash/check-prerequisites.sh`, `scripts/bash/setup-plan.sh`, `scripts/bash/create-new-feature.sh`, `docs/quickstart.md`

**Finding**: digitalmodel and worldenergydata share the same command template with 15 broken file references. These commands were likely copied from an older scaffold that assumed a `scripts/bash/` structure that was never created or was removed.

### Duplicate Commands Across Repos

| Command        | Found In                                                    | Count |
|----------------|-------------------------------------------------------------|-------|
| `compound.md`  | assetutilities, assethold, sabithaandkrishnaestates, teamresumes, achantas-data, investments, sd-work, aceengineer-admin, client_projects, OGManufacturing, doris, frontierdeepwater, saipem, seanation | 14 |
| `today.md`     | workspace-hub, CAD-DEVELOPMENTS, digitalmodel               | 3     |
| `work.md`      | CAD-DEVELOPMENTS, digitalmodel                               | 2     |
| `analyze.md`   | digitalmodel, worldenergydata                                | 2     |
| `clarify.md`   | digitalmodel, worldenergydata                                | 2     |
| `constitution.md` | digitalmodel, worldenergydata                             | 2     |
| `implement.md` | digitalmodel, worldenergydata                                | 2     |
| `plan.md`      | digitalmodel, worldenergydata                                | 2     |
| `specify.md`   | digitalmodel, worldenergydata                                | 2     |
| `tasks.md`     | digitalmodel, worldenergydata                                | 2     |

**Finding**: `compound.md` is deployed in 14 repos — this is likely a standard scaffold command pushed via harness tooling. The digitalmodel/worldenergydata command set (analyze, clarify, constitution, implement, plan, specify, tasks) appears to be a shared template with stale references.

---

## 5. Skill Promotion Candidates

### From CAD-DEVELOPMENTS (296 skills)

CAD-DEVELOPMENTS has a near-complete copy of the workspace-hub skill tree. Categories: `_core`, `_internal`, `ai`, `business`, `coordination`, `data`, `development`, `engineering`, `operations`, `workspace-hub`.

**Domain-general skills that are candidates for promotion to workspace-hub** (not CAD-specific):

| Category          | Count | Examples                                      | Action |
|-------------------|-------|-----------------------------------------------|--------|
| ai/optimization   | 2     | model-selection, usage-optimization           | CHECK SYNC — may be duplicates of workspace-hub skills |
| ai/prompting      | 5     | agenta, dspy, langchain, pandasai, prompt-engineering | PROMOTE — pandasai and agenta are not in workspace-hub |
| business/*        | 15+   | calendly-api, slack-api, teams-api, etc.      | CHECK SYNC — most exist in workspace-hub |
| engineering/marine-offshore | 11 | fatigue-analysis, ship-dynamics-6dof, wave-theory | PROMOTE — fatigue-analysis, ship-dynamics-6dof, wave-theory not in workspace-hub |
| engineering/standards | 5  | api, astm, dnv, iso, norsok                   | CHECK SYNC — exist in workspace-hub |

**High-priority promotions from CAD-DEVELOPMENTS**:
1. `engineering/marine-offshore/fatigue-analysis` — domain-critical, not in workspace-hub
2. `engineering/marine-offshore/ship-dynamics-6dof` — domain-critical, not in workspace-hub
3. `engineering/marine-offshore/wave-theory` — domain-critical, not in workspace-hub
4. `ai/prompting/pandasai` — useful for data analysis across repos
5. `ai/prompting/agenta` — agent framework skill

### From worldenergydata (33 skills)

**Skills that could serve digitalmodel or broader ecosystem**:

| Skill                        | Reusable? | Why |
|------------------------------|-----------|-----|
| metocean-data-fetcher        | YES       | Already promoted to workspace-hub — check sync |
| metocean-statistics          | YES       | Already promoted to workspace-hub — check sync |
| metocean-visualizer          | YES       | Already promoted to workspace-hub — check sync |
| marine-safety-incidents      | YES       | Relevant for doris, seanation, OGManufacturing |
| economic-sensitivity-analyzer| YES       | Relevant for investments, client_projects |
| bsee-data-extractor          | PARTIAL   | US-specific but reusable pattern |
| sodir-data-extractor         | PARTIAL   | Norway-specific but reusable pattern |

**Finding**: 3 metocean skills appear in both worldenergydata and workspace-hub — need to verify they are in sync and that workspace-hub's versions are the canonical ones.

### From achantas-data (13 skills)

| Skill                     | Reusable? | Why |
|---------------------------|-----------|-----|
| guidelines/* (5 skills)   | YES       | Already promoted to workspace-hub — identical names |
| workflows/* (4 skills)    | YES       | codex-review, cross-review-policy, dev-workflow, gemini-review — already in workspace-hub |
| meta/session-start-routine| YES       | Already in workspace-hub |
| optimization/* (2 skills) | YES       | Already in workspace-hub |
| product/product-roadmap   | YES       | Already in workspace-hub |

**Finding**: achantas-data skills are 100% duplicates of workspace-hub skills. This repo should either use external_dirs referencing or have its skills removed to eliminate drift risk.

---

## 6. Repos Needing Attention (Prioritized)

### Priority 1: CRITICAL

| Repo                  | Issue                                         | Action |
|-----------------------|-----------------------------------------------|--------|
| assethold             | **TIER-1 with 0 skills, 746L CLAUDE.md with merge conflict** | Resolve merge conflict; add domain skills |
| CAD-DEVELOPMENTS      | **2nd most active repo (265 commits), MISSING AGENTS.md, 54 pending WQ items** | Create AGENTS.md; triage 54 pending work queue items |

### Priority 2: HIGH

| Repo                        | Issue                                              | Action |
|-----------------------------|----------------------------------------------------|---------| 
| aceengineer-website         | **111 commits but 0 skills, 0 commands, 0 docs**  | Add website-specific skills (SEO, deployment, etc.) |
| sabithaandkrishnaestates    | CLAUDE.md merge conflict (740L)                    | Resolve conflict |
| teamresumes                 | CLAUDE.md merge conflict (740L)                    | Resolve conflict |
| investments                 | CLAUDE.md merge conflict (740L)                    | Resolve conflict |
| hobbies                     | CLAUDE.md merge conflict (752L)                    | Resolve conflict |
| achantas-data               | CLAUDE.md merge conflict (44L); 13 duplicate skills | Resolve conflict; deduplicate skills |

### Priority 3: MEDIUM

| Repo                  | Issue                                              | Action |
|-----------------------|----------------------------------------------------|---------| 
| digitalmodel          | **TIER-1 with only 3 skills** despite 92 commits; 8 stale command references | Clean up commands; add engineering skills from CAD-DEVELOPMENTS |
| worldenergydata       | **TIER-1** with 7 stale command references         | Clean up commands |
| OGManufacturing       | has test_command in AGENTS.md but 0 test files in tests/ | Either add tests or remove test_command claim |
| aceengineer-strategy  | Missing both AGENTS.md and CLAUDE.md               | Add minimal pointer files |

### Priority 4: LOW

| Repo                  | Issue                                              |
|-----------------------|----------------------------------------------------|
| simpledigitalmarketing| 1 commit in 90d, no skills/commands — dormant      |
| rock-oil-field        | 4 commits, no skills — low activity                |
| seanation             | 4 commits, no skills — low activity                |
| frontierdeepwater     | 4 commits, no skills — low activity                |

---

## 7. Ecosystem Health Summary

### Strengths
1. **Consistent contract architecture**: 22 of 24 repos have AGENTS.md (standalone or pointer)
2. **Skill infrastructure**: 3,229 skills across ecosystem with clear categorization
3. **Work queue system**: Active in 3 repos with pending items being tracked
4. **Tier classification**: Clear tier-1/tier-2 distinction in harness config

### Weaknesses
1. **6 CLAUDE.md merge conflicts**: Broken agent context in 25% of repos
2. **15 stale command references**: digitalmodel and worldenergydata commands reference non-existent scripts
3. **Skill duplication**: CAD-DEVELOPMENTS has ~218 skills that overlap with workspace-hub; achantas-data has 13 pure duplicates
4. **Tier-1 gaps**: assethold has 0 skills; digitalmodel has only 3 skills
5. **CAD-DEVELOPMENTS governance gap**: 2nd most active repo with no AGENTS.md contract

### Key Metrics

| Metric                                | Value |
|---------------------------------------|-------|
| Total repos with .claude/             | 24    |
| Total skills across ecosystem         | 3,229 |
| Total commands across repos           | 32    |
| Repos with merge conflicts in CLAUDE.md | 6 (25%) |
| Stale command references              | 15    |
| Duplicate commands (compound.md)      | 14 repos |
| Tier-1 repos with full ecosystem      | 2 of 4 (digitalmodel, worldenergydata) |
| Repos missing AGENTS.md              | 2     |
| Skill promotion candidates           | 5 (from CAD-DEVELOPMENTS) |
| Duplicate skill sets to deduplicate   | 13 (achantas-data) |
| Work queue items pending              | 55 (54 in CAD-DEVELOPMENTS, 1 in workspace-hub) |

---

## Appendix: Raw Data

- Full repo scan: `phase-g-data/repo-scan.json` (24 repos, all fields)
