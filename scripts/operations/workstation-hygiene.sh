#!/usr/bin/env bash
# workstation-hygiene.sh — report (default) or remove disk residue that agents leave behind.
# Rule: .claude/rules/workstation-hygiene.md
#
# Usage:
#   workstation-hygiene.sh [--root DIR] [--sizes] [--apply] [--caches]
#     --root DIR  workspace root holding the sibling repos (default: parent of this repo)
#     --sizes     measure directory sizes (slow on large trees)
#     --apply     remove SAFE worktrees and SAFE duplicate clones (never dirty or unpushed ones)
#     --caches    with --apply: also prune npm/uv/pip caches
#
# SAFE = no tracked changes, no untracked files except caches (__pycache__, .pytest_cache,
# .ruff_cache, .mypy_cache), no stashes of its own (clones), and HEAD contained in an origin ref
# or equal to the head of a merged PR (squash merge, branch deleted). Removing a SAFE clone also
# removes its gitignored files. --apply removes worktrees only under --root; those elsewhere (for
# example app task folders) stay report-only. A worktree with a running process inside it (Linux)
# is IN USE and never removed; long jobs should also `git worktree lock --reason <job>` so LOCKED
# protects them on every platform.
# Exit 0 always in report mode; non-zero only on usage errors.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SIZES=0; APPLY=0; CACHES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --sizes) SIZES=1; shift ;;
    --apply) APPLY=1; shift ;;
    --caches) CACHES=1; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

CACHE_STATUS_IGNORE_RE='^\?\? (.*/)?(__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache)/$'
size_of() { [ "$SIZES" = 1 ] && du -sh "$1" 2>/dev/null | cut -f1 || echo "-"; }

# Prints "IN USE" if a process has its working directory inside $1 (Linux /proc only).
in_use() {
  local p
  [ -d /proc/self/cwd ] || return 1
  for p in /proc/[0-9]*/cwd; do
    case "$(readlink "$p" 2>/dev/null)" in "$1"|"$1"/*) return 0 ;; esac
  done
  return 1
}

# Returns 0 when the commit is on origin/* or is the head of a merged PR.
commit_is_published_or_merged() {
  local d="$1" branch="$2" commit="$3" url merged
  if git -C "$d" branch -r --contains "$commit" --format='%(refname:short)' 2>/dev/null | grep -q '^origin/'; then
    return 0
  fi

  # Squash-merged and branch deleted: the local branch tip is the head of a merged PR.
  url=$(git -C "$d" remote get-url origin 2>/dev/null)
  if [ -n "$branch" ] && [ -n "$url" ] && command -v gh >/dev/null; then
    merged=$(gh pr list -R "$url" --head "$branch" --state merged --json headRefOid \
      --jq ".[] | select(.headRefOid==\"$commit\") | .headRefOid" 2>/dev/null | head -1)
    [ -n "$merged" ] && return 0
  fi
  return 1
}

# Prints "SAFE" or a reason it is not safe.
assess() {
  local d="$1" mode="${2:-head}" dirty head branch ref_branch ref_commit
  in_use "$d" && { echo "IN USE: a running process has its cwd here"; return; }
  dirty=$(git -C "$d" status --porcelain 2>/dev/null | grep -Ev "$CACHE_STATUS_IGNORE_RE" | head -3)
  [ -n "$dirty" ] && { echo "DIRTY: $(echo "$dirty" | tr '\n' ' ')"; return; }
  git -C "$d" fetch -q --prune origin || { echo "UNVERIFIED: fetch failed"; return; }

  if [ "$mode" = "all-branches" ]; then
    head=$(git -C "$d" rev-parse HEAD)
    branch=$(git -C "$d" symbolic-ref -q --short HEAD)
    if ! commit_is_published_or_merged "$d" "$branch" "$head"; then
      echo "UNPUSHED: HEAD $head"
      return
    fi
    while read -r ref_branch ref_commit; do
      [ -n "$ref_branch" ] || continue
      if ! commit_is_published_or_merged "$d" "$ref_branch" "$ref_commit"; then
        echo "UNPUSHED BRANCH: $ref_branch ${ref_commit:0:9} not on origin and not a merged PR head"
        return
      fi
    done < <(git -C "$d" for-each-ref --format='%(refname:short) %(objectname)' refs/heads)
    echo SAFE
    return
  fi

  head=$(git -C "$d" rev-parse HEAD)
  branch=$(git -C "$d" symbolic-ref -q --short HEAD)
  commit_is_published_or_merged "$d" "$branch" "$head" && { echo SAFE; return; }
  echo "UNPUSHED: HEAD ${head:0:9}${branch:+ ($branch)} not on origin and not a merged PR head"
}

echo "== Disk"
df -h "$ROOT" 2>/dev/null | tail -1

echo "== Duplicate clones (same origin as another checkout under $ROOT)"
declare -A first
for d in "$ROOT"/*/; do
  d="${d%/}"; [ -d "$d/.git" ] || continue          # worktrees have a .git file, clones a dir
  url=$(git -C "$d" remote get-url origin 2>/dev/null) || continue
  name=$(basename "${url%.git}")
  if [ "$(basename "$d")" = "$name" ]; then first[$url]="$d"; fi
done
for d in "$ROOT"/*/; do
  d="${d%/}"; [ -d "$d/.git" ] || continue
  url=$(git -C "$d" remote get-url origin 2>/dev/null) || continue
  [ "${first[$url]:-}" = "" ] || [ "${first[$url]}" = "$d" ] && continue
  if [ "$(git -C "$d" worktree list --porcelain 2>/dev/null | grep -c '^worktree ')" -gt 1 ]; then
    v="HAS WORKTREES"
  elif [ -n "$(git -C "$d" stash list 2>/dev/null)" ]; then
    v="HAS STASHES"
  else
    v=$(assess "$d" all-branches)
  fi
  printf '%-8s %-60s %s\n' "$(size_of "$d")" "$d" "$v"
  if [ "$APPLY" = 1 ] && [[ "$v" == SAFE* ]]; then rm -rf -- "$d" && echo "  removed"; fi
done

echo "== Linked worktrees"
for repo in "$ROOT"/*/; do
  repo="${repo%/}"; [ -d "$repo/.git" ] || continue
  git -C "$repo" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0,10)}' | tail -n +2 |
  while read -r wt; do
    [ -d "$wt" ] || { echo "  (missing) $wt"; continue; }
    if git -C "$repo" worktree list --porcelain | grep -A3 "^worktree $wt\$" | grep -q '^locked'; then
      echo "  LOCKED   $wt"; continue
    fi
    v=$(assess "$wt")
    printf '%-8s %-60s %s\n' "$(size_of "$wt")" "$wt" "$v"
    if [ "$APPLY" = 1 ] && [[ "$v" == SAFE* ]]; then
      rootw=$(cd "$ROOT" && pwd -W 2>/dev/null || pwd)
      case "$wt" in "$ROOT"/*|"$rootw"/*) ;; *) echo "  outside root: report only (an app may own it)"; continue ;; esac
      git -C "$repo" worktree remove --force "$wt" && echo "  removed"
    fi
  done
  [ "$APPLY" = 1 ] && git -C "$repo" worktree prune
done

echo "== Caches"
for c in "${LOCALAPPDATA:-$HOME/.cache}/npm-cache" "$HOME/.npm/_cacache" \
         "${LOCALAPPDATA:-$HOME/.cache}/uv" "$HOME/.cache/uv" "${LOCALAPPDATA:-$HOME/.cache}/pip"; do
  [ -d "$c" ] && printf '%-8s %s\n' "$(size_of "$c")" "$c"
done
if [ "$APPLY" = 1 ] && [ "$CACHES" = 1 ]; then
  command -v npm >/dev/null && npm cache clean --force >/dev/null 2>&1 && echo "  npm cache cleaned"
  command -v uv  >/dev/null && uv cache prune >/dev/null 2>&1 && echo "  uv cache pruned"
  command -v pip >/dev/null && pip cache purge >/dev/null 2>&1 && echo "  pip cache purged"
fi

[ "$APPLY" = 1 ] && { echo "== Disk after"; df -h "$ROOT" 2>/dev/null | tail -1; }
exit 0
