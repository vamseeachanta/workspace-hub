#!/usr/bin/env bash
# check-equality-artifacts-out-of-tree.sh — Level-2 regression guard for #3702.
#
# Fails when an edit re-points equality GENERATION back at a tracked path inside the
# checkout. That regression is silent and expensive: the generated artifacts become
# tracked-and-modified, `git pull --ff-only` starts aborting on them, behind_main
# ratchets on every peer publish, and is_stale() stamps STALE-CHECKOUT across every
# dimension of the affected machine while all crons keep reporting success.
#
# Deliberately does NOT check the PUBLISHED surface: `.claude/state/equality-*.yaml` and
# `docs/reports/*machine-equality-matrix.html` must stay TRACKED on main (GitHub Pages
# reads the alias via scripts/build_pages.py). Only the generation target moved.
#
# Windows is explicitly exempt in Phase 1: scripts/windows/equality-report.ps1 and
# scripts/readiness/collect-equality.ps1 PIN the seam back to the in-tree paths on
# purpose, so their `.claude\state` / `docs\reports` literals are correct, not a defect.
#
# Usage: check-equality-artifacts-out-of-tree.sh [--root <dir>]
# Exit 0 = compliant. Exit 1 = a generator writes into the tree.
set -uo pipefail

ROOT=""
for ((i=1; i<=$#; i++)); do
  case "${!i}" in
    --root) j=$((i+1)); ROOT="${!j:-}";;
  esac
done
if [[ -z "$ROOT" ]]; then
  _sd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  ROOT="$(git -C "$_sd" rev-parse --show-toplevel 2>/dev/null)"
  [[ -n "$ROOT" ]] || ROOT="$(cd "$_sd/.." && pwd)"
fi

FAILED=0
fail() { echo "check-equality-artifacts-out-of-tree: FAIL — $*" >&2; FAILED=1; }
ok()   { echo "  ok: $*"; }

COLLECT="$ROOT/scripts/readiness/collect-equality.sh"
BUILDER="$ROOT/scripts/readiness/build-equality-matrix.py"
PUBLISH="$ROOT/scripts/readiness/publish-equality.sh"
SEAM_LIB="$ROOT/scripts/readiness/lib/eq-seam.sh"
CURATION="$ROOT/scripts/curation/curate-session-memory.sh"

echo "check-equality-artifacts-out-of-tree: root=$ROOT"

# ── 1. the shared seam resolver exists and defaults out of tree ───────────────
if [[ ! -f "$SEAM_LIB" ]]; then
  fail "scripts/readiness/lib/eq-seam.sh is missing — the seam has no single source of truth"
elif ! grep -q 'XDG_STATE_HOME' "$SEAM_LIB" || ! grep -q 'workspace-hub/equality' "$SEAM_LIB"; then
  fail "lib/eq-seam.sh no longer defaults to \${XDG_STATE_HOME:-\$HOME/.local/state}/workspace-hub/equality"
else
  ok "lib/eq-seam.sh defaults out of tree"
fi

# ── 2. collect-equality.sh writes through the seam, not into the checkout ─────
if [[ ! -f "$COLLECT" ]]; then
  fail "scripts/readiness/collect-equality.sh is missing"
else
  out_assign="$(grep -E '^EQ_OUT_DIR=' "$COLLECT" || true)"
  if [[ -z "$out_assign" ]]; then
    fail "collect-equality.sh has no EQ_OUT_DIR seam assignment"
  elif ! printf '%s' "$out_assign" | grep -q 'eq_state_dir'; then
    fail "collect-equality.sh: EQ_OUT_DIR is not resolved through eq_state_dir() — got: ${out_assign}"
  elif printf '%s' "$out_assign" | grep -qE '\$\{?WS\}?|\.claude'; then
    fail "collect-equality.sh: EQ_OUT_DIR points back inside the checkout — got: ${out_assign}"
  else
    ok "collect-equality.sh EQ_OUT_DIR resolves through the seam"
  fi
  if ! grep -qE '^OUT="\$\{EQ_OUT_DIR\}/equality-\$\{MACHINE\}\.yaml"' "$COLLECT"; then
    fail "collect-equality.sh: the equality yaml write target is not \${EQ_OUT_DIR}/equality-\${MACHINE}.yaml"
  else
    ok "collect-equality.sh writes equality-<machine>.yaml into the seam"
  fi
fi

# ── 3. build-equality-matrix.py renders through the seam ─────────────────────
if [[ ! -f "$BUILDER" ]]; then
  fail "scripts/readiness/build-equality-matrix.py is missing"
else
  if grep -qE '^REPORTS = REPO */ *"docs"' "$BUILDER"; then
    fail "build-equality-matrix.py: REPORTS is derived from REPO again — renders land in the tracked tree"
  else
    ok "build-equality-matrix.py REPORTS is not REPO-derived"
  fi
  for needle in 'def resolve_report_out' 'def resolve_state_inputs' 'XDG_STATE_HOME' 'workspace-hub'; do
    grep -q "$needle" "$BUILDER" \
      || fail "build-equality-matrix.py: missing seam element '${needle}'"
  done
  grep -qE 'report_dir *= *resolve_report_out\(\)' "$BUILDER" \
    || fail "build-equality-matrix.py: the HTML write does not go through resolve_report_out()"
  grep -qE 'out *= *report_dir */' "$BUILDER" \
    || fail "build-equality-matrix.py: the dated report is not written under resolve_report_out()"
fi

# ── 4. publish-equality.sh reads the seam and fails loud when it is empty ────
if [[ ! -f "$PUBLISH" ]]; then
  fail "scripts/readiness/publish-equality.sh is missing"
else
  grep -q 'EQ_LOCAL_DIR="\$(eq_state_dir' "$PUBLISH" \
    || fail "publish-equality.sh does not resolve local evidence through the seam"
  grep -q 'no local equality evidence' "$PUBLISH" \
    || fail "publish-equality.sh does not fail loud on an empty seam dir (silent dark-box risk)"
  grep -q '\-\-state-dir "\$WT/\.claude/state"' "$PUBLISH" \
    || fail "publish-equality.sh's --rebuild render does not pin --state-dir to the worktree"
  grep -qE 'for f in "\$EQ_LOCAL_DIR"/equality-\*\.yaml' "$PUBLISH" \
    || fail "publish-equality.sh still iterates the tracked working tree for local evidence"
  [[ "$FAILED" == 0 ]] && ok "publish-equality.sh reads the seam, pins the render, fails loud when empty"
fi

# ── 5. no collection entry point pins the seam back into the checkout ────────
for f in "$CURATION" "$ROOT/scripts/readiness/equality-matrix-cron.sh"; do
  [[ -f "$f" ]] || continue
  if grep -nE '^[^#]*(EQ_STATE_DIR|EQ_REPORT_DIR)=.*(\$\{?WS\}?|\$\{?REPO_ROOT\}?|\.claude/state|docs/reports)' "$f"; then
    fail "$(basename "$f") pins the generation seam back into the tracked tree"
  fi
done
ok "no Linux/macOS collection entry point pins the seam in-tree"

if [[ "$FAILED" != 0 ]]; then
  echo "check-equality-artifacts-out-of-tree: FAILED (see #3702)" >&2
  exit 1
fi
echo "check-equality-artifacts-out-of-tree: PASS"
