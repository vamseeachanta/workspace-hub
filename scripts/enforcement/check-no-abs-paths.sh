#!/usr/bin/env bash
# check-no-abs-paths.sh — #2322
# Enforce the "no hardcoded absolute paths in scripts" rule
# from .claude/rules/coding-style.md.
#
# Usage:
#   scripts/enforcement/check-no-abs-paths.sh [--baseline=<file>] [--update-baseline] [<file-or-dir>...]
#
# With no positional args, scans all git-tracked `.sh` and `.py` files
# (excluding files under any `*/tests/fixtures/*` path) and uses the
# default baseline at `config/quality/no-abs-paths-baseline.txt`. With
# positional args, scans exactly those files/dirs, fixture-exclusion is
# off, and baseline is off unless --baseline is given explicitly.
#
# Ratchet behavior: the baseline file lists known-accepted violations as
# `<repo-relative-path>:<line>` entries. Matching violations are skipped,
# so only NEW offenses fail the check. Refresh the baseline with
# --update-baseline after cleanup work.
#
# Bypass: ALLOW_ABS_PATHS=1 (logs to stderr). Use sparingly.
#
# Detection: regex scan for /home/, /mnt/, /Users/, /opt/, and DOS-style
# drive letters. Level-2 regex check per the enforcement-gradient
# philosophy — AST upgrade is deferred debt.
#
# Allowlist (line-level): any line ending with "# abs-path-allowed" is
# ignored (Bash/Python comment style; placed as a trailing comment).

set -euo pipefail

# Anchor REPO_ROOT to the script's own location (not the caller's cwd) so that
# baseline keys are stable regardless of where the script is invoked from.
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/worktree-index.sh
source "$SELF_DIR/../lib/worktree-index.sh"
REPO_ROOT="$(worktree_git -C "$SELF_DIR" rev-parse --show-toplevel)"
DEFAULT_BASELINE="${REPO_ROOT}/config/quality/no-abs-paths-baseline.txt"

# ── Argument parsing ─────────────────────────────────────────────────────
BASELINE=""
BASELINE_EXPLICIT=0
UPDATE_BASELINE=0
# Git 2.43 git-ls-files / git-show: index and HEAD are distinct content states.
# Default: materialized tracked files, index fallback ONLY for skip-worktree.
# --staged: effective index blobs; --head: committed blobs. Positional paths
# retain the legacy filesystem authority and cannot be mixed with blob modes.
CONTENT_MODE=worktree
declare -a POSITIONAL=()

while (( $# > 0 )); do
  case "$1" in
    --baseline=*)      BASELINE="${1#*=}"; BASELINE_EXPLICIT=1; shift ;;
    --baseline)        BASELINE="${2:?--baseline requires a path}"; BASELINE_EXPLICIT=1; shift 2 ;;
    --staged)         CONTENT_MODE=index; shift ;;
    --head)           CONTENT_MODE=head; shift ;;
    --worktree)       CONTENT_MODE=worktree; shift ;;
    --update-baseline) UPDATE_BASELINE=1; shift ;;
    --no-baseline)     BASELINE=""; BASELINE_EXPLICIT=1; shift ;;
    --)                shift; POSITIONAL+=("$@"); break ;;
    -*)                echo "check-no-abs-paths: unknown flag: $1" >&2; exit 2 ;;
    *)                 POSITIONAL+=("$1"); shift ;;
  esac
done

# Default baseline applies only when no positional args are given.
if (( ${#POSITIONAL[@]} == 0 )) && (( BASELINE_EXPLICIT == 0 )); then
  BASELINE="$DEFAULT_BASELINE"
fi

# ── Collect the target file set ──────────────────────────────────────────
declare -a TARGETS=()
# Keep NUL bytes in a file, not command substitution, and check the producer.
# The caller controls TMPDIR; this file contains paths only and is disposable.
targets_file=$(mktemp)
trap 'rm -f -- "$targets_file"' EXIT
if (( ${#POSITIONAL[@]} == 0 )); then
  worktree_index_preflight "$REPO_ROOT" >&2
  unmerged=$(worktree_git -C "$REPO_ROOT" ls-files --unmerged) || exit 2
  if [[ -n $unmerged ]]; then
    echo 'check-no-abs-paths: unmerged index; content authority ambiguous' >&2
    exit 2
  fi
  if [[ $CONTENT_MODE == head ]]; then
    worktree_git -C "$REPO_ROOT" ls-tree -r -z --name-only HEAD > "$targets_file" || exit 2
  else
    worktree_git -C "$REPO_ROOT" ls-files --cached -z > "$targets_file" || exit 2
  fi
  while IFS= read -r -d '' f; do
    case "$f" in
      */tests/fixtures/*) continue ;;
      *.sh|*.py) TARGETS+=("$REPO_ROOT/$f") ;;
    esac
  done < "$targets_file"
else
  if [[ $CONTENT_MODE != worktree ]]; then
    echo 'check-no-abs-paths: positional paths require --worktree authority' >&2
    exit 2
  fi
  for arg in "${POSITIONAL[@]}"; do
    if [[ -d "$arg" ]]; then
      find "$arg" -type f \( -name '*.sh' -o -name '*.py' \) -print0 > "$targets_file" || exit 2
      while IFS= read -r -d '' f; do TARGETS+=("$f"); done < "$targets_file"
    elif [[ -f "$arg" ]]; then
      TARGETS+=("$arg")
    else
      echo "check-no-abs-paths: path not found: $arg" >&2
      exit 2
    fi
  done
fi

# ── Load baseline (known-accepted violations) ────────────────────────────
declare -A BASELINE_SET=()
if [[ -n "$BASELINE" && -f "$BASELINE" ]]; then
  while IFS= read -r entry; do
    # Skip comments + blanks.
    [[ -z "$entry" || "$entry" == \#* ]] && continue
    BASELINE_SET["$entry"]=1
  done < "$BASELINE"
fi

# Convert an absolute or relative path to repo-relative (best effort).
to_repo_relative() {
  local p="$1"
  local real
  real="$(realpath -m --relative-to="$REPO_ROOT" "$p" 2>/dev/null || echo "$p")"
  echo "$real"
}

# ── Scan ────────────────────────────────────────────────────────────────
PATTERN='(/home/|/mnt/|/Users/|/opt/|[A-Z]:[\\/])'

declare -a NEW_VIOLATIONS=()
declare -a ALL_VIOLATIONS=()

scanned=0
fallback=0
for file in "${TARGETS[@]}"; do
  if [[ $file == "$REPO_ROOT/"* ]]; then
    rel=${file#"$REPO_ROOT/"}
  else
    rel="$(to_repo_relative "$file")"
  fi
  authority=$CONTENT_MODE
  if (( ${#POSITIONAL[@]} == 0 )) && [[ $authority == worktree && ! -f $file ]]; then
    tag=$(worktree_git -C "$REPO_ROOT" ls-files -t -- ":(literal)$rel")
    if [[ $tag == 'S '* ]]; then
      authority=index
      fallback=$((fallback + 1))
    else
      printf 'check-no-abs-paths: missing materialized target: %q\n' "$rel" >&2
      exit 2
    fi
  fi
  case "$authority" in
    worktree) content=$(cat -- "$file") || exit 2 ;;
    index) content=$(worktree_git -C "$REPO_ROOT" show ":$rel") || exit 2 ;;
    head) content=$(worktree_git -C "$REPO_ROOT" show "HEAD:$rel") || exit 2 ;;
  esac
  scanned=$((scanned + 1))
  line_no=0
  while IFS= read -r line; do
    line_no=$((line_no + 1))
    [[ "$line" == *'# abs-path-allowed' ]] && continue
    if [[ "$line" =~ $PATTERN ]]; then
      key="${rel}:${line_no}"
      ALL_VIOLATIONS+=("$key")
      # Known-baselined violations are skipped unless we're regenerating.
      if (( UPDATE_BASELINE == 0 )) && [[ -n "${BASELINE_SET[$key]:-}" ]]; then
        continue
      fi
      printf '%s:%d: %s\n' "$rel" "$line_no" "$line"
      NEW_VIOLATIONS+=("$key")
    fi
  done <<< "$content"
done
printf 'check-no-abs-paths: authority=%s enumerated=%s scanned=%s object-fallback=%s\n' \
  "$CONTENT_MODE" "${#TARGETS[@]}" "$scanned" "$fallback" >&2

# ── --update-baseline: regenerate and exit 0 ────────────────────────────
if (( UPDATE_BASELINE == 1 )); then
  target="${BASELINE:-$DEFAULT_BASELINE}"
  mkdir -p "$(dirname "$target")"
  {
    echo "# no-abs-paths-baseline — regenerated by scripts/enforcement/check-no-abs-paths.sh --update-baseline"
    echo "# Each line: <repo-relative-path>:<line>"
    echo "# Refresh after cleaning up absolute-path violations. See #2322."
    echo "#"
    echo "# Total entries: ${#ALL_VIOLATIONS[@]}"
    printf '%s\n' "${ALL_VIOLATIONS[@]}" | LC_ALL=C sort -u
  } > "$target"
  echo "check-no-abs-paths: wrote ${#ALL_VIOLATIONS[@]} baseline entries to $target" >&2
  exit 0
fi

# ── Exit based on NEW (non-baselined) violations ─────────────────────────
if (( ${#NEW_VIOLATIONS[@]} > 0 )); then
  if [[ "${ALLOW_ABS_PATHS:-0}" == "1" ]]; then
    echo "check-no-abs-paths: ${#NEW_VIOLATIONS[@]} new violation(s) found; ALLOW_ABS_PATHS=1 bypass in effect" >&2
    exit 0
  fi
  echo "" >&2
  echo "check-no-abs-paths: ${#NEW_VIOLATIONS[@]} NEW violation(s) (not in baseline)." >&2
  echo "  Use \$(git rev-parse --show-toplevel) / \${REPO_ROOT} instead of hardcoded paths." >&2
  echo "  Trailing '# abs-path-allowed' on a single line exempts that line." >&2
  echo "  Baseline: ${BASELINE:-<none>}" >&2
  echo "  Refresh baseline with: scripts/enforcement/check-no-abs-paths.sh --update-baseline" >&2
  echo "  One-shot bypass (logged): ALLOW_ABS_PATHS=1 ..." >&2
  exit 1
fi
exit 0
