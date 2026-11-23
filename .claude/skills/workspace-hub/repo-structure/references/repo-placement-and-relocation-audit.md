# Repo Placement and Relocation Audit

Use when tier-1 or related repos are found nested under another repo (for example `/mnt/local-analysis/workspace-hub/<repo>`) or when deciding which machine should host which tier-1 checkout.

## Durable lesson

Repo placement changes are not just filesystem moves. They update the assumptions that future GitHub issues, scorecards, scripts, and handoffs will encode. After relocation, audit stale path references before drafting follow-on machine-placement or repo-distribution issues.

## Safe workflow

1. **Classify before moving**
   - Confirm each candidate is a real git checkout (`.git` present or gitfile worktree pointer).
   - Identify whether a sibling checkout already exists.
   - Record branch/ahead-behind/dirty state where practical.
   - Treat dirty/untracked state as data to preserve, not clutter to clean.

2. **Move intact, not piecemeal**
   - Prefer moving the whole checkout to the intended sibling location.
   - Do not rewrite history, delete untracked files, or normalize branches during placement cleanup.
   - If a repo is huge and status walks time out, preserve the checkout intact and mark status as unknown instead of forcing cleanup.

3. **Preserve existing destinations and resume safely**
   - If the intended destination already exists, never overwrite it blindly. Move or rename the preexisting destination to a timestamped preservation path first (for example `<dest>.preexisting-before-repo-move-YYYYMMDD-HHMMSS`).
   - For large checkouts, use a resumable verified-copy pattern rather than a single fragile `mv`: `rsync -a --delete --info=stats2 <source>/ <dest>/`, then verify git identity before removing the source.
   - If copy/resume work is slow because multiple rsync jobs are sharing a mount, report it as I/O contention and keep the process observable; do not infer failure from low CPU or long elapsed time alone.
   - Keep the source directory until destination verification passes. At minimum, compare source and destination `git rev-parse --short HEAD`; if HEAD differs or either repo is unreadable, stop and preserve both trees.

4. **Verify relocation**
   - For every repo: `nested=gone`, `sibling=git`.
   - Confirm no tracked/visible workspace-hub changes were introduced for the moved paths.
   - Re-run direct nested-git inventory under the parent repo; target count is zero for direct nested checkouts.

5. **Audit stale references before follow-on issues**
   - Search docs/scripts/scorecards/plans for old nested paths such as:
     - `/mnt/local-analysis/workspace-hub/<repo>`
     - `workspace-hub/<repo>`
   - Update or explicitly mark stale any artifacts that still assume nested layout.
   - Only then draft machine-placement issues, so their bodies do not encode obsolete paths.

## Issue-body guidance

For machine-placement decision issues, include:

- machine name and role (`ace-linux-1`, `ace-linux-2`, `licensed-win-1`, etc.);
- candidate tier-1 repos for that machine;
- data/license/hardware constraints;
- current verified checkout paths;
- explicit decision checklist for user approval.

Create one decision issue per machine when the user wants to decide distribution across machines. Keep the issue sequence aligned with the requested review order (for example `ace-linux-1` first, then `ace-linux-2`, then `licensed-win-1`, etc.) so each decision can be discussed and approved independently.

Do not combine relocation cleanup and machine-placement decisions in one issue unless the plan explicitly separates cleanup evidence from placement decision criteria.
