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
# checkout) → copy in any LOCAL equality yaml (read from the #3702 EQ_STATE_DIR seam,
# NOT from the tracked working tree) whose generated_at is NEWER than origin's
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
# Public label for anything that can land in tracked/published surfaces (commit
# subjects!). Raw ${HOST} put a policy-banned private hostname into a public main
# commit subject on 2026-07-18 (#3571) — resolve the fleet label instead and fall
# back to HOST only for boxes with no mapping (whose hostnames are public-safe).
# shellcheck source=scripts/readiness/lib/machine-identity.sh
. "$SCRIPT_DIR/lib/machine-identity.sh"
PUBLIC_LABEL="${EQ_MACHINE:-}"
if [[ -z "$PUBLIC_LABEL" ]]; then
  case "$HOST" in
    ace-linux-1*) PUBLIC_LABEL="dev-primary" ;;
    ace-linux-2*) PUBLIC_LABEL="dev-secondary" ;;
    *macbook*)    PUBLIC_LABEL="macbook-portable" ;;
    ace-win-1*|licensed-win-1*|acma-ansys05*) PUBLIC_LABEL="ace-win-1" ;;
    ace-win-2*|licensed-win-2*|acma-ws014*)   PUBLIC_LABEL="ace-win-2" ;;
    *)
      if _identity="$(resolve_identity_file "$HOST")"; then
        PUBLIC_LABEL="${_identity##* }"
      else
        [[ $? -eq 1 ]] && exit 1
        PUBLIC_LABEL="$HOST"
      fi ;;
  esac
fi
say()  { echo "publish-equality: $*"; }
fail() {
  bash "$REPO_ROOT/scripts/notify.sh" cron equality-publish fail "$1" 2>/dev/null || true
  echo "publish-equality FAIL: $1" >&2
  exit 1
}

# Local evidence now comes from the #3702 generation seam, NOT the tracked working tree.
# shellcheck source=scripts/readiness/lib/eq-seam.sh
. "$SCRIPT_DIR/lib/eq-seam.sh"
EQ_LOCAL_DIR="$(eq_state_dir "")"
# FAIL LOUD on an empty seam (r1 M7). Silently publishing nothing is the worst failure
# mode this change can produce: `attempt()` would stage nothing, print "nothing newer …
# no commit needed" and exit 0, so the box goes DARK on the matrix while every scheduled
# task reports success. Checked before the lock so a lock-held skip is unaffected.
_eq_local_count=0
for _f in "$EQ_LOCAL_DIR"/equality-*.yaml; do [[ -f "$_f" ]] && _eq_local_count=$((_eq_local_count+1)); done
if (( _eq_local_count == 0 )); then
  fail "no local equality evidence at ${EQ_LOCAL_DIR} (EQ_STATE_DIR seam empty or misresolved) — refusing to report success while this machine goes dark on the matrix"
fi

# One publish per host at a time (a 6h curation refresh racing the daily rebuild).
# flock is absent on Git for Windows bash; a bare `flock -n || skip` collapses
# command-not-found into the lock-held path and silently no-ops the publish (#3571).
# Detect via `command -v`; PUBLISH_EQUALITY_LOCK=mkdir forces the fallback (a mkdir
# lock is a real lock on any host — test seam and operator escape hatch).
LOCK="${TMPDIR:-/tmp}/publish-equality-${HOST}.lock"
LOCK_DIR="$LOCK.d"
LOCK_HELD=0
LOCK_IMPL="${PUBLISH_EQUALITY_LOCK:-}"
if [[ -z "$LOCK_IMPL" ]]; then
  if command -v flock >/dev/null 2>&1; then
    LOCK_IMPL="flock"
  else
    LOCK_IMPL="mkdir"
    say "lock: flock unavailable; using mkdir fallback"
  fi
fi

lock_mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || date +%s; }

if [[ "$LOCK_IMPL" == "flock" ]]; then
  exec 9>"$LOCK" || fail "cannot open lock $LOCK"
  flock -n 9 || { say "another publish in flight; skipping"; exit 0; }
else
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    # Steal only when stale (>30 min), atomically via rename: exactly one contender
    # wins the mv; a loser treats its failed mv as lock-held. No rm ever targets a
    # live-named lock dir, so a fresh replacement lock can never be deleted.
    now="$(date +%s)"
    if (( now - $(lock_mtime "$LOCK_DIR") > 1800 )) \
        && mv "$LOCK_DIR" "$LOCK_DIR.stale.$$" 2>/dev/null; then
      say "lock: stale mkdir lock (>30 min) stolen"
      rm -rf "$LOCK_DIR.stale.$$"
      mkdir "$LOCK_DIR" 2>/dev/null || { say "another publish in flight; skipping"; exit 0; }
    else
      say "another publish in flight; skipping"
      exit 0
    fi
  fi
  LOCK_HELD=1
  printf 'pid=%s start=%s\n' "$$" "$(date -u +%FT%TZ)" > "$LOCK_DIR/owner" 2>/dev/null || true
  rm -rf "$LOCK_DIR".stale.* 2>/dev/null || true   # abandoned rename leftovers are inert
fi

WT=""
# Two-tier cleanup (Codex r2-code MAJOR): attempt() re-runs the worktree cleanup
# between retries, but the LOCK must survive until process exit — a combined
# cleanup released the mkdir lock at the START of the publish it protects.
cleanup_worktree() {
  [[ -n "$WT" ]] && git -C "$REPO_ROOT" worktree remove --force "$WT" >/dev/null 2>&1
  git -C "$REPO_ROOT" worktree prune >/dev/null 2>&1
}
cleanup() {
  cleanup_worktree
  [[ "${LOCK_HELD:-0}" == 1 ]] && rm -rf "$LOCK_DIR" >/dev/null 2>&1
}
trap cleanup EXIT

# generated_at of an equality yaml ("" when absent/garbled) — ISO stamps compare lexically.
gen_at() { awk -F'"' '/^generated_at:/{print $2; exit}' "$1" 2>/dev/null; }

attempt() {
  cleanup_worktree; WT=""
  timeout 120 git -C "$REPO_ROOT" fetch "$REMOTE" "$BRANCH" --quiet || return 1

  WT="$(mktemp -d "${TMPDIR:-/tmp}/publish-equality-wt.XXXXXX")" || return 1
  rmdir "$WT"    # git worktree add wants to create the leaf itself
  git -C "$REPO_ROOT" worktree add --no-checkout --detach "$WT" "$REMOTE/$BRANCH" >/dev/null 2>&1 || return 1
  # The '/dir/*' form is load-bearing: on git 2.54 non-cone, both '/dir' and '/dir/'
  # leave every file skip-worktree — the worktree materializes EMPTY and the later
  # `git add` trips the outside-sparse guard (probed empirically on git
  # 2.54.0.windows.1, #3571 AC3). '/dir/*' is anchored and materializes contents.
  git -C "$WT" sparse-checkout set --no-cone '/.claude/state/*' '/docs/reports/*' '/scripts/readiness/*' \
    >/dev/null 2>&1 || return 1
  git -C "$WT" checkout --quiet --detach "$REMOTE/$BRANCH" || return 1
  mkdir -p "$WT/.claude/state" "$WT/docs/reports"

  # 1. Evidence: copy in each LOCAL equality yaml strictly newer than origin's copy.
  local f base local_gen origin_gen
  for f in "$EQ_LOCAL_DIR"/equality-*.yaml; do
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
  # --state-dir/--out-dir are passed EXPLICITLY and point at the worktree only (#3702).
  # --state-dir REPLACES the builder's default input layers (r1 M1) — without that the
  # render would fold the interactive checkout's stale peer evidence, and this box's
  # local seam copy, into the PUBLISHED matrix and destroy the union-of-freshest
  # guarantee this whole worktree design exists to provide.
  if [[ "$REBUILD" == 1 ]]; then
    local render_args=(--state-dir "$WT/.claude/state" --out-dir "$WT/docs/reports")
    if command -v uv >/dev/null 2>&1; then
      (cd "$WT" && uv run --script scripts/readiness/build-equality-matrix.py \
        "${render_args[@]}") >/dev/null || return 1
    else
      (cd "$WT" && python3 scripts/readiness/build-equality-matrix.py \
        "${render_args[@]}") >/dev/null || return 1
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

  git -C "$WT" commit --quiet -m "chore(equality): publish equality artifacts from ${PUBLIC_LABEL}" \
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
  attempt || fail "could not publish equality artifacts to $REMOTE/$BRANCH from ${PUBLIC_LABEL}"
fi
say "done (${PUBLISHED})"
