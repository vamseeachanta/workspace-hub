#!/usr/bin/env bash
# refresh-equality-matrix.sh --- operator-driven refresh of THIS machine's equality
# snapshot AND the live machine-equality matrix (Linux/macOS side; #2801 / #2998).
#
# OS-paired twin of refresh-equality-matrix.ps1. The manual equivalent of the scheduled
# path: it runs the canonical builder (equality-matrix-cron.sh: collect-equality.sh +
# build-equality-matrix.py) on a fresh main, then commits+pushes the state yaml + matrix
# HTML so the operator can refresh the LIVE GitHub Pages matrix immediately rather than
# waiting for repo-sync to pick it up.
#
# Divergence note (intentional, mirrors the OS split): on Windows equality-report.ps1
# self-pushes because Windows has no repo-sync; on Linux the SCHEDULED matrix push is owned
# by repo-sync, and equality-matrix-cron.sh only builds. This wrapper adds the commit+push
# ONLY for the manual on-demand case, scoped by pathspec to the equality artifacts so it
# cannot sweep unrelated working-tree changes.
#
# Usage: refresh-equality-matrix.sh [--machine <label>]
set -uo pipefail

MACHINE=""
for ((i=1; i<=$#; i++)); do
  case "${!i}" in
    --machine) j=$((i+1)); MACHINE="${!j:-}";;
  esac
done

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "refresh-equality-matrix: not inside a git checkout" >&2
  exit 1
fi
cd "$REPO_ROOT" || { echo "refresh-equality-matrix: cannot cd to repo root" >&2; exit 1; }

step() { printf '\n=== %s ===\n' "$1"; }

# ------ 1/3  fresh main ------------------------------------------------------------------
step "1/3  Fresh main (switch + pull --rebase --autostash)"
branch="$(git branch --show-current)"
if [[ "$branch" != "main" ]]; then
  git switch main || { echo "git switch main failed" >&2; exit 1; }
fi
git pull --rebase --autostash origin main || { echo "git pull failed" >&2; exit 1; }

# ------ 2/3  collect + build (canonical, single-sourced) ---------------------------------
step "2/3  equality-matrix-cron.sh (collect + build)"
cron_args=()
# equality-matrix-cron.sh has no --machine flag; if a label override is needed it flows
# through the EQ env seam / collect-equality.sh autodetect. Pass-through kept for parity.
if [[ -n "$MACHINE" ]]; then
  echo "note: --machine '$MACHINE' relies on collect-equality.sh autodetect on Linux" >&2
fi
bash "$REPO_ROOT/scripts/readiness/equality-matrix-cron.sh" "${cron_args[@]}" \
  || { echo "equality-matrix-cron.sh failed" >&2; exit 1; }

# ------ 3/3  commit + push the equality artifacts (manual on-demand only) ----------------
step "3/3  Commit + push equality artifacts"
today="$(date +%F)"
artifacts=(
  "docs/reports/${today}-machine-equality-matrix.html"
  "docs/reports/machine-equality-matrix.html"
)
# Stage the matrix HTML + any changed per-machine state yaml (scoped; no blanket add).
git add -- "${artifacts[@]}" 2>/dev/null || true
while IFS= read -r f; do
  [[ -n "$f" ]] && git add -- "$f"
done < <(git status --porcelain -- '.claude/state/equality-*.yaml' | awk '{print $2}')

if git diff --cached --quiet; then
  echo "No equality changes to commit (canonical payload unchanged)."
else
  host="$(hostname | tr '[:upper:]' '[:lower:]')"
  git commit -m "chore: equality report from ${host}" || { echo "commit failed" >&2; exit 1; }
  git push origin main || { echo "push failed; left local commit for repo-sync retry" >&2; exit 1; }
  echo "Pushed equality artifacts; GitHub Pages will redeploy."
fi

# ------ verify --------------------------------------------------------------------------
step "Provenance + commit"
echo "--- provenance (expect dirty: false, behind_main: 0, ahead_main: 0, origin_ref_age_h 0-48)"
grep -E 'dirty|behind_main|ahead_main|origin_ref_age_h' .claude/state/equality-*.yaml 2>/dev/null || true
echo "--- last commit"
git log -1 --oneline
echo "--- status"
git status -sb

echo ""
echo "DONE. GitHub Pages redeploys in ~1-2 min:"
echo "  https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html"
