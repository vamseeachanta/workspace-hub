> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_plugin_cache_not_repo_tracked.md

---
name: Plugin-installed skills live outside the repo tree
description: `gsd:`, `sparc:`, `workflows:`, `agents:`, and other plugin families cannot be `git mv`d because they live under `~/.claude/plugins/cache/`, not `.claude/skills/` in the repo
type: feedback
originSessionId: f5aefbf6-482d-404e-84f9-d1ebc70e92a3
---
Skills fall into two disjoint populations that must NOT be conflated when planning archival/consolidation/rename work:

1. **Repo-tree skills** — live at `.claude/skills/<family>/<skill>/SKILL.md` inside the workspace-hub git tree. ~60+ top-level families (coordination, development, github, engineering, …). Managed via `git mv`, git-tracked archival to `.claude/skills/_archive/`, etc.
2. **Plugin-installed skills** — live at `~/.claude/plugins/cache/claude-plugins-official/<plugin-id>/<version>/<skill-path>/SKILL.md`. The `gsd:`, `sparc:`, `workflows:`, `agents:` prefixes you see in skill listings are plugin-owned. Not in the repo tree. `git mv` literally cannot operate on them.

**Why this matters:** #2321 v1 plan prescribed `git mv .claude/skills/<family>/<sibling>/ .claude/skills/_archive/...` for plugin families — this was DOA because the target paths don't exist in the repo. All 3 adversarial reviewers flagged the risk; empirical `find` confirmed it during implementation; issue was split (now #2358 + #2359).

**How to apply:** Before any plan that proposes moving/archiving skill families:
1. `find .claude/skills/<family>` — if empty, the family is plugin-installed; `git mv` cannot be the mechanism.
2. `ls ~/.claude/plugins/cache/claude-plugins-official/` — confirms which plugin bundles are installed.
3. For plugin-owned overlap, the remediation is **preference guidance** (which family to prefer for which purpose) and optionally **plugin enable/disable** — NOT file moves.
4. For repo-tree overlap, `git mv` works fine.

Context: #2321 (closed, split); children #2358 + #2359. Baseline for which skills exist at all: `docs/reports/skill-invocation-baseline-2026-04-17.md` (2921 total skills, both populations).
