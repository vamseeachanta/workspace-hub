#!/usr/bin/env bash
# check-soul-runtime-drift.sh — Verify committed SOUL.runtime.md / AGENTS.runtime.md
# artifacts match a fresh rebuild from canonical sources.
#
# Level-2 enforcement per .claude/rules/patterns.md. Hookable into pre-commit
# OR daily cron. Exits non-zero on drift (rebuilt content != committed content).
#
# Drift means someone edited a SHARED_SOUL.md / SOUL.md / SOUL.delta.md source
# without re-running scripts/agents/build-soul-runtime.sh and committing the
# new runtime artifact alongside.
#
# Usage:
#   scripts/enforcement/check-soul-runtime-drift.sh           # human-readable diff
#   scripts/enforcement/check-soul-runtime-drift.sh --quiet   # exit code only
#
# Refs: workspace-hub#2719 Phase 3.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

# Mirror the build script's emit logic into a tmp tree so we can diff
# without mutating the committed artifacts.
SHARED="${REPO_ROOT}/config/agents/SHARED_SOUL.md"
[[ -f "${SHARED}" ]] || { echo "ERROR: ${SHARED} not found" >&2; exit 2; }

drift_count=0

check_one() {
    local provider="$1" delta_file="$2" runtime_file="$3"
    local delta_path="${REPO_ROOT}/config/agents/${provider}/${delta_file}"
    local committed_path="${REPO_ROOT}/config/agents/${provider}/${runtime_file}"
    local rebuilt_path="${TMPDIR}/${provider}-${runtime_file}"

    if [[ ! -f "${delta_path}" ]]; then
        return 0
    fi
    if [[ ! -f "${committed_path}" ]]; then
        echo "DRIFT  ${provider}/${runtime_file} — committed artifact missing; run build-soul-runtime.sh"
        drift_count=$((drift_count + 1))
        return 0
    fi

    {
        echo "<!-- BUILT by scripts/agents/build-soul-runtime.sh — edit ${delta_file} or SHARED_SOUL.md, not this file. -->"
        echo "<!-- Refs: workspace-hub#2719 Phase 3. -->"
        echo
        cat "${SHARED}"
        echo
        echo "---"
        echo
        cat "${delta_path}"
    } > "${rebuilt_path}"

    if ! diff -q "${committed_path}" "${rebuilt_path}" > /dev/null 2>&1; then
        echo "DRIFT  ${provider}/${runtime_file} — committed artifact differs from rebuilt sources"
        if [[ "${QUIET}" -eq 0 ]]; then
            diff -u "${committed_path}" "${rebuilt_path}" | head -40
        fi
        drift_count=$((drift_count + 1))
    elif [[ "${QUIET}" -eq 0 ]]; then
        echo "OK     ${provider}/${runtime_file}"
    fi
}

check_one hermes SOUL.md       SOUL.runtime.md
check_one claude SOUL.delta.md SOUL.runtime.md
check_one codex  SOUL.delta.md SOUL.runtime.md
check_one codex  SOUL.delta.md AGENTS.runtime.md
check_one gemini SOUL.delta.md SOUL.runtime.md

# ── Auto-load wiring check (workspace-hub#2725) ──
# CLAUDE.md and GEMINI.md must inline-import their per-provider runtime
# artifacts via @file.md import syntax (Claude Code @file, Gemini CLI @file.md).
# Without this, the 14+5 Must-Fire Rules don't reach Claude/Gemini sessions.
check_autoload_wiring() {
    local file="$1" expected="$2"
    local full_path="${REPO_ROOT}/${file}"
    if [[ ! -f "${full_path}" ]]; then
        echo "DRIFT  ${file} — file missing; cannot verify auto-load wiring"
        drift_count=$((drift_count + 1))
        return 0
    fi
    if ! grep -Fxq "${expected}" "${full_path}"; then
        echo "DRIFT  ${file} missing auto-load directive: ${expected}"
        drift_count=$((drift_count + 1))
    elif [[ "${QUIET}" -eq 0 ]]; then
        echo "OK     ${file} auto-load wired"
    fi
}

check_autoload_wiring CLAUDE.md "@config/agents/claude/SOUL.runtime.md"
check_autoload_wiring GEMINI.md "@config/agents/gemini/SOUL.runtime.md"

if [[ "${drift_count}" -gt 0 ]]; then
    echo
    echo "DRIFT DETECTED: ${drift_count} artifact(s) out of sync."
    echo "Fix: bash scripts/agents/build-soul-runtime.sh && git add config/agents/**/*.runtime.md"
    exit 1
fi

[[ "${QUIET}" -eq 0 ]] && echo "All SOUL runtime artifacts up to date."
exit 0
