# 2026-05-07 — Nest llm-wiki + kaggle-rogii-2026 into workspace-hub

## What changed

Two repos that lived as siblings to workspace-hub were moved into it as nested independent git repos:

| Repo | Old path | New path | HEAD preserved |
|---|---|---|---|
| llm-wiki | `/mnt/local-analysis/llm-wiki` | `/mnt/local-analysis/workspace-hub/llm-wiki` | `d4f1d8c1` |
| kaggle-rogii-2026 | `/mnt/local-analysis/kaggle-rogii-2026` | `/mnt/local-analysis/workspace-hub/kaggle-rogii-2026` | `a406c94` |

Each retains its own `.git`, its own remote (`vamseeachanta/llm-wiki`, `vamseeachanta/kaggle-rogii-2026`), and its own license/ToS posture.

## Why

User-directed pivot from the 2026-05-05 spinout decision (#2398). Driver: navigation/experience consistency across all locally-edited repos. The structural objections that motivated keeping them as siblings (license contamination, ToS exposure, CLAUDE.md context leak) turned out to be conditional on layout assumptions that don't hold when:

- Each repo has its own `LICENSE` file (license travels with the repo, not the directory).
- The data is already gitignored (Kaggle dataset never enters git history regardless of disk location).
- The agent-context boundary is enforced by per-repo `.claude/` directory presence, not by file-system distance.

In short: **the firewall is per-repo metadata, not directory location.** Once that was clear, the migration cost (15 min, 22 commits to relocate) was much smaller than the consistency benefit.

## Firewall installed per nested repo

Each nested repo received:

1. **`CLAUDE.md`** at repo root (committed) — documents license/ToS boundary and instructs agents not to inherit workspace-hub private state.
2. **`.claude/memory/MEMORY.md`** (gitignored) — its presence scopes the Claude Code memory namespace to the nested-repo path, preventing inheritance of workspace-hub's private project memory.
3. **`.claude/` entry in repo's own `.gitignore`** — keeps the firewall local-only so external contributors who clone the public repo don't inherit hub-specific tooling.

Workspace-hub's root `.gitignore` got `/llm-wiki/` and `/kaggle-rogii-2026/` so they don't appear as untracked from the hub.

## Files modified (committed in `aac73e11a`, pushed to origin)

- `.gitignore` (+5 lines)
- `config/agents/claude/memory-snapshots/MEMORY.md` (kaggle path reference updated)
- `config/agents/claude/memory-snapshots/project_kaggle_rogii_2026.md` (kaggle path reference updated)
- (Plus 2 unrelated `.claude/state/corrections/` files that Hermes bundled into the same auto-sync commit)

## Memory updates (live + snapshot)

- `MEMORY.md` index — kaggle entry path updated.
- `project_kaggle_rogii_2026.md` — local path updated, firewall noted.
- `project_llm_wiki_spunout.md` — added "Layout amendment 2026-05-07" footer noting nested location while preserving the architectural-spinout language.

## Verification still owed (user, fresh session)

The one thing I cannot verify from inside this session: whether Claude Code's path-walk actually stops at the nested `.claude/` directory and uses a separate memory namespace, or whether it walks past and unifies them. This is a harness-implementation detail.

**Cheap check:** open a fresh Claude session inside `workspace-hub/llm-wiki/` and ask "what private project memory do you have access to?"

- ✅ If it references only the nested repo's MEMORY.md → firewall holds, migration is safe.
- ❌ If it references workspace-hub recruiter notes / tax data / hub-internal project state → firewall didn't scope, fallback needed.

**Fallback if firewall doesn't hold:** reverse `mv` (15 min) restores siblings; revert this session's commits in workspace-hub; restore old paths in memory snapshots. Cost is symmetric to the migration itself.

## Resume from here

If a future session needs to revisit:

1. Check `feedback_per_repo_metadata_is_firewall.md` for the placement-decision rule.
2. Read this doc for the migration recipe (in case other sibling repos need similar treatment).
3. The reverse-migration recipe is the same as the forward, with `mv` directions flipped and snapshot edits reverted.

## Open question logged for follow-up

If the firewall-verification check (above) reveals that nested `.claude/` does NOT scope memory, file an issue documenting the harness behavior and reverse the migration. If it does scope correctly, this becomes a portable pattern for any future "public OSS or external-ecosystem repo we want adjacent for navigation" cases.
