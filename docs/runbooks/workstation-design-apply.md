# Apply the workstation design to another machine

The design was set on 2026-10-07/08 after one workstation's system drive filled. It consists of:

| Part | Where it lives |
|---|---|
| Worktrees not clones; cleanup once work is on origin; bulk output to `/mnt/ace` with manifest and second copy; session coordination; blocked actions to the owner | [`.claude/rules/workstation-hygiene.md`](../../.claude/rules/workstation-hygiene.md) |
| Report-first cleanup script | [`scripts/operations/workstation-hygiene.sh`](../../scripts/operations/workstation-hygiene.sh) |
| Codex follows the same rule | `config/agents/codex/SOUL.delta.md` item 5 (built into the Codex runtime) |
| Owner decisions on local HTML boards | [`.claude/rules/human-decision-boards.md`](../../.claude/rules/human-decision-boards.md) |
| Merge authority and cleanup after merge | [`merge-authorization.md`](../../.claude/rules/merge-authorization.md), [`merge-cleanup.md`](../../.claude/rules/merge-cleanup.md) |

## Prompt

Paste this into a Claude Code session on the target machine, started in the workspace root
(the folder that holds `workspace-hub` and its sibling repositories).

```text
Apply the workstation design from workspace-hub to this machine. Report first; change nothing
the design marks as owner-only.

1. In workspace-hub: `git fetch --prune` and fast-forward main (ff-only; if the checkout is dirty
   or diverged, stop and report). Read .claude/rules/workstation-hygiene.md,
   human-decision-boards.md, merge-authorization.md and merge-cleanup.md, and
   docs/runbooks/workstation-design-apply.md.
2. Check the agent runtimes this machine loads match origin:
   `bash scripts/enforcement/check-soul-deployment-drift.sh`. If a runtime is stale and its
   install is in scope, refresh it with `scripts/agents/install-soul-runtime.sh` and re-check.
   Report anything you could not refresh.
3. Run `bash scripts/operations/workstation-hygiene.sh --root <workspace root> --sizes` and show
   the report: disk free, duplicate clones, linked worktrees (SAFE / DIRTY / UNPUSHED / LOCKED)
   and cache sizes.
4. If free space is below ~10 % of the drive, or any SAFE duplicate clone exists, run it again
   with `--apply` (add `--caches` if npm/uv/pip caches exceed a few GB). --apply only removes
   SAFE items under the root. Removing a SAFE duplicate clone also removes its gitignored files.
   Never delete DIRTY, UNPUSHED or LOCKED items, and never touch folders owned by a running app
   (Codex app task folders stay report-only).
5. Look for bulky regenerable output tracked in Git or staged in open PRs (per-case solver
   results, hundreds of MB). Do not move it yourself; list it for the owner with size and repo.
6. List live peer Claude sessions on this machine and tell them which items you are taking.
7. Put every owner decision (DIRTY/UNPUSHED worktrees to keep, push or discard; bulk output to
   move to /mnt/ace; any action the permission classifier refused, with its exact command) on a
   local HTML decision board per human-decision-boards.md, with your recommendation marked.
   Open it and name it in chat. Do not ask in chat.
8. Finish with a short report: disk before/after, what was removed, what is on the board,
   runtime drift status.
```

## Claude permission rules (owner-run)

Agents cannot change permission settings on any machine, locally or over SSH; the
classifier refuses it as self-modification. The owner makes two moves:

1. Edit the canonical `config/agents/claude/settings.json` on main: rules belong under
   `permissions.allow` / `permissions.deny` (a top-level `deny` key is not read by Claude Code).
2. Roll it out from one machine with
   `scripts/operations/rollout-claude-permissions.sh [--apply] <alias>:<hub path> ...`
   (`local:<hub path>` for the current machine). It fetches origin, reads the canonical file
   without touching the checkout, and sets each machine's allow and deny lists to the union
   of its own rules and the canonical ones, with a timestamped backup. Default is a dry run;
   `--ref <branch>` previews an unmerged change. Agents may run the dry run.

`scripts/_core/sync-agent-configs.sh` is not used for this: its jq merge replaces whole
arrays (dropping machine-specific rules) and it deploys whatever the local checkout holds,
which is stale or diverged on several hosts.

## What not to expect

- The permission rules that let agents merge through `merge-when-clean.sh` or run `codex exec`
  are per-machine user settings and stay owner-only. The prompt puts them on the board.
- Removing a worktree does not shrink a repository's history; files moved to `/mnt/ace` remain
  in commits made before the move.
