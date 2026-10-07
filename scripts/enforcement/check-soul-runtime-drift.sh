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
# Git hooks export repository bindings; clear them in this child before locating roots.
while IFS= read -r git_binding; do unset "${git_binding}"; done < <(git rev-parse --local-env-vars)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

required_sources=(config/agents/SHARED_SOUL.md config/agents/hermes/SOUL.md
    config/agents/claude/SOUL.delta.md config/agents/codex/SOUL.delta.md
    config/agents/gemini/SOUL.delta.md config/agents/agy/SOUL.delta.md
    scripts/agents/soul-runtime-lib.sh .claude/rules/coding-style.md .claude/rules/patterns.md)
missing=0
for relative in "${required_sources[@]}"; do
    if [[ ! -f "${REPO_ROOT}/${relative}" ]]; then
        echo "DRIFT  ${relative} — required source missing"
        missing=$((missing + 1))
    fi
done
if [[ "${missing}" -gt 0 ]]; then
    echo "DRIFT DETECTED: ${missing} required source(s) missing."
    exit 1
fi
source "${REPO_ROOT}/scripts/agents/soul-runtime-lib.sh"
DRIFT_PARENT="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
DRIFT_TMP="$(mktemp -d "${DRIFT_PARENT}/soul-runtime-drift.XXXXXXXX")"
DRIFT_TMP="$(cd "${DRIFT_TMP}" && pwd -P)"
cleanup() {
    [[ -d "${DRIFT_TMP}" && ! -L "${DRIFT_TMP}" ]] || return 1
    local resolved
    resolved="$(cd "${DRIFT_TMP}" && pwd -P)" || return 1
    [[ "${resolved}" == "${DRIFT_TMP}" && "${resolved%/*}" == "${DRIFT_PARENT}" ]] || return 1
    [[ "${resolved##*/}" == soul-runtime-drift.* && "${resolved}" != "${REPO_ROOT}" ]] || return 1
    rm -rf -- "${resolved}"
}
trap 'cleanup || { echo "WARN retained ${DRIFT_TMP}: cleanup guard declined removal" >&2; exit 1; }' EXIT

# Mirror the build script's emit logic into a tmp tree so we can diff
# without mutating the committed artifacts.
SHARED="${REPO_ROOT}/config/agents/SHARED_SOUL.md"

drift_count=0

check_one() {
    local provider="$1" delta_file="$2" runtime_file="$3"
    local delta_path="${REPO_ROOT}/config/agents/${provider}/${delta_file}"
    local committed_path="${REPO_ROOT}/config/agents/${provider}/${runtime_file}"
    local rebuilt_path="${DRIFT_TMP}/${provider}-${runtime_file}"

    if [[ ! -f "${delta_path}" ]]; then
        echo "DRIFT  ${provider}/${delta_file} — required source missing"
        drift_count=$((drift_count + 1))
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

    if [[ "${provider}" == "codex" && "${runtime_file}" == "AGENTS.runtime.md" ]]; then
        append_codex_agents_extras "${REPO_ROOT}" "${rebuilt_path}"
    fi

    if ! diff -q "${committed_path}" "${rebuilt_path}" > /dev/null 2>&1; then
        echo "DRIFT  ${provider}/${runtime_file} — committed artifact differs from rebuilt sources"
        if [[ "${QUIET}" -eq 0 ]]; then
            # diff exit 1 means differences; consume bounded output without SIGPIPE.
            diff -u "${committed_path}" "${rebuilt_path}" > "${DRIFT_TMP}/detail.diff" || true
            sed -n '1,40p' "${DRIFT_TMP}/detail.diff"
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
check_one agy SOUL.delta.md SOUL.runtime.md

# ── Auto-load wiring check (workspace-hub#2725) ──
# GEMINI.md must inline-import its per-provider runtime artifact via @file.md
# import syntax (Gemini CLI @file.md). Without this, the Must-Fire Rules don't
# reach Gemini sessions.
#
# CLAUDE.md was retired 2026-08-01 (#3743) — AGENTS.md is canonical and there is
# no repository Claude auto-load file to verify. User-root symlinks are separate
# installer/runtime checks; do NOT re-add a repository CLAUDE.md check here.
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

check_autoload_wiring GEMINI.md "@config/agents/gemini/SOUL.runtime.md"

if [[ "${drift_count}" -gt 0 ]]; then
    echo
    echo "DRIFT DETECTED: ${drift_count} artifact(s) out of sync."
    echo "Fix: bash scripts/agents/build-soul-runtime.sh && git add config/agents/**/*.runtime.md"
    exit 1
fi

if [[ "${QUIET}" -eq 0 ]]; then
    echo "All six SOUL runtime artifacts match sources; installed loading is not verified."
    echo "INFO agy/SOUL.runtime.md and codex/SOUL.runtime.md are built reference artifacts."
fi
exit 0
