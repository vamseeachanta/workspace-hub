#!/usr/bin/env bash
set -euo pipefail

DEFAULT_WORKTREE_KEEP_MINUTES=60

cmd="${1:-start}"
dry_run=false
if [ "${2:-}" = --dry-run ]; then
  dry_run=true
  set -- "$1" "${@:3}"
fi
id="${2:-}"
issue="${3:-none}"
[ "${5:-}" != --dry-run ] || dry_run=true
config_path="${4:-${JOB_QUEUE_CONFIG:-$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)/job-queue.local.conf}}"

die() { echo "$*" >&2; exit 2; }
case "$id" in ""|*[!a-z0-9-]*) die "bad job id";; esac
case "$issue" in none|*[!0-9]*) [ "$issue" = none ] || die "bad issue";; esac

read_config() {
  [ -f "$config_path" ] || die "configuration file not found"
  while IFS='=' read -r key value; do
    key=$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    value=$(printf '%s' "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    case "$key" in ""|\#*) continue;; esac
    case "$key" in
      QUEUE_ROOT|CLONE_ROOT|WORKTREE_ROOT|JOB_BRANCH_PREFIX|DEFAULT_REPOSITORY|REPOSITORY_ALLOW_LIST|MIN_DISK_FREE_GB)
        eval "$key=\$value"
        ;;
    esac
  done < "$config_path"
  : "${JOB_BRANCH_PREFIX:?missing JOB_BRANCH_PREFIX}"
  git check-ref-format --branch "${JOB_BRANCH_PREFIX}${id}" >/dev/null || die "bad job branch"
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
  case "$repo" in .*|*[!A-Za-z0-9._-]*|"") die "blocked: repository name is not allowed";; esac
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
  local refs="$1" qid spec
  : > "$refs"
  if [ -f "$QUEUE_ROOT/queue.txt" ]; then
    while read -r qid _; do
      case "$qid" in ""|\#*) continue;; esac
      [ -f "$QUEUE_ROOT/logs/$qid.result" ] || printf '%s\n' "$qid" >> "$refs"
      spec="$QUEUE_ROOT/jobs/$qid.md"
      [ -f "$spec" ] && [ ! -f "$QUEUE_ROOT/logs/$qid.result" ] && cat "$spec" >> "$refs"
    done < "$QUEUE_ROOT/queue.txt"
  fi
  return 0
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
  local wt="$1" reason="$2" size="0" record retry_dir
  if $dry_run; then printf 'keep: %s: %s\n' "$id" "$reason"; return 0; fi
  mkdir -p "$QUEUE_ROOT/logs"
  retry_dir="$QUEUE_ROOT/logs/recent-cleanup"
  if [ "$reason" = "worktree was touched recently" ]; then
    mkdir -p "$retry_dir"
    touch -- "$retry_dir/$id"
  fi
  if [ -d "$wt" ]; then
    if size=$(timeout --kill-after=1s 2s du -sk -- "$wt" 2>/dev/null | awk '{print $1}') &&
       [[ $size =~ ^[0-9]+$ ]]; then :; else size=unknown; fi
  fi
  record=$(printf '%s\t%s\t%s\t%s' "$id" "$wt" "$size" "$reason")
  if [ ! -f "$QUEUE_ROOT/logs/kept-worktrees.tsv" ] ||
     ! grep -Fxq -- "$record" "$QUEUE_ROOT/logs/kept-worktrees.tsv"; then
    printf '%s\n' "$record" >> "$QUEUE_ROOT/logs/kept-worktrees.tsv"
  fi
  if [ "$reason" != "worktree was touched recently" ]; then
    rm -f -- "$retry_dir/$id"
  fi
}

is_pushed() {
  local wt="$1" branch="$2" head remote
  head=$(git -C "$wt" rev-parse HEAD)
  # Issue 4081, cleanup criterion: work must be pushed, not merely cached locally.
  # Preserve the existing network timeout used by cleanup-recent.
  remote=$(GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never timeout --kill-after=2s 15s \
    git -C "$wt" ls-remote origin "refs/heads/$branch" 2>/dev/null |
    cut -f1 | head -n 1) || return 1
  [ -n "$remote" ] || return 1
  [ "$remote" = "$head" ] && return 0
  git -C "$wt" merge-base --is-ancestor "$head" "$remote" 2>/dev/null
}

cleanup_worktree() (
  read_config
  local repo wt refs branch status ignored item bad reason result clone err rc marker holder
  local listing top listed_wt entry admin touched keep_minutes listed
  repo="$(job_repo)"
  wt="$(worktree_path "$repo")"
  result="$QUEUE_ROOT/logs/$id.result"
  refs=$(mktemp "${TMPDIR:-$QUEUE_ROOT}/pending-refs.XXXXXX")
  trap 'rm -f -- "$refs"' EXIT
  pending_refs_file "$refs"
  reason=""
  [ -f "$result" ] || reason="${reason}${reason:+; }job has no result line"
  if [ -f "$result" ] && ! head -n 1 "$result" | grep -qE '^OK([[:space:]]|$)'; then
    reason="${reason}${reason:+; }job result is not successful"
  fi
  for marker in "$QUEUE_ROOT"/locks/slot*/owner; do
    [ -f "$marker" ] || continue
    read -r holder _ < "$marker" || true
    [ "$holder" != "$id" ] || reason="${reason}${reason:+; }job holds a lock slot"
  done
  [ -d "$wt" ] || reason="${reason}${reason:+; }worktree is absent"
  if [ -z "$reason" ]; then
    branch=$(git -C "$wt" symbolic-ref --short -q HEAD || true)
    [ -n "$branch" ] || reason="${reason}${reason:+; }worktree is detached"
    [ "$branch" = "${JOB_BRANCH_PREFIX}${id}" ] || reason="${reason}${reason:+; }worktree is not on the job branch"
    status=$(git --no-optional-locks -C "$wt" status --porcelain --untracked-files=all) || reason="${reason}${reason:+; }git status failed"
    [ -z "$status" ] || reason="${reason}${reason:+; }changed or untracked files"
    is_pushed "$wt" "$branch" || reason="${reason}${reason:+; }head is not on its remote branch"
    named_in_refs "$(basename "$wt")" "$refs" && reason="${reason}${reason:+; }named by pending work"
    named_in_refs "$id" "$refs" && reason="${reason}${reason:+; }named by pending work"
    [ -n "$branch" ] && named_in_refs "$branch" "$refs" && reason="${reason}${reason:+; }named by pending work"
    bad=""
    if ignored=$(git --no-optional-locks -C "$wt" status --porcelain --ignored); then
      while IFS= read -r item; do
        case "$item" in '!! '*) ;; *) continue;; esac
        item=${item#!! }
        item=${item%/}
        ignored_kind_ok "${item##*/}" || bad="$item"
        [ -z "$bad" ] || break
      done <<< "$ignored"
    else
      reason="${reason}${reason:+; }git ignored status failed"
    fi
    [ -z "$bad" ] || reason="${reason}${reason:+; }ignored item is not regenerable"
    if top=$(git -C "$wt" rev-parse --show-toplevel) &&
       listing=$(git -C "$wt" worktree list --porcelain); then
      listed_wt=""
      listed=false
      while IFS= read -r entry; do
        case "$entry" in
          worktree\ *)
            listed_wt=${entry#worktree }
            [ "$listed_wt" != "$top" ] || listed=true
            ;;
          locked|locked\ *)
            [ "$listed_wt" != "$top" ] || reason="${reason}${reason:+; }worktree is locked"
            ;;
        esac
      done <<< "$listing"
      $listed || reason="${reason}${reason:+; }worktree is not listed by git"
    else
      reason="${reason}${reason:+; }git worktree lock lookup failed"
    fi
    keep_minutes=${WORKTREE_KEEP_MINUTES:-$DEFAULT_WORKTREE_KEEP_MINUTES}
    if [[ ! $keep_minutes =~ ^[0-9]+$ || ! $keep_minutes =~ [1-9] ]]; then
      reason="${reason}${reason:+; }invalid worktree retention minutes"
    elif admin=$(git -C "$wt" rev-parse --absolute-git-dir) &&
         touched=$(find "$wt" -path "$wt/.git" -prune -o -type f -mmin "-$keep_minutes" -print -quit) &&
         touched+=$(find "$admin" -mmin "-$keep_minutes" -print -quit); then
      [ -z "$touched" ] || reason="${reason}${reason:+; }worktree was touched recently"
    else
      reason="${reason}${reason:+; }worktree activity probe failed"
    fi
  fi
  if [ -n "$reason" ]; then append_keep "$wt" "$reason"; return 0; fi
  if $dry_run; then printf 'would remove: %s\n' "$id"; return 0; fi
  clone=$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir) || { append_keep "$wt" "git common directory lookup failed"; return 0; }
  clone=${clone%/.git}
  if err=$(git -C "$clone" worktree remove "$wt" 2>&1); then
    rm -f -- "$QUEUE_ROOT/logs/recent-cleanup/$id"
    return 0
  else
    rc=$?
  fi
  reason="git worktree remove refused"
  if [ ! -e "$wt/.git" ]; then reason="removal failed; tree may be partial"; fi
  append_keep "$wt" "$reason: exit $rc: $(printf '%s' "$err" | tr '\t\r\n' '   ' | cut -c1-160)"
)

# Retry only recent-only keeps, at most six due entries per pump invocation.
# Child execution preserves errexit in cleanup_worktree; no job is started here.
cleanup_recent() (
  read_config
  local retry_dir marker retry_id due count=0 keep_minutes rc
  local -a retry_args=()
  retry_dir="$QUEUE_ROOT/logs/recent-cleanup"
  keep_minutes=${WORKTREE_KEEP_MINUTES:-$DEFAULT_WORKTREE_KEEP_MINUTES}
  [[ $keep_minutes =~ ^[0-9]+$ && $keep_minutes =~ [1-9] ]] ||
    die "invalid worktree retention minutes"
  [ -d "$retry_dir" ] || return 0
  if $dry_run; then retry_args=(--dry-run); fi
  for marker in "$retry_dir"/*; do
    if [ ! -f "$marker" ] || [ -L "$marker" ]; then continue; fi
    retry_id=${marker##*/}
    case "$retry_id" in ""|*[!a-z0-9-]*) continue;; esac
    due=$(find "$marker" -maxdepth 0 -type f ! -mmin "-$keep_minutes" -print) ||
      die "retry activity probe failed; worktrees kept"
    [ -n "$due" ] || continue
    count=$((count + 1))
    printf 'retry cleanup: %s\n' "$retry_id"
    # Record before starting: even an outer kill must leave this entry backed off.
    $dry_run || touch -- "$marker"
    if timeout --kill-after=2s 90s "$BASH" "$0" cleanup "$retry_id" none "$config_path" "${retry_args[@]}"; then
      :
    else
      rc=$?
      if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
        ( id="$retry_id"; append_keep "$(worktree_path "$(job_repo)")" "cleanup attempt timed out" )
      fi
      printf 'cleanup retry failed: %s; inspect worktree and keep log\n' "$retry_id" >&2
    fi
    [ "$count" -lt 6 ] || break
  done
)

# Recheck immediately before creating a worktree, including direct launcher use.
disk_floor_check() {
  local floor="${MIN_DISK_FREE_GB:-50}" root available
  case "$floor" in ""|*[!0-9]*) echo "blocked: invalid disk floor"; return 1;; esac
  floor=$((10#$floor))
  [ "$floor" -ge 50 ] || floor=50
  for root in "$CLONE_ROOT" "$WORKTREE_ROOT"; do
    available=$(df -Pk -- "$root" | awk 'END {print $4}') || return 1
    case "$available" in ""|*[!0-9]*) echo "blocked: disk probe failed"; return 1;; esac
    [ "$available" -ge "$((floor * 1024 * 1024))" ] || { echo "blocked: disk under floor"; return 1; }
  done
}

start_job() {
  read_config
  local repo clone wt base_ref longest
  disk_floor_check || return 2
  repo="$(job_repo)"
  clone="${CLONE_ROOT%/}/$repo"
  wt="$(worktree_path "$repo")"
  base_ref="$(spec_head BASE_REF)"
  [ -n "$base_ref" ] || base_ref=main
  longest="$(git -C "$clone" ls-tree -r --name-only "origin/$base_ref" | awk '{ if (length($0) > length(max)) max=$0 } END { print max }')"
  path_limit_check "$WORKTREE_ROOT" "$repo" "$longest" || exit 2
  git -C "$clone" -c gc.auto=0 worktree add -b "${JOB_BRANCH_PREFIX}${id}" "$wt" "origin/$base_ref"
  echo "worktree created: $id"
}

case "$cmd" in
  start) start_job;;
  cleanup) cleanup_worktree;;
  cleanup-recent) cleanup_recent;;
  path-check)
    read_config
    repo="$(job_repo)"
    path_limit_check "$WORKTREE_ROOT" "$repo" "${5:-README.md}"
    ;;
  *) die "unknown command";;
esac
