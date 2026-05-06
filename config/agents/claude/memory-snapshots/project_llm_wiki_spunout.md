---
name: llm-wiki spun out to dedicated public repo (override of #2398)
description: 2026-05-05 user-directive override moved knowledge/wikis tree to vamseeachanta/llm-wiki. Pipeline stays in workspace-hub.
type: project
originSessionId: eeda8a41-16c1-49a7-a086-2a0f25db1b88
---
llm-wiki content lives at https://github.com/vamseeachanta/llm-wiki (public, MIT + CC-BY-4.0).

**Why:** User directive overrode the 2026-04-23 stay-embedded decision (workspace-hub#2398) despite no triggers having fired. Operative reason recorded in workspace-hub#2398 comment 4383474579.

**Architectural model:** workspace-hub continues to play orchestration / tooling-hub role for sibling repos. The llm-wiki repo is the artifact / storehouse — consumed by workspace-hub's pipeline, not run by it.

**Stays in workspace-hub:**
- `scripts/data/llm-wiki/` (corpus extraction pipeline)
- `scripts/knowledge/` (helpers, conformance checks, cron)
- `.claude/skills/research/llm-wiki/`, `.claude/skills/coordination/llm-wiki-roadmap-integration/`
- `.claude/state/llm-wiki-completeness-loop/`
- `data/document-index/` (derived index)
- `knowledge/wikis/health-reports/` and `knowledge/wikis/personal/` (workspace-hub-internal)

**Moved to llm-wiki repo:**
- 8 domain wikis: acma-projects, asset-management, engineering, engineering-standards, lng-projects, marine-engineering, maritime-law, naval-architecture
- `knowledge/wikis/cross-links.md`
- `knowledge/seeds/` (mooring failures + 6 files)
- `tests/fixtures/llm-wiki/` data fixtures

**Vendor-derivative PDFs:** archived to `/mnt/ace/llm-wiki-archive/marine-engineering/raw/papers/` (5 PDFs, 29 MB). NOT in any git repo. `.gitignore` rules in both workspace-hub and llm-wiki block re-commit.

**How to apply:**
- New wiki content goes to llm-wiki repo, not workspace-hub
- workspace-hub Python files referencing `knowledge/wikis/` paths are tracked for cleanup in workspace-hub#2650
- Heads-up issue for parallel sessions: workspace-hub#2647
- 12 WRK extraction issues now live at llm-wiki#1-#12
- 9 mis-filed worldenergydata issues re-routed: #144-#150 (digitalmodel), #147 (OGManufacturing), #208 (saipem), #152 (frontierdeepwater)
- Iron Law on `commit --no-verify` still holds; cleanup PR (workspace-hub#2649) used `push --no-verify` per `feedback_pre_push_hook_no_verify_for_preservation.md` precedent

**Supersedes:** `project_llm_wiki_stays_embedded.md` (delete after Step 7 confirmation).
