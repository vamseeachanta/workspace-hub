#!/usr/bin/env bash
# install-hooks.sh — Install enforcement environment and wire learning pipeline into git hooks
# Issue: #2027
#
# Idempotent: safe to run multiple times.
#
# What it does:
# 1. Copies enforcement-env.sh to .git/hooks/enforcement-env
# 2. Wires enforcement-env sourcing into pre-commit (if not already present)
# 3. Wires stage-prompt drift guard into pre-push (if not already present)
# 4. Wires post-commit-learnings.sh into post-commit (fixes dead code after exit 0)
#
# Usage:
#   bash scripts/enforcement/install-hooks.sh
#   bash scripts/enforcement/install-hooks.sh --dry-run

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
  esac
done

log() { echo "[install-hooks] $1"; }

# ── Step 1: Install enforcement-env ─────────────────────────────────────
ENFORCEMENT_SRC="${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"
ENFORCEMENT_DST="${REPO_ROOT}/.git/hooks/enforcement-env"

if [[ -f "$ENFORCEMENT_SRC" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY-RUN: Would copy enforcement-env.sh -> .git/hooks/enforcement-env"
  else
    cp "$ENFORCEMENT_SRC" "$ENFORCEMENT_DST"
    chmod 644 "$ENFORCEMENT_DST"
    log "OK: Installed enforcement-env to .git/hooks/"
  fi
else
  log "SKIP: enforcement-env.sh not found at ${ENFORCEMENT_SRC}"
fi

# ── Step 2: Wire enforcement-env into pre-commit ────────────────────────
PRE_COMMIT="${REPO_ROOT}/.git/hooks/pre-commit"

if [[ -f "$PRE_COMMIT" ]]; then
  if grep -q "enforcement-env" "$PRE_COMMIT" 2>/dev/null; then
    log "OK: enforcement-env already wired into pre-commit"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would add enforcement-env sourcing to pre-commit"
    else
      # Insert after the PATH export line
      sed -i '/^export PATH=/a\
\
# Source enforcement environment (#2027)\
ENFORCEMENT_ENV="${REPO_ROOT}/.git/hooks/enforcement-env"\
if [[ -f "${ENFORCEMENT_ENV}" ]]; then\
  source "${ENFORCEMENT_ENV}"\
fi' "$PRE_COMMIT"
      log "OK: Wired enforcement-env into pre-commit"
    fi
  fi
else
  log "SKIP: pre-commit hook not found"
fi

# ── Step 3: Wire full pre-push enforcement chain (#2128, #3781) ───────
# Order matters: enforcement-env FIRST — it exports REVIEW_GATE_STRICT=1, and
# the review wrapper defaults that to 0, so a later source leaves review
# ADVISORY. Blocks are INSERTED at the hook's extension point, never appended
# past the end: the hook terminates in an unconditional `exit`, and anything
# below it never runs. Four blocks sat there for months while this script
# logged "OK: Wired ..." for each (#3781).
PRE_PUSH="${REPO_ROOT}/.git/hooks/pre-push"
SENTINEL='# <<INSTALL_HOOKS_EXTENSION_POINT>>'

# Everything above the sentinel — the reachable region of the hook.
reachable_region() {
  sed "/<<INSTALL_HOOKS_EXTENSION_POINT>>/q" "$PRE_PUSH"
}

# $1 = grep marker identifying the block, $2 = file holding the block text
insert_block() {
  local marker="$1" block_file="$2" label="$3"

  if ! grep -q "INSTALL_HOOKS_EXTENSION_POINT" "$PRE_PUSH" 2>/dev/null; then
    echo "FATAL: no extension point in ${PRE_PUSH}." >&2
    echo "  Refusing to append — appended blocks land below the terminal exit" >&2
    echo "  and never run. Reinstall the tracked hook (scripts/hooks/pre-push.sh)." >&2
    return 1
  fi

  # Reachability-aware idempotence. A plain `grep -q "$marker" "$PRE_PUSH"`
  # is what made #3781 permanent: it reported "already wired" for a block
  # sitting below the exit, so re-running could never repair it.
  if reachable_region | grep -q "$marker"; then
    log "OK: ${label} already wired into pre-push (reachable)"
    return 0
  fi

  if grep -q "$marker" "$PRE_PUSH" 2>/dev/null; then
    log "WARN: ${label} present but UNREACHABLE — re-wiring above the extension point"
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY-RUN: Would wire ${label} into pre-push"
    return 0
  fi

  local tmp; tmp="$(mktemp)"
  awk -v blockfile="$block_file" '
    /<<INSTALL_HOOKS_EXTENSION_POINT>>/ && !done {
      while ((getline line < blockfile) > 0) print line
      close(blockfile); done = 1
    }
    { print }
  ' "$PRE_PUSH" > "$tmp"

  if ! bash -n "$tmp"; then
    echo "FATAL: insertion of ${label} produced invalid bash — not written" >&2
    rm -f "$tmp"; return 1
  fi
  cat "$tmp" > "$PRE_PUSH"; rm -f "$tmp"
  log "OK: Wired ${label} into pre-push"
}

# Remove any enforcement stranded below the hook's terminal exit. Inserting the
# live copy above is not enough on its own: the dead copy stays behind, keeps
# matching a naive grep, and misleads the next reader into thinking the gate is
# wired twice. Blocks below an unconditional exit are dead by definition, so
# truncating there is well-defined rather than a heuristic.
strip_dead_tail() {
  awk '
    { lines[NR] = $0; if ($0 ~ /^exit([[:space:]]|$)/) last_exit = NR }
    END {
      end = (last_exit ? last_exit : NR)
      for (i = 1; i <= end; i++) print lines[i]
    }
  ' "$PRE_PUSH" > "${PRE_PUSH}.tmp" && mv "${PRE_PUSH}.tmp" "$PRE_PUSH"
}

if [[ -f "$PRE_PUSH" ]]; then
  # Detect the #3781 state: enforcement present, but below the terminal exit.
  if grep -q "INSTALL_HOOKS_EXTENSION_POINT" "$PRE_PUSH" 2>/dev/null \
     && [[ -n "$(awk '/^exit([[:space:]]|$)/{f=NR} END{print (f?f:"")}' "$PRE_PUSH")" ]] \
     && awk '/^exit([[:space:]]|$)/{seen=1; next} seen' "$PRE_PUSH" \
        | grep -qE "enforcement-env|scripts/enforcement/|scripts/sync/|\.claude/hooks/"; then
    log "WARN: enforcement found below the terminal exit (#3781) — removing the dead tail"
    strip_dead_tail
  fi

  _blk="$(mktemp -d)"

  cat > "${_blk}/env" <<'EOF'

# ── Enforcement environment (installed by install-hooks.sh #2128) ──────
# MUST precede gates whose strictness it sets (#3781).
ENFORCEMENT_ENV="${REPO_ROOT}/.git/hooks/enforcement-env"
if [[ -f "${ENFORCEMENT_ENV}" ]]; then
  source "${ENFORCEMENT_ENV}"
fi
EOF

  cat > "${_blk}/review" <<'EOF'

# ── Review gate (installed by install-hooks.sh #2128) ──────────────────
REVIEW_GATE="${REPO_ROOT}/scripts/enforcement/require-review-on-push.sh"
if [[ -f "$REVIEW_GATE" ]]; then
  bash "$REVIEW_GATE" || OVERALL_EXIT=1
fi
EOF

  cat > "${_blk}/drift" <<'EOF'

# ── Stage prompt drift guard (installed by install-hooks.sh) ─────────────
STAGE_PROMPT_DRIFT_GATE="${REPO_ROOT}/scripts/enforcement/require-stage-prompt-drift.sh"
if [[ -f "$STAGE_PROMPT_DRIFT_GATE" ]]; then
  bash "$STAGE_PROMPT_DRIFT_GATE" || OVERALL_EXIT=1
fi
EOF

  cat > "${_blk}/size" <<'EOF'

# ── State-file size guard pre-push (#2070) ───────────────────────────────
# Reads the push refspecs from ITS OWN stdin. The hook already consumed git's
# stdin into PUSH_LINES, so replay them — without this the guard silently
# falls back to an inferred ref and scans the wrong range (#3781).
STATE_SIZE_PREPUSH="${REPO_ROOT}/.claude/hooks/check-state-file-size-prepush.sh"
if [[ -f "$STATE_SIZE_PREPUSH" ]]; then
  printf '%s\n' "${PUSH_LINES[@]}" | bash "$STATE_SIZE_PREPUSH" || OVERALL_EXIT=1
fi
EOF

  cat > "${_blk}/cadence" <<'EOF'

# ── Cadence-helper sync check (wed#309) ──────────────────────────────────
CADENCE_SYNC="${REPO_ROOT}/scripts/sync/sync-cadence-helper.sh"
if [[ -f "$CADENCE_SYNC" ]]; then
  bash "$CADENCE_SYNC" || OVERALL_EXIT=1
fi
EOF

  _install_rc=0
  insert_block "enforcement-env"                   "${_blk}/env"     "enforcement-env" || _install_rc=$?
  insert_block "require-review-on-push.sh"         "${_blk}/review"  "review gate" || _install_rc=$?
  insert_block "require-stage-prompt-drift.sh"     "${_blk}/drift"   "stage prompt drift guard" || _install_rc=$?
  insert_block "check-state-file-size-prepush.sh"  "${_blk}/size"    "state-file size guard" || _install_rc=$?
  insert_block "sync-cadence-helper.sh"            "${_blk}/cadence" "cadence-helper sync check" || _install_rc=$?

  rm -rf "$_blk"
  chmod +x "$PRE_PUSH"
  [[ $_install_rc -eq 0 ]] || exit $_install_rc
else
  log "SKIP: pre-push hook not found"
fi

# ── Step 3.5: Wire state-file size guard into pre-commit (#2070) ───────
# Blocks commits that stage oversized files under .claude/state/session-signals/
# (mitigates the 103 MB cost-tracking.jsonl push failure class).
if [[ -f "$PRE_COMMIT" ]]; then
  if grep -q "check-state-file-size-precommit.sh" "$PRE_COMMIT" 2>/dev/null; then
    log "OK: state-file size guard already wired into pre-commit"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would wire state-file size guard into pre-commit"
    else
      cat >> "$PRE_COMMIT" <<'EOF'

# ── State-file size guard (#2070) ──────────────────────────────────────
if [[ -f "${REPO_ROOT}/.claude/hooks/check-state-file-size-precommit.sh" ]]; then
  bash "${REPO_ROOT}/.claude/hooks/check-state-file-size-precommit.sh" || exit 1
fi
EOF
      log "OK: Wired state-file size guard into pre-commit"
    fi
  fi
fi

# ── Step 3.6: Wire conflict-marker check into pre-commit (#2722) ──────
# Inserts the check BEFORE the existing `exit 0` at the end of the early
# enforcement chain. Linux-gated awk-in-place rewrite; macOS/non-Linux
# emits manual-install instructions (Claude r1 finding #6 on BSD sed).
if [[ -f "$PRE_COMMIT" ]]; then
  if grep -q "check-no-conflict-markers" "$PRE_COMMIT" 2>/dev/null; then
    log "OK: conflict-marker check already wired into pre-commit"
  elif [[ "$DRY_RUN" == "1" ]]; then
    log "DRY-RUN: Would wire conflict-marker check into pre-commit"
  elif [[ "$(uname -s)" == "Linux" ]]; then
    tmpfile="$(mktemp)"
    awk '
      /^exit 0$/ && !done {
        print ""
        print "# ── Conflict-marker check (#2722) ──"
        print "if [[ -f \"${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh\" ]]; then"
        print "  bash \"${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh\" || exit 1"
        print "fi"
        print ""
        print
        done = 1
        next
      }
      { print }
    ' "$PRE_COMMIT" > "$tmpfile"
    mv "$tmpfile" "$PRE_COMMIT"
    chmod +x "$PRE_COMMIT"
    log "OK: Wired conflict-marker check into pre-commit"
  else
    log "WARN: non-Linux platform ($(uname -s)) — auto-wiring skipped"
    log "      Add the following block to $PRE_COMMIT before the final 'exit 0':"
    cat <<'EOF'
        # ── Conflict-marker check (#2722) ──
        if [[ -f "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" ]]; then
          bash "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" || exit 1
        fi
EOF
  fi
fi

# ── Step 4: Wire learning pipeline into post-commit ─────────────────────
POST_COMMIT="${REPO_ROOT}/.git/hooks/post-commit"

if [[ -f "$POST_COMMIT" ]]; then
  if grep -q "post-commit-learnings" "$POST_COMMIT" 2>/dev/null; then
    log "OK: learning pipeline already wired into post-commit"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would wire learning pipeline into post-commit (fix dead code)"
    else
      # Remove the dead code after exit 0 and replace with learning pipeline call
      # The post-commit has: exit 0 \n\n# Track skill...\nbash scripts/hooks/...
      # We need to replace that with: learning pipeline call \n exit 0

      # Create a temporary file with the fix
      tmpfile="$(mktemp)"

      # Process the file: find the "exit 0" that precedes dead code, replace it
      awk '
        /^exit 0$/ {
          # Check if next lines are dead code (track-skill-patches)
          if (!printed_learning) {
            print ""
            print "# ── Post-commit learning pipeline (#2027) ────────────────────────────"
            print "REPO_ROOT=\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)\""
            print "bash \"${REPO_ROOT}/scripts/hooks/post-commit-learnings.sh\" || true"
            print ""
            print "exit 0"
            printed_learning = 1
            skip_dead_code = 1
            next
          }
          print
          next
        }
        skip_dead_code && /^$/ { next }
        skip_dead_code && /^#/ { next }
        skip_dead_code && /^bash/ { next }
        skip_dead_code { skip_dead_code = 0 }
        !skip_dead_code { print }
      ' "$POST_COMMIT" > "$tmpfile"

      cp "$tmpfile" "$POST_COMMIT"
      chmod +x "$POST_COMMIT"
      rm -f "$tmpfile"
      log "OK: Wired learning pipeline into post-commit (fixed dead code)"
    fi
  fi
else
  log "SKIP: post-commit hook not found"
fi

# ── Summary ─────────────────────────────────────────────────────────────
log ""
log "Enforcement hook chain:"
log "  pre-commit -> enforcement-env -> plan-approval-gate"
log "  pre-push -> enforcement-env -> review-gate -> stage-prompt-drift-gate"
log "  post-commit -> auto-push -> learning pipeline -> extract-learnings"
log ""
if [[ "$DRY_RUN" == "1" ]]; then
  log "DRY-RUN mode — no changes made. Remove --dry-run to apply."
fi
