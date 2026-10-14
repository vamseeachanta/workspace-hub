#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-start}"
id="${2:-}"
issue="${3:-none}"
config_path="${4:-${JOB_QUEUE_CONFIG:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/job-queue.local.conf}}"

die() { echo "$*" >&2; exit 2; }
case "$id" in ""|*[!a-z0-9-]*) die "bad job id";; esac
case "$issue" in none|*[!0-9]*) [ "$issue" = none ] || die "bad issue";; esac

read_config() {
  [ -f "$config_path" ] || die "configuration file not found"
  while IFS='=' read -r key value; do
    case "$key" in ""|\#*) continue;; esac
    case "$key" in
      QUEUE_ROOT|CLONE_ROOT|WORKTREE_ROOT|REPOSITORY_OWNER|DEFAULT_REPOSITORY|REPOSITORY_ALLOW_LIST|MIN_DISK_FREE_GB)
        eval "$key=\$value"
        ;;
    esac
  done < "$config_path"
  : "${QUEUE_ROOT:?missing QUEUE_ROOT}" "${CLONE_ROOT:?missing CLONE_ROOT}" "${WORKTREE_ROOT:?missing WORKTREE_ROOT}" "${DEFAULT_REPOSITORY:?missing DEFAULT_REPOSITORY}" "${REPOSITORY_ALLOW_LIST:?missing REPOSITORY_ALLOW_LIST}"
}

spec_head() {
  local key="$1" file="$QUEUE_ROOT/jobs/$id.md"
  [ -f "$file" ] || return 0
  head -n 10 "$file" | tr -d '\r' | sed -n "s/^$key:[[:space:]]*//p" | sed -e 's/[[:space:]]*$//' | head -n 1
}

repo_allowed() {
  local repo="$1" item
  IFS=',' read -r -a items <<< "$REPOSITORY_ALLOW_LIST"
  for item in "${items[@]}"; do [ "$(printf '%s' "$item" | xargs)" = "$repo" ] && return 0; done
  return 1
}

job_repo() {
  local repo
  repo="$(spec_head REPO)"
  [ -n "$repo" ] || repo="$DEFAULT_REPOSITORY"
  case "$repo" in *[!A-Za-z0-9._-]*|"") die "blocked: repository name is not allowed";; esac
  repo_allowed "$repo" || die "blocked: repository is not in the local allow list"
  printf '%s\n' "$repo"
}

worktree_path() {
  local repo="$1"
  printf '%s/%s-cxl-%s\n' "${WORKTREE_ROOT%/}" "$repo" "$id"
}

path_limit_check() {
  local root="$1" repo="$2" longest="$3" candidate branch_dir total
  branch_dir="$repo-cxl-$id"
  candidate="${root%/}/$branch_dir/$longest"
  total=${#candidate}
  if [ "$total" -ge 260 ]; then
    echo "blocked: worktree path length $total is at or above the 260 character limit"
    return 1
  fi
}

pending_refs_file() {
  local refs="$1" qid qissue spec
  : > "$refs"
  if [ -f "$QUEUE_ROOT/queue.txt" ]; then
    while read -r qid qissue _; do
      case "$qid" in ""|\#*) continue;; esac
      [ -f "$QUEUE_ROOT/logs/$qid.result" ] || printf '%s\n' "$qid" >> "$refs"
      spec="$QUEUE_ROOT/jobs/$qid.md"
      [ -f "$spec" ] && [ ! -f "$QUEUE_ROOT/logs/$qid.result" ] && cat "$spec" >> "$refs"
    done < "$QUEUE_ROOT/queue.txt"
  fi
}

named_in_refs() {
  local needle="$1" refs="$2"
  grep -Eq "(^|[^A-Za-z0-9._/-])$(printf '%s' "$needle" | sed 's/[.[\*^$/+?(){}|]/\\&/g')([^A-Za-z0-9._-]|\$)" "$refs"
}

ignored_kind_ok() {
  case "$1" in .venv|__pycache__|node_modules|.pytest_cache|.mypy_cache|.ruff_cache|build|dist|.uv-cache|uv.lock|*.egg-info) return 0;; esac
  return 1
}

append_keep() {
  local wt="$1" reason="$2" size="0"
  mkdir -p "$QUEUE_ROOT/logs"
  if [ -d "$wt" ]; then size=$(python - "$wt" <<'PY'
import os, sys
total = 0
for root, dirs, files in os.walk(sys.argv[1]):
    dirs[:] = [d for d in dirs if d != ".git"]
    for name in files:
        try:
            total += os.path.getsize(os.path.join(root, name))
        except OSError:
            pass
print(total)
PY
); fi
  printf '%s\t%s\t%s\t%s\n' "$id" "$wt" "$size" "$reason" >> "$QUEUE_ROOT/logs/kept-worktrees.tsv"
}

is_pushed() {
  local wt="$1" branch="$2" head remote
  head=$(git -C "$wt" rev-parse HEAD)
  remote=$(git -C "$wt" rev-parse -q --verify "refs/remotes/origin/$branch^{commit}" 2>/dev/null || true)
  [ -n "$remote" ] || remote=$(git -C "$wt" ls-remote origin "refs/heads/$branch" 2>/dev/null | cut -f1 | head -n 1)
  [ -n "$remote" ] || return 1
  [ "$remote" = "$head" ] && return 0
  git -C "$wt" merge-base --is-ancestor "$head" "$remote" 2>/dev/null
}

cleanup_worktree() {
  read_config
  local repo wt refs branch status ignored bad reason result clone err rc
  repo="$(job_repo)"
  wt="$(worktree_path "$repo")"
  result="$QUEUE_ROOT/logs/$id.result"
  refs="$QUEUE_ROOT/tmp-$id-pending-refs.txt"
  pending_refs_file "$refs"
  reason=""
  [ -f "$result" ] || reason="${reason}${reason:+; }job has no result line"
  [ -d "$wt" ] || reason="${reason}${reason:+; }worktree is absent"
  if [ -z "$reason" ]; then
    branch=$(git -C "$wt" symbolic-ref --short -q HEAD || true)
    [ -n "$branch" ] || reason="${reason}${reason:+; }worktree is detached"
    status=$(git --no-optional-locks -C "$wt" status --porcelain --untracked-files=all)
    [ -z "$status" ] || reason="${reason}${reason:+; }changed or untracked files"
    is_pushed "$wt" "$branch" || reason="${reason}${reason:+; }head is not on its remote branch"
    named_in_refs "$(basename "$wt")" "$refs" && reason="${reason}${reason:+; }named by pending work"
    named_in_refs "$id" "$refs" && reason="${reason}${reason:+; }named by pending work"
    named_in_refs "$branch" "$refs" && reason="${reason}${reason:+; }named by pending work"
    bad=""
    while IFS= read -r ignored; do
      ignored=${ignored#!! }
      ignored=${ignored%/}
      ignored_kind_ok "${ignored##*/}" || bad="$ignored"
      [ -z "$bad" ] || break
    done < <(git --no-optional-locks -C "$wt" status --porcelain --ignored | grep '^!! ' || true)
    [ -z "$bad" ] || reason="${reason}${reason:+; }ignored item is not regenerable"
  fi
  rm -f "$refs"
  if [ -n "$reason" ]; then append_keep "$wt" "$reason"; return 0; fi
  clone=$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir)
  clone=${clone%/.git}
  err=$(git -C "$clone" worktree remove "$wt" 2>&1) && return 0
  rc=$?
  append_keep "$wt" "git worktree remove refused: exit $rc: $(printf '%s' "$err" | tr '\t\r\n' '   ' | cut -c1-160)"
}

start_job() {
  read_config
  local repo clone wt base_ref longest
  repo="$(job_repo)"
  clone="${CLONE_ROOT%/}/$repo"
  wt="$(worktree_path "$repo")"
  base_ref="$(spec_head BASE_REF)"
  [ -n "$base_ref" ] || base_ref=main
  longest="$(git -C "$clone" ls-tree -r --name-only HEAD | awk '{ if (length($0) > length(max)) max=$0 } END { print max }')"
  path_limit_check "$WORKTREE_ROOT" "$repo" "$longest" || exit 2
  git -C "$clone" -c gc.auto=0 worktree add -b "codex/cxl-$id" "$wt" "origin/$base_ref"
  echo "worktree created: $id"
}

case "$cmd" in
  start) start_job;;
  cleanup) cleanup_worktree;;
  path-check)
    read_config
    repo="$(job_repo)"
    path_limit_check "$WORKTREE_ROOT" "$repo" "${5:-README.md}"
    ;;
  *) die "unknown command";;
esac
