---
name: mnt-analysis-cleanup
description: Survey, classify, and clean up `/mnt/local-analysis/` (or any sibling-to-workspace-hub directory holding orphan worktrees, codex-burn artifacts, agent log accumulations, and outer-clone duplicates) without losing useful code/work. Surfaces a tiered approval menu rather than baking decisions; defers all destructive ops until user confirms.
when_to_use: |
  - User asks to "clean up local-analysis", "free up disk", "remove stale repos", "what's still useful in /mnt/local-analysis"
  - After a Hermes codex-burn run completes (post-run artifact sweep)
  - Routinely (monthly or after disk pressure) to keep the workspace-hub sibling area lean
  - Whenever `df /mnt/local-analysis` crosses a warning threshold (configurable)
related_skills:
  - operations/devops/remote-desktop-headless-ubuntu (sibling operations skill)
  - workspace-hub/repo-sync (handles inner-clone freshness)
  - coordination/issue-planning-mode (when cleanup surfaces issues for #2666-style follow-up)
---

# `/mnt/local-analysis/` cleanup

A reusable routine for the dirty work that accumulates alongside `workspace-hub/`: orphan worktrees from completed Hermes codex-burn runs, outer-clone duplicates of nested repos, monitoring evidence from past audit passes, and agent log accumulations.

## Iron Law: NEVER skip the verification step

The single most-load-bearing rule. Before deleting anything that looks like a repo clone or worktree:

1. **Confirm content is on origin** — for git repos/worktrees, fetch the relevant branch and `diff -rq` the working tree against the branch tip. Filter derived artifacts (`__pycache__`, `.venv`, `node_modules`, `egg-info`, `.benchmarks`, `test_output`, `results/Data`, `results/Plot`, `logs/`, `.hypothesis`, `.ruff_cache`).
2. **Archive non-derived unique content** — any item flagged unique-to-bundle that's NOT a derived artifact (especially SQLite DBs, downloaded data caches, hand-edited files) goes into the cleanup tarball before delete.
3. **No `rm -rf` until** the diff is clean OR the diff residue is captured in the archive.

Reason for the law: it's how you honor "don't lose useful code/work" in a deletion-heavy routine. See `references/case-study-2026-05-12.md` for the worked example.

## Skill structure (numbered steps)

### 1. Survey

```bash
ls -la /mnt/local-analysis/
for d in /mnt/local-analysis/*/; do timeout 20 du -sh "$d" 2>/dev/null; done
df -h /mnt/local-analysis
```

Capture: top-level entries, sizes, last-modified dates, mount usage %.

### 2. Classify each entry

Use this taxonomy (apply order matters — most-specific first):

| Class | Signal | Example |
|---|---|---|
| **system** | dotfile, pnpm/.cargo/.npm cache, XDG `.Trash-*` | `.pnpm-store/`, `.Trash-1000/` |
| **workspace-hub canonical** | the workspace-hub repo itself | `workspace-hub/` |
| **outer-clone duplicate** | a repo dir at top-level that also exists nested under `workspace-hub/<same-name>/` | `assetutilities/`, `digitalmodel/`, `worldenergydata/`, `llm-wiki/` (historical pattern, see references) |
| **orphan worktree** | `.git` is a file pointing at a path that no longer exists | `codex-burn-YYYYMMDD/<repo>-bundle/` after parent clone is gone |
| **codex-burn run artifact** | dated dir matching `codex-burn-YYYYMMDD/` containing per-repo bundles, monitoring-evidence, logs, prompts | full Hermes codex-burn run output |
| **agent log accumulation** | dir holding `provider-capacity-aware-YYYYMMDD-*` or `workspace-hub-{exit,closeout}-handoff-*.md` | `agent-logs/` |
| **empty coordination meta-dir** | dir created for an agent run that left no artifacts | `agent-worktrees/`, `worktrees/` |

### 3. Per-class verification

| Class | Verification |
|---|---|
| outer-clone duplicate | Compare HEAD of outer vs nested. Check `for-each-ref refs/heads/ --format='%(upstream:track)'` for unpushed work. Check `git stash list`. Check `git status --short` for dirty. |
| orphan worktree | Read `.git` (it's a file, contents = `gitdir: <path>`). If that path doesn't exist, orphan confirmed. Then fetch the branch the orphan was tracking into a sibling clone, archive its content, run the diff. |
| codex-burn run artifact | Cross-check with Hermes' active state — `pgrep -af hermes`, `hermes cron list`, `~/.hermes/goals/*.json` for recent goals naming the dated dir. If no active reference, the dir is post-run vestigial. |
| agent log accumulation | Inspect timestamps; threshold for prune is the `mtime` policy below. |
| empty coordination meta-dir | If genuinely empty (`find <dir> -maxdepth 2 -mindepth 1 | head -1` returns nothing), safe to remove. |

### 4. Risk-tier the proposal

Always present three tiers; let the user reject any.

- **Tier 0 — safe deletes**: orphan worktrees with verified-clean origin-diff, empty coordination meta-dirs, system trash if user opts in.
- **Tier 1 — archive then delete**: monitoring evidence, codex-burn prompts/logs that may be useful as audit reference or as skill-authoring fodder. Archive target: `workspace-hub/docs/sessions/archives/YYYY-MM-DD-<topic>.tar.gz`.
- **Tier 2 — reduce in place**: agent-logs with mtime policy (default: prune subdirs >14 days, keep standalone .md handoffs).
- **Tier 3 — leave alone**: outer-clone duplicates with any unpushed/dirty/stashed state, anything still actively referenced by Hermes/cron/scripts.

### 5. Present to user via `AskUserQuestion`

One question per tier (so user can reject independently). Always include "show me the diffs first" as an option for the tiers that delete content. Never auto-execute without per-tier approval.

### 6. Execute approved actions

In this order (most-reversible first):
1. Archive (creates `.tar.gz`)
2. Verify archive integrity (`tar tzf <archive> | wc -l`)
3. Delete sources
4. Prune in-place
5. Verify final state (`df -h`, `ls /mnt/local-analysis/`)

### 7. Handoff documentation

Write `workspace-hub/docs/sessions/YYYY-MM-DD-local-analysis-cleanup.md` capturing:
- before/after disk usage
- table of entries acted on, with class + verdict
- archive path and what it contains
- items deferred (and why)
- any follow-up GitHub issues filed

Commit the handoff. If an archive was created, also commit it (or note that it's gitignored — `docs/sessions/archives/` is currently not gitignored; if archives grow large enough that committing them is wrong, propose gitignoring the dir).

## Hermes coordination

The Hermes agent runs `~/.hermes/skills/autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md` which uses `/mnt/local-analysis/codex-burn-YYYYMMDD/` as its lane root. Important:

- Hermes creates a **fresh dated dir per run** — it does NOT poll old dated dirs.
- Old `codex-burn-YYYYMMDD/` dirs are therefore post-run vestigial.
- Always check `pgrep -af hermes` before deletion to confirm no in-flight burn run is using a dated dir.
- If a burn is in flight against TODAY's dated dir, do NOT touch it — defer that one.

To "talk to" Hermes from this skill: use `hermes status`, `hermes cron list`, `hermes sessions list` to read state. Don't try to write to Hermes' state.

## Disk-pressure trigger

If invoked autonomously (e.g. from a cron health check), gate execution on `df -h /mnt/local-analysis | awk '/sdc1|local-analysis/ {gsub("%",""); print $5}'` exceeding a threshold (default 75%). Below that, defer.

## What NOT to clean

- Anything under `workspace-hub/` itself — that's a different skill (per-repo housekeeping)
- `.pnpm-store/`, `.cache/`, `.cargo/` and other system-managed package caches
- XDG `.Trash-*` (system-managed; user can empty via their file manager)
- Any path referenced by an active Hermes goal, cron job, or session
- Any orphan worktree whose origin-diff shows unique non-derived content NOT captured in the archive

## Memory hooks

When this skill completes a successful run, optionally update auto-memory at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`:
- `feedback_local_analysis_cleanup_routine.md` — if a new gotcha surfaced
- `project_local_analysis_state.md` — post-run state snapshot if useful for future sessions

The case-study reference (`references/case-study-2026-05-12.md`) captures the worked example that produced this skill.
