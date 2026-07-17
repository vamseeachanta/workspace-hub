#!/usr/bin/env bash
# publish-equality.sh — commit THIS machine's equality artifacts to origin/main via a
# disposable SPARSE worktree, independent of the interactive checkout's state.
#
# WHY: the matrix only compares machines equally when every machine's evidence reaches
# origin/main. The scheduled Linux path (equality-matrix-cron.sh) used to only BUILD and
# delegate the commit+push to the repo-sync cron — a chain that breaks exactly when the
# fleet most needs comparable evidence: a diverged interactive checkout piles up non-FF
# commits, a dead sync cron publishes nothing, and the machine goes dark on the matrix.
#
# HOW: fetch origin/main → temp worktree with a sparse checkout of ONLY the artifact
# paths (.claude/state, docs/reports, scripts/readiness — seconds, not a 22k-file
# checkout) → copy in any LOCAL equality yaml whose generated_at is NEWER than origin's
# copy (never clobbers a peer's fresher evidence) → optionally rebuild the matrix INSIDE
# the worktree so the committed render reflects the union of freshest evidence →
# scoped commit → push (fast-forward by construction; bounded retries on a push race).
# The main checkout's HEAD/index/rebase state is never touched.
#
# Usage: publish-equality.sh [--rebuild] [--dry-run] [--repo <path>] [--remote <name>]
#                            [--branch <name>] [--max-attempts <n>]
#                            [--retry-delay-seconds <n>]
#   --rebuild   re-render the matrix HTML inside the worktree (control-plane crons)
#   --dry-run   stage + commit in the worktree, print the plan, do NOT push
#   --repo      repo whose artifacts + git dir to use (default: this script's checkout)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
REMOTE="origin"; BRANCH="main"; REBUILD=0; DRY_RUN=0
MAX_ATTEMPTS=3; RETRY_DELAY_SECONDS=2
usage_error() { echo "publish-equality: $*" >&2; exit 2; }
while (( $# )); do
  case "$1" in
    --rebuild) REBUILD=1; shift;;
    --dry-run) DRY_RUN=1; shift;;
    --repo|--remote|--branch|--max-attempts|--retry-delay-seconds)
      option="$1"
      [[ -n "${2:-}" ]] || usage_error "$option requires a value"
      value="$2"
      shift 2
      case "$option" in
        --repo) REPO_ROOT="$value";;
        --remote) REMOTE="$value";;
        --branch) BRANCH="$value";;
        --max-attempts) MAX_ATTEMPTS="$value";;
        --retry-delay-seconds) RETRY_DELAY_SECONDS="$value";;
      esac
      ;;
    *) usage_error "unknown option: $1";;
  esac
done
[[ "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]] \
  || usage_error "--max-attempts must be a positive integer"
[[ "$RETRY_DELAY_SECONDS" =~ ^[0-9]+$ ]] \
  || usage_error "--retry-delay-seconds must be a non-negative integer"
[[ -n "$REPO_ROOT" && -d "$REPO_ROOT" ]] || { echo "publish-equality: no repo root" >&2; exit 1; }

HOST="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')"
say()  { echo "publish-equality: $*"; }
fail() {
  bash "$REPO_ROOT/scripts/notify.sh" cron equality-publish fail "$1" 2>/dev/null || true
  echo "publish-equality FAIL: $1" >&2
  exit 1
}

WT=""
WT_REGISTERED=0
cleanup() {
  local rc=0
  if [[ -n "$WT" ]]; then
    if [[ "$WT_REGISTERED" == 1 ]] \
      && git -C "$REPO_ROOT" worktree remove --force "$WT" >/dev/null 2>&1; then
      WT=""
      WT_REGISTERED=0
    elif [[ "$WT_REGISTERED" == 0 && ! -e "$WT" ]]; then
      WT=""
    elif [[ "$WT_REGISTERED" == 0 && -d "$WT" ]] && rmdir "$WT" 2>/dev/null; then
      WT=""
    else
      rc=1
    fi
  fi
  git -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || rc=1
  return "$rc"
}
best_effort_cleanup() { cleanup || true; }
trap best_effort_cleanup EXIT

# generated_at of an equality yaml ("" when absent/garbled) — ISO stamps compare lexically.
gen_at() { awk -F'"' '/^generated_at:/{print $2; exit}' "$1" 2>/dev/null; }

attempt() {
  cleanup || return 1
  timeout 120 git -C "$REPO_ROOT" fetch "$REMOTE" "$BRANCH" --quiet || return 1

  WT="$(mktemp -d "${TMPDIR:-/tmp}/publish-equality-wt.XXXXXX")" || return 1
  WT_REGISTERED=0
  rmdir "$WT" || return 1    # git worktree add wants to create the leaf itself
  if git -C "$REPO_ROOT" worktree add --no-checkout --detach "$WT" "$REMOTE/$BRANCH" \
    >/dev/null 2>&1; then
    WT_REGISTERED=1
  else
    # A failed Git command can still have registered the worktree. Detect that
    # state so cleanup uses Git rather than treating it as an ordinary temp dir.
    git -C "$WT" rev-parse --is-inside-work-tree >/dev/null 2>&1 && WT_REGISTERED=1
    return 1
  fi
  # Do not lead these patterns with '/': MSYS rewrites slash-prefixed argv as
  # Windows paths before Git sees them, producing an empty sparse checkout.
  git -C "$WT" sparse-checkout set --no-cone '.claude/state/' 'docs/reports/' 'scripts/readiness/' \
    >/dev/null 2>&1 || return 1
  git -C "$WT" checkout --quiet --detach "$REMOTE/$BRANCH" || return 1
  mkdir -p "$WT/.claude/state" "$WT/docs/reports"

  # 1. Evidence: copy in each LOCAL equality yaml strictly newer than origin's copy.
  local f base local_gen origin_gen
  for f in "$REPO_ROOT"/.claude/state/equality-*.yaml; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    local_gen="$(gen_at "$f")"
    [[ -n "$local_gen" ]] || continue                      # unstamped evidence is not publishable
    origin_gen="$(gen_at "$WT/.claude/state/$base")"
    if [[ "$local_gen" > "${origin_gen:-}" ]]; then
      cp "$f" "$WT/.claude/state/$base" || return 1
      say "evidence: $base ($local_gen > ${origin_gen:-none})"
    fi
  done

  # 2. Render (control-plane): rebuild from the worktree's union-of-freshest evidence.
  if [[ "$REBUILD" == 1 ]]; then
    if command -v uv >/dev/null 2>&1; then
      (cd "$WT" && uv run --script scripts/readiness/build-equality-matrix.py) >/dev/null \
        || return 1
    else
      (cd "$WT" && python3 scripts/readiness/build-equality-matrix.py) >/dev/null || return 1
    fi
  fi

  # 3. Scoped stage + allowlist guard: ONLY equality artifacts may ever be committed here.
  # --sparse is required when concurrent worktrees briefly observe another
  # worktree's sparse-index configuration while Git initializes per-worktree state.
  git -C "$WT" add --sparse -A -- '.claude/state' 'docs/reports' || return 1
  local staged
  staged="$(git -C "$WT" diff --cached --name-only)"
  if [[ -z "$staged" ]]; then
    say "nothing newer than $REMOTE/$BRANCH; no commit needed"
    PUBLISHED="noop"
    return 0
  fi
  while IFS= read -r p; do
    case "$p" in
      .claude/state/equality-*.yaml) ;;
      docs/reports/*machine-equality-matrix.html) ;;
      *) say "unexpected staged path '$p' — refusing to publish"; return 1;;
    esac
  done <<< "$staged"

  git -C "$WT" commit --quiet -m "chore(equality): publish equality artifacts from ${HOST}" \
    || return 1
  if [[ "$DRY_RUN" == 1 ]]; then
    say "dry-run — would push:"
    git -C "$WT" show --stat --oneline HEAD | sed 's/^/  /'
    PUBLISHED="dry-run"
    return 0
  fi
  timeout 300 git -C "$WT" push "$REMOTE" HEAD:"$BRANCH" || return 1
  PUBLISHED="pushed"
  return 0
}

PUBLISHED=""
attempt_number=1
while ! attempt; do
  if (( attempt_number >= MAX_ATTEMPTS )); then
    fail "could not publish equality artifacts to $REMOTE/$BRANCH from ${HOST} after ${MAX_ATTEMPTS} attempts"
  fi
  say "attempt ${attempt_number} failed (push race or transient); retrying"
  (( RETRY_DELAY_SECONDS > 0 )) && sleep "$RETRY_DELAY_SECONDS"
  attempt_number=$((attempt_number + 1))
done
cleanup || fail "publication ${PUBLISHED} completed but publisher worktree cleanup failed"
trap - EXIT
say "done (${PUBLISHED})"
