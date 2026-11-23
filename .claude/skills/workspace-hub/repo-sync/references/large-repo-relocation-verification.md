# Large Repo Relocation Verification

Use this when moving very large local repo working copies between mounts (for example `/mnt/local-analysis/<repo>` to `/mnt/ace/<repo>`) where broad `git status` or filesystem scans may time out.

## Safe relocation pattern

1. Capture source identity before copying:
   - source path
   - destination path
   - source `HEAD`
   - source branch
   - source `origin`
2. If the destination already exists, preserve it with a timestamped sibling backup before overwriting:
   - Example: `/mnt/ace/<repo>.preexisting-before-repo-move-YYYYMMDD-HHMMSS`
3. Copy with `rsync -a --delete --info=stats2 "$src/" "$dst/"`.
4. Verify destination identity with lightweight commands before removing the source:
   - `git --git-dir="$dst/.git" --work-tree="$dst" rev-parse HEAD`
   - `git --git-dir="$dst/.git" --work-tree="$dst" branch --show-current`
   - `git --git-dir="$dst/.git" --work-tree="$dst" remote get-url origin`
5. Remove the source only if source and destination `HEAD` match exactly.
6. Preserve a log containing rsync stats, HEAD comparison, and source-removal marker.

## Avoid expensive checks during/soon after copy

For huge repos, avoid using these as the first verification step:

- broad `git status --porcelain -uall`
- full untracked scans
- recursive `du` or file inventory sweeps

Even `git status --untracked-files=no` can time out on cold or I/O-congested mounts. Treat a status timeout as an unconfirmed cleanliness caveat, not as move failure, if lightweight identity checks and copy logs are good.

## Minimal status probe

```bash
set -euo pipefail
src=/mnt/local-analysis/<repo>
dst=/mnt/ace/<repo>

printf 'source='; [ -e "$src" ] && echo exists || echo absent
printf 'dest='; [ -d "$dst/.git" ] && echo git || echo missing-or-not-git
printf 'head='; git --git-dir="$dst/.git" --work-tree="$dst" rev-parse --short HEAD
printf 'branch='; git --git-dir="$dst/.git" --work-tree="$dst" branch --show-current
printf 'origin='; git --git-dir="$dst/.git" --work-tree="$dst" remote get-url origin
```

## Reporting format

Report separately:

- known complete: process exited, source absent, destination exists, HEAD match, log completion marker
- preserved artifacts: timestamped destination backups
- caveats: `git status` cleanliness not confirmed if status timed out
- disk pressure: include `df -h` only when relevant to relocation risk
