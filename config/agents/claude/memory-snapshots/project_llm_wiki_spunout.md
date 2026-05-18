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

**Layout amendment 2026-05-07:** Local-disk path changed from `/mnt/local-analysis/llm-wiki/` to `/mnt/local-analysis/workspace-hub/llm-wiki/` (nested for navigation consistency). Repo remains independently licensed (MIT + CC-BY-4.0), independently published to vamseeachanta/llm-wiki, with its own `.git`. Agent-context firewall: per-repo `.claude/` (gitignored, scopes Claude Code memory namespace away from workspace-hub private state) + per-repo `CLAUDE.md` documenting the boundary. The architectural spinout (separate license, separate publish target, separate governance) is unchanged — only the disk location moved.

**Ground-truth reconciliation 2026-05-18:** The 2026-05-07 amendment's stated consolidation was NOT executed for llm-wiki. As of 2026-05-18 (mid-session) BOTH paths coexisted intentionally:

- `/mnt/local-analysis/workspace-hub/llm-wiki/` — nested copy, used for umbrella-ecosystem queries and tracking nested-into-hub layout pattern; has its own `origin/main` tracking ref.
- `/mnt/local-analysis/llm-wiki/` — top-level standalone clone, **canonical worktree-spawn parent for Hermes reservoir-engineering wave work**. Session log evidence (`session_20260518.jsonl` at 2026-05-18 03:31 and 03:43) shows live Hermes lanes spawn `/tmp/llm-wiki-<wave-N>` worktrees via `cd /mnt/local-analysis/llm-wiki && git worktree add ...`.

**Resolution executed 2026-05-18 ~10:38 UTC (user directive: "sync and push to origin main. delete the outside"):**

- **Nested `workspace-hub/llm-wiki/` is now the sole canonical clone.** At `e7a25741 feat(graph): public-safe knowledge/link graph manifest tooling`, synced with origin/main.
- **Outside `/mnt/local-analysis/llm-wiki/` REMOVED** (~97 MB reclaim).
- **All outside-only WIP preserved** in `workspace-hub/_archive/`:
  - `llm-wiki-outside-stash-2026-05-18.patch` (22 MB) — outside's `stash@{0}` "graph artifacts 2026-05-18 pre-rebase"
  - `llm-wiki-outside-untracked-WIP-2026-05-18.tar.gz` (1 MB, 10 files) — outside's untracked tree: graph artifacts CSV/JSONL, summary.json, public-safe-knowledge-graph-report.md, public-graph-v1.md schema, AND the 3 py scripts that diverged substantively from nested's tracked HEAD versions (337+/521-, 243+/160-, 283+/177- line diffs vs. e7a25741). User judgment required to determine if outside's WIP scripts represent newer-than-committed iteration worth merging, OR older drafts superseded by e7a25741. The script-level patch is preserved verbatim in the tarball.
  - 3 truly-new untracked items (report, schema, graph artifacts) also copied to nested as untracked alongside the tarball for visibility.

**Known consequence — ACTIVELY BROKEN:** The Hermes wave-N worktree-spawn pattern `cd /mnt/local-analysis/llm-wiki && git worktree add /tmp/llm-wiki-<N> origin/main` WILL FAIL on next invocation (no such directory). The pattern must be migrated to `cd /mnt/local-analysis/workspace-hub/llm-wiki && git worktree add ...`. Search points: Hermes session config + any `whats-next` dispatch templates that hardcode the old path.
