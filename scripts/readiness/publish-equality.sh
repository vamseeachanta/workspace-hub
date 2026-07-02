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
# scoped commit → push (fast-forward by construction; one retry on a push race).
# The main checkout's HEAD/index/rebase state is never touched.
#
# Usage: publish-equality.sh [--rebuild] [--dry-run] [--repo <path>] [--remote <name>]
#                            [--branch <name>]
#   --rebuild   re-render the matrix HTML inside the worktree (control-plane crons)
#   --dry-run   stage + commit in the worktree, print the plan, do NOT push
#   --repo      repo whose artifacts + git dir to use (default: this script's checkout)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
REMOTE="origin"; BRANCH="main"; REBUILD=0; DRY_RUN=0
for ((i=1; i<=$#; i++)); do
  case "${!i}" in
    --rebuild) REBUILD=1;;
    --dry-run) DRY_RUN=1;;
    --repo)   j=$((i+1)); REPO_ROOT="${!j:-}";;
    --remote) j=$((i+1)); REMOTE="${!j:-origin}";;
    --branch) j=$((i+1)); BRANCH="${!j:-main}";;
  esac
done
[[ -n "$REPO_ROOT" && -d "$REPO_ROOT" ]] || { echo "publish-equality: no repo root" >&2; exit 1; }

HOST="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')"
say()  { echo "publish-equality: $*"; }
fail() {
  bash "$REPO_ROOT/scripts/notify.sh" cron equality-publish fail "$1" 2>/dev/null || true
  echo "publish-equality FAIL: $1" >&2
  exit 1
}

# One publish per host at a time (a 6h curation refresh racing the daily rebuild).
LOCK="${TMPDIR:-/tmp}/publish-equality-${HOST}.lock"
exec 9>"$LOCK" || fail "cannot open lock $LOCK"
flock -n 9 || { say "another publish in flight; skipping"; exit 0; }

WT=""
cleanup() {
  [[ -n "$WT" ]] && git -C "$REPO_ROOT" worktree remove --force "$WT" >/dev/null 2>&1
  git -C "$REPO_ROOT" worktree prune >/dev/null 2>&1
}
trap cleanup EXIT

# generated_at of an equality yaml ("" when absent/garbled) — ISO stamps compare lexically.
gen_at() { awk -F'"' '/^generated_at:/{print $2; exit}' "$1" 2>/dev/null; }

attempt() {
  cleanup; WT=""
  timeout 120 git -C "$REPO_ROOT" fetch "$REMOTE" "$BRANCH" --quiet || return 1

  WT="$(mktemp -d "${TMPDIR:-/tmp}/publish-equality-wt.XXXXXX")" || return 1
  rmdir "$WT"    # git worktree add wants to create the leaf itself
  git -C "$REPO_ROOT" worktree add --no-checkout --detach "$WT" "$REMOTE/$BRANCH" >/dev/null 2>&1 || return 1
  git -C "$WT" sparse-checkout set --no-cone '/.claude/state' '/docs/reports' '/scripts/readiness' \
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
  git -C "$WT" add -A -- '.claude/state' 'docs/reports' || return 1
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
if ! attempt; then
  say "first attempt failed (push race or transient); retrying once"
  attempt || fail "could not publish equality artifacts to $REMOTE/$BRANCH from ${HOST}"
fi
say "done (${PUBLISHED})"
