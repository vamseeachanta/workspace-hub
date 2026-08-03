#!/usr/bin/env bash
# surface-inventory.sh — deterministic work-surface inventory for one machine.
# Emits a machine-readable report to stdout. Read-only: never mutates anything.
SURFACE="${1:?usage: surface-inventory.sh <surface-dir>}"
cd "$SURFACE" 2>/dev/null || { echo "SURFACE_MISSING $SURFACE"; exit 0; }

echo "### HOST $(hostname)"
echo "### SURFACE $SURFACE"
echo "### FILESYSTEM"
df -hT . 2>/dev/null | tail -1
echo "### OTHER_VOLUMES"
df -hT -x tmpfs -x devtmpfs -x squashfs 2>/dev/null | awk 'NR==1 || $2 ~ /ext4|xfs|btrfs|fuseblk|zfs/'
echo "### LOOSE_FILES_TOPLEVEL"
find . -maxdepth 1 -type f -printf '%10s  %TY-%Tm-%Td  %f\n' 2>/dev/null | sort -k3
echo "### DIRECTORIES"
for n in $(ls -d */ 2>/dev/null | sed 's#/##'); do
  if [ -e "$n/.git" ]; then
    kind=$([ -f "$n/.git" ] && echo WORKTREE || echo CLONE)
    br=$(timeout 30 git -C "$n" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')
    origin=$(timeout 20 git -C "$n" remote get-url origin 2>/dev/null | sed 's#.*[/:]##;s#\.git$##')
    dirty=$(timeout 60 git -C "$n" status --porcelain 2>/dev/null | wc -l)
    ahead=$(timeout 30 git -C "$n" rev-list --count '@{u}..HEAD' 2>/dev/null || echo NO_UPSTREAM)
    behind=$(timeout 30 git -C "$n" rev-list --count 'HEAD..@{u}' 2>/dev/null || echo NO_UPSTREAM)
    stash=$(timeout 30 git -C "$n" stash list 2>/dev/null | wc -l)
    unmerged=$(timeout 60 git -C "$n" log --oneline origin/main..HEAD 2>/dev/null | wc -l)
    last=$(timeout 20 git -C "$n" log -1 --format=%cs 2>/dev/null)
    untracked_sz=$(timeout 90 git -C "$n" ls-files --others --exclude-standard 2>/dev/null | wc -l)
    echo "DIR $n kind=$kind origin=${origin:-NONE} branch=$br dirty=$dirty ahead=$ahead behind=$behind stash=$stash not_on_main=$unmerged untracked_files=$untracked_sz last_commit=$last"
  else
    cnt=$(ls -A "$n" 2>/dev/null | wc -l)
    newest=$(find "$n" -type f -printf '%TY-%Tm-%Td\n' 2>/dev/null | sort -r | head -1)
    echo "DIR $n kind=PLAIN entries=$cnt newest_file=${newest:-EMPTY}"
  fi
done
echo "### REGISTERED_WORKTREES"
for n in $(ls -d */ 2>/dev/null | sed 's#/##'); do
  [ -d "$n/.git" ] || continue
  timeout 30 git -C "$n" worktree list 2>/dev/null | tail -n +2 | sed "s#^#$n -> #"
done
echo "### END"
