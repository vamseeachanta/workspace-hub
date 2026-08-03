#!/usr/bin/env bash
# ff-preflight.sh — best-effort, guard-gated fast-forward of the interactive checkout
# before a scheduled equality collection (#3702).
#
# WHY: the Linux/macOS cron path had no freshness preflight at all (Windows has one:
# equality-report.ps1's Confirm-FreshCheckout). Every peer publish moves origin/main, so
# an unattended box drifts further behind on every cycle and is_stale() fail-closes on
# behind_main != 0, stamping STALE-CHECKOUT across all of that machine's dimensions.
#
# DELIBERATELY WEAK. Three guards, and a warn-don't-fail posture:
#   * only on `main`            — never switches or creates a branch
#   * only on a clean tree      — never clobbers operator work ("Dirty work is NEVER
#                                 discarded", reconcile-ecosystem.sh:14)
#   * only `merge --ff-only`    — never a rebase, reset, stash, or ordinary merge
# A genuinely diverged box warns and CONTINUES so it still publishes its evidence; a
# preflight that could block publishing would be worse than the drift it fixes.
#
# HAZARD THIS FILE EXISTS TO AVOID (r1 M3): a fast-forward that replaces
# equality-matrix-cron.sh / collect-equality.sh / publish-equality.sh on disk while bash
# is still reading the running script makes bash execute truncated input. So ff_preflight
# is NEVER called from a script that keeps executing repo code afterwards — it is called
# only from a thin wrapper that `exec`s the real entry point once the merge has landed.
# See scripts/readiness/equality-preflight.sh and
# scripts/curation/session-curation-preflight.sh.

# Run a command under a wall-clock bound when the platform provides one. `timeout` is GNU
# coreutils; macOS ships without it, and a bare call would abort the preflight there.
_ff_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"; else "$@"; fi
}

# ff_preflight <repo-root>  — always returns 0.
ff_preflight() {
  local repo="${1:-}"
  [[ -n "$repo" && -d "$repo" ]] || { echo "ff-preflight: no repo root; skipping" >&2; return 0; }
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 \
    || { echo "ff-preflight: not a git checkout; skipping" >&2; return 0; }

  local branch
  branch="$(git -C "$repo" branch --show-current 2>/dev/null)"
  if [[ "$branch" != "main" ]]; then
    echo "ff-preflight: on '${branch:-<detached>}', not main; skipping (no fetch, no merge)" >&2
    return 0
  fi
  if [[ -n "$(git -C "$repo" status --porcelain --untracked-files=no 2>/dev/null)" ]]; then
    echo "ff-preflight: tracked files modified; skipping (operator work is never discarded)" >&2
    return 0
  fi

  if ! _ff_timeout 120 git -C "$repo" fetch --quiet origin main 2>/dev/null; then
    echo "ff-preflight: fetch failed (offline/transient); continuing on the local ref" >&2
    return 0
  fi
  if ! git -C "$repo" merge --ff-only origin/main >/dev/null 2>&1; then
    echo "ff-preflight: checkout diverged from origin/main; continuing anyway" >&2
  fi
  return 0
}
