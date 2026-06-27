#!/usr/bin/env bash
# reconcile-ecosystem.sh — bring THIS machine back to ecosystem + equality equivalence.
#
# Report-first corrective-action driver. Default mode is READ-ONLY: it detects repo
# hygiene drift (dirty trees, behind/ahead upstream, merged-but-undeleted branches,
# stale worktrees, stale stashes) across this machine's sibling repos AND reads this
# machine's equality-matrix verdicts, then prints ONE classified plan:
#
#   AUTO-SAFE     — reversible / guard-approved; --apply will run it
#   NEEDS-APPROVAL— destructive or judgement-dependent; printed, never auto-run
#   OPERATOR-ONLY — off-box (Windows licence probe, hardware, remote host)
#
# Safety invariants (load-bearing — see worktree_guard.py #3143):
#   * Dirty work is NEVER discarded. --apply --stash-dirty stashes it (recoverable);
#     without that flag dirty trees are surfaced only.
#   * A branch is deleted ONLY if merged to origin/main, matches the safe-pattern, is
#     not current, and passes `worktree_guard.py safe-delete-branch`.
#   * A worktree is removed ONLY if `worktree_guard.py safe-remove-worktree` approves
#     it (owned, not an active session) — foreign/unowned worktrees are surfaced, never
#     removed. This is what protects the intentional-worktree automation host.
#   * Remotes: only fast-forward (`pull --ff-only`); never reset/force.
#
# Usage:
#   reconcile-ecosystem.sh                 # report only (read-only), exit 0
#   reconcile-ecosystem.sh --apply         # run the AUTO-SAFE subset
#   reconcile-ecosystem.sh --apply --stash-dirty   # also stash dirty trees (recoverable)
#   reconcile-ecosystem.sh --apply --equality      # after hygiene, re-collect + rebuild matrix
#   reconcile-ecosystem.sh --json          # machine-readable plan (no actions)
#
# Exit: 0 = report produced / apply succeeded; non-zero = hard failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../.." && pwd))"
GUARD="${REPO_ROOT}/scripts/lib/worktree_guard.py"
BUILD_MATRIX="${REPO_ROOT}/scripts/readiness/build-equality-matrix.py"
# Canonical equality entry points — reconcile DELEGATES here rather than re-implementing the
# collect+build chain, so it stays single-sourced with the cron + operator-refresh paths:
#   equality-matrix-cron.sh    = collect THIS box + rebuild matrix (fail-loud, no push)
#   refresh-equality-matrix.sh = fresh-main -> cron -> commit+push (publishes the live link)
CRON="${REPO_ROOT}/scripts/readiness/equality-matrix-cron.sh"
REFRESH="${REPO_ROOT}/scripts/readiness/refresh-equality-matrix.sh"
SIBLING_ROOT="$(dirname "$REPO_ROOT")"

# Branch names safe to auto-delete once merged (mirrors daily-cleanup.sh SAFE_BRANCH_RE).
SAFE_BRANCH_RE='^(chore/auto-|bot/|claude-session/|pages/)'
STALE_DAYS="${RECONCILE_STALE_DAYS:-14}"

APPLY=0; STASH_DIRTY=0; DO_EQUALITY=0; AS_JSON=0
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --stash-dirty) STASH_DIRTY=1 ;;
    --equality) DO_EQUALITY=1 ;;
    --json) AS_JSON=1 ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "reconcile-ecosystem.sh: unknown arg '$a'" >&2; exit 2 ;;
  esac
done

ts() { date '+%Y-%m-%dT%H:%M:%S'; }

# ── machine slug (canonical mapping, mirrors collect-equality.sh) ─────────────
HOST="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')"
case "$HOST" in
  ace-linux-1*) MACHINE="dev-primary" ;;
  ace-linux-2*) MACHINE="dev-secondary" ;;
  *macbook*)    MACHINE="macbook-portable" ;;
  ace-win-1*|licensed-win-1*|acma-ansys05*) MACHINE="ace-win-1" ;;
  ace-win-2*|licensed-win-2*|acma-ws014*)   MACHINE="ace-win-2" ;;
  *) MACHINE="${RECONCILE_MACHINE:-$HOST}" ;;
esac

# dev-primary runs the intentional worktree-per-feature automation + the daily-cleanup
# cron owns destructive disposal there → branch/worktree deletion is REPORT-ONLY on it.
DESTRUCTIVE_OK=1
[ "$MACHINE" = "dev-primary" ] && DESTRUCTIVE_OK=0

# ── collectors ───────────────────────────────────────────────────────────────
# Echo a planned action line: <CLASS>\t<repo>\t<action>\t<command>
PLAN=()
add() { PLAN+=("$1"$'\t'"$2"$'\t'"$3"$'\t'"$4"); }

discover_repos() {
  # workspace-hub + any sibling dir that is a git repo (not a worktree link).
  echo "$REPO_ROOT"
  for d in "$SIBLING_ROOT"/*/; do
    d="${d%/}"
    [ "$d" = "$REPO_ROOT" ] && continue
    [ -d "$d/.git" ] || continue
    echo "$d"
  done
}

scan_repo() {
  local repo="$1" name; name="$(basename "$repo")"
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || return 0

  # dirty
  local dirty; dirty=$(git -C "$repo" status --porcelain 2>/dev/null | grep -c . || true)
  if [ "${dirty:-0}" -gt 0 ]; then
    if [ "$STASH_DIRTY" = 1 ]; then
      add AUTO-SAFE "$name" "stash $dirty dirty path(s) (recoverable)" \
        "git -C '$repo' stash push -u -m 'reconcile $(ts)'"
    else
      add NEEDS-APPROVAL "$name" "$dirty dirty path(s) — commit/push or re-run with --stash-dirty" \
        "git -C '$repo' status --short"
    fi
  fi

  # ahead / behind upstream (guarded: upstream may not exist)
  local ab behind=0 ahead=0
  ab=$(git -C "$repo" rev-list --left-right --count HEAD...@{u} 2>/dev/null || true)
  if [ -n "$ab" ]; then
    ahead=$(printf '%s' "$ab" | awk '{print $1}'); behind=$(printf '%s' "$ab" | awk '{print $2}')
    if [ "${behind:-0}" -gt 0 ] && [ "${dirty:-0}" -eq 0 ] && [ "${ahead:-0}" -eq 0 ]; then
      add AUTO-SAFE "$name" "behind upstream by $behind — fast-forward" \
        "git -C '$repo' pull --ff-only"
    elif [ "${behind:-0}" -gt 0 ]; then
      add NEEDS-APPROVAL "$name" "behind by $behind but dirty/ahead — manual integrate" \
        "git -C '$repo' status --short --branch"
    fi
    if [ "${ahead:-0}" -gt 0 ]; then
      add NEEDS-APPROVAL "$name" "ahead of upstream by $ahead unpushed commit(s)" \
        "git -C '$repo' log --oneline @{u}..HEAD"
    fi
  fi

  # merged, safe-pattern, non-current local branches → guard-gated delete
  local cur merged; cur=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null || echo DETACHED)
  merged=$(git -C "$repo" branch --merged origin/main 2>/dev/null </dev/null)
  while IFS= read -r b; do
    b="${b#"${b%%[![:space:]]*}"}"; b="${b#\* }"; [ -z "$b" ] && continue
    [ "$b" = "$cur" ] && continue
    [[ "$b" =~ $SAFE_BRANCH_RE ]] || continue
    if [ "$DESTRUCTIVE_OK" = 1 ] && ( cd "$repo" && python3 "$GUARD" safe-delete-branch "$b" ) >/dev/null 2>&1 </dev/null; then
      add AUTO-SAFE "$name" "delete merged safe-pattern branch '$b'" \
        "git -C '$repo' branch -d '$b'"
    else
      add NEEDS-APPROVAL "$name" "merged branch '$b' (guard/host policy held)" \
        "python3 '$GUARD' safe-delete-branch '$b'"
    fi
  done <<< "$merged"

  # squash-merged-stale branches: GitHub squash-merge does NOT preserve ancestry, so a branch
  # whose PR is MERGED is invisible to `git branch --merged` and the ancestry pass above — it
  # accumulates forever. Detect via PR state (gh). The merged PR is the proof the work is in
  # main, which is why `branch -D` (force) is correct here (git can't see the squash as an
  # ancestor). Gated on: PR merged AND worktree_guard approval AND DESTRUCTIVE_OK. Degrades
  # to a no-op if gh is unavailable/unauthenticated (the ancestry pass still runs).
  local nbranch; nbranch=$(git -C "$repo" branch 2>/dev/null | grep -c . || echo 0)
  if [ "${nbranch:-0}" -gt 1 ] && command -v gh >/dev/null 2>&1; then
    local gh_run=(gh pr list --state merged --limit 500 --json headRefName -q '.[].headRefName')
    command -v timeout >/dev/null 2>&1 && gh_run=(timeout 25 "${gh_run[@]}")
    local merged_prs all_b
    merged_prs=$(cd "$repo" && "${gh_run[@]}" 2>/dev/null </dev/null)
    if [ -n "$merged_prs" ]; then
      all_b=$(git -C "$repo" branch --format='%(refname:short)' 2>/dev/null </dev/null)
      while IFS= read -r b; do
        [ -z "$b" ] && continue
        [ "$b" = "$cur" ] && continue
        [ "$b" = "main" ] && continue
        grep -qx "$b" <<< "$merged_prs" || continue                         # PR merged ⇒ in main
        git -C "$repo" merge-base --is-ancestor "$b" origin/main 2>/dev/null && continue  # ancestry pass owns it
        if [ "$DESTRUCTIVE_OK" = 1 ] && ( cd "$repo" && python3 "$GUARD" safe-delete-branch "$b" ) >/dev/null 2>&1 </dev/null; then
          add AUTO-SAFE "$name" "delete squash-merged branch '$b' (PR merged, not in ancestry)" \
            "git -C '$repo' branch -D '$b'"
        else
          add NEEDS-APPROVAL "$name" "squash-merged branch '$b' (guard/host policy held)" \
            "cd '$repo' && python3 '$GUARD' safe-delete-branch '$b'"
        fi
      done <<< "$all_b"
    fi
  fi

  # worktrees: deny-by-default — only surface; removal needs ownership proof
  local wt; wt=$(git -C "$repo" worktree list --porcelain 2>/dev/null | grep -c '^worktree ' || true)
  if [ "${wt:-0}" -gt 1 ]; then
    add NEEDS-APPROVAL "$name" "$((wt-1)) linked worktree(s) — prune only via guard ownership" \
      "git -C '$repo' worktree list  # then: cd '$repo' && python3 '$GUARD' safe-remove-worktree <dir> <owner>"
  fi

  # stale stashes (≥ STALE_DAYS): surface only, never auto-drop
  local stash; stash=$(git -C "$repo" stash list 2>/dev/null | grep -c . || true)
  if [ "${stash:-0}" -gt 0 ]; then
    add NEEDS-APPROVAL "$name" "$stash stash(es) present — inspect before any drop" \
      "git -C '$repo' stash list --date=iso-strict"
  fi
}

# ── equality remediation mapping (this machine's column) ─────────────────────
equality_plan() {
  command -v uv >/dev/null 2>&1 || { add OPERATOR-ONLY "$MACHINE" "uv missing — cannot read equality verdicts" "install uv"; return; }
  local json verdicts; json=$(uv run --script "$BUILD_MATRIX" --json --machine "$MACHINE" 2>/dev/null </dev/null) || return
  # parse "dim": "VERDICT" lines for this machine, map each non-OK to a fix.
  # here-string (not a pipe) so add() runs in THIS shell and PLAN persists.
  verdicts=$(printf '%s\n' "$json" | grep -oE '"[a-z_:]+": "[A-Z-]+"')
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local dim verdict; dim=$(printf '%s' "$line" | sed -E 's/^"([^"]+)".*/\1/')
    verdict=$(printf '%s' "$line" | sed -E 's/.*"([A-Z-]+)"$/\1/')
    case "$verdict" in
      CONFORMS|EQUAL|PARITY|EXPECTED-DIFF|EXPECTED-DIVERGENCE|UNREACHABLE|ABSENT|CURATED-FRESH|SKILLS-CURRENT|MEMORY-FRESH) continue ;;
    esac
    case "$verdict" in
      STALE-CHECKOUT)
        add AUTO-SAFE "$MACHINE" "[$dim] STALE — clean tree + fetch, then re-collect" \
          "git -C '$REPO_ROOT' fetch origin main && bash '$CRON'" ;;
      MISSING-EVIDENCE)
        if printf '%s' "$dim" | grep -q '^harness:'; then
          add NEEDS-APPROVAL "$MACHINE" "[$dim] provider capability absent (or no Claude baseline on host)" \
            "verify provider install/auth; on a Hermes-only host this is by-design"
        else
          add AUTO-SAFE "$MACHINE" "[$dim] no fresh report — collect equality on this box" \
            "bash '$CRON'"
        fi ;;
      BELOW-BASELINE)
        case "$dim" in
          solvers) add OPERATOR-ONLY "$MACHINE" "[solvers] licence probe emits present≠licensed — Windows licence-probe follow-up" "see PR #2850 note" ;;
          data_access) add NEEDS-APPROVAL "$MACHINE" "[data_access] a required tier-1 sibling is not cloned" "clone the missing repo under $SIBLING_ROOT" ;;
          compute) add OPERATOR-ONLY "$MACHINE" "[compute] under cores/ram/gpu floor — hardware/registry" "reconcile harness-config compute_floor or upgrade box" ;;
          *) add NEEDS-APPROVAL "$MACHINE" "[$dim] below declared baseline" "inspect equality-$MACHINE.yaml" ;;
        esac ;;
      DIVERGES|NO-MAJORITY)
        case "$dim" in
          skills) add NEEDS-APPROVAL "$MACHINE" "[skills] likely tracked-symlink-materialized-as-text — repair (rm+checkout tracked paths)" \
                    "git -C '$REPO_ROOT' config core.symlinks true; for s in .codex/skills .gemini/skills; do rm -f \"\$s\" && git -C '$REPO_ROOT' checkout -- \"\$s\"; done" ;;
          harness|behavior) add NEEDS-APPROVAL "$MACHINE" "[$dim] runtime/config drift — rebuild soul runtime + re-collect" \
                    "bash scripts/agents/build-soul-runtime.sh && bash scripts/agents/install-soul-runtime.sh && bash '$CRON'" ;;
          scheduler) add NEEDS-APPROVAL "$MACHINE" "[scheduler] cron drift — reconcile jobs then re-collect" \
                    "bash scripts/cron/setup-cron.sh --check && bash '$CRON'" ;;
          *) add NEEDS-APPROVAL "$MACHINE" "[$dim] diverges from peers — stale report? re-collect, else reconcile config" \
                    "bash '$CRON'" ;;
        esac ;;
      *) add NEEDS-APPROVAL "$MACHINE" "[$dim] verdict $verdict — investigate" "inspect equality-$MACHINE.yaml" ;;
    esac
  done <<< "$verdicts"
}

# ── run detection ────────────────────────────────────────────────────────────
# Read the repo list into an array FIRST (no process-substitution on the scan loop —
# inner git/guard calls would otherwise consume the loop's stdin and drop repos).
mapfile -t REPOS < <(discover_repos)
for repo in "${REPOS[@]}"; do scan_repo "$repo"; done
equality_plan

# ── output ───────────────────────────────────────────────────────────────────
if [ "$AS_JSON" = 1 ]; then
  printf '{"machine":"%s","destructive_ok":%s,"plan":[' "$MACHINE" "$DESTRUCTIVE_OK"
  first=1
  for row in "${PLAN[@]:-}"; do
    [ -z "$row" ] && continue
    IFS=$'\t' read -r cls name act cmd <<<"$row"
    esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
    [ "$first" = 1 ] || printf ','
    printf '{"class":"%s","repo":"%s","action":"%s","command":"%s"}' \
      "$cls" "$(esc "$name")" "$(esc "$act")" "$(esc "$cmd")"
    first=0
  done
  printf ']}\n'
  exit 0
fi

echo "── ecosystem + equality reconcile · machine=$MACHINE · $(ts) ──"
echo "   (default is read-only; pass --apply to run the AUTO-SAFE subset)"
for cls in AUTO-SAFE NEEDS-APPROVAL OPERATOR-ONLY; do
  n=0
  for row in "${PLAN[@]:-}"; do [ -n "$row" ] && [ "${row%%$'\t'*}" = "$cls" ] && n=$((n+1)); done
  echo
  echo "### $cls ($n)"
  for row in "${PLAN[@]:-}"; do
    [ -z "$row" ] && continue
    IFS=$'\t' read -r rcls name act cmd <<<"$row"
    [ "$rcls" = "$cls" ] || continue
    printf '  • [%s] %s\n      $ %s\n' "$name" "$act" "$cmd"
  done
done

# ── apply (AUTO-SAFE only) ───────────────────────────────────────────────────
if [ "$APPLY" = 1 ]; then
  echo
  echo "── applying AUTO-SAFE actions ──"
  rc=0
  for row in "${PLAN[@]:-}"; do
    [ -z "$row" ] && continue
    IFS=$'\t' read -r rcls name act cmd <<<"$row"
    [ "$rcls" = "AUTO-SAFE" ] || continue
    # Equality-refresh actions funnel through the canonical cron ONCE below — don't run
    # them per-item (that would re-collect+rebuild N times).
    if printf '%s' "$cmd" | grep -q "$CRON"; then
      echo "  ~ defer to canonical equality refresh: [$name] $act"; continue
    fi
    echo "  + [$name] $act"
    if ! bash -c "$cmd"; then echo "    ! failed: $cmd" >&2; rc=1; fi
  done
  if [ "$DO_EQUALITY" = 1 ]; then
    echo "  + refresh equality (fetch + equality-matrix-cron.sh: collect this box + rebuild matrix)"
    git -C "$REPO_ROOT" fetch origin main >/dev/null 2>&1 || true
    bash "$CRON" || rc=1
    echo "    (to publish the live Pages link, run: bash '$REFRESH')"
  fi
  exit "$rc"
fi
exit 0
