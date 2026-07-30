#!/usr/bin/env bash
# build-soul-runtime.sh — Materialize per-provider SOUL.runtime.md artifacts.
#
# Concatenates config/agents/SHARED_SOUL.md + per-provider delta into a
# single committed runtime file that runtimes symlink to via
# scripts/agents/install-soul-runtime.sh.
#
# Sources (canonical):
#   config/agents/SHARED_SOUL.md
#   config/agents/hermes/SOUL.md         (Hermes uses SOUL.md directly as the delta)
#   config/agents/claude/SOUL.delta.md
#   config/agents/codex/SOUL.delta.md
#   config/agents/gemini/SOUL.delta.md
#   config/agents/agy/SOUL.delta.md
#
# Outputs (built; committed for review):
#   config/agents/hermes/SOUL.runtime.md
#   config/agents/claude/SOUL.runtime.md
#   config/agents/codex/SOUL.runtime.md
#   config/agents/codex/AGENTS.runtime.md   (Codex CLI loads ~/.codex/AGENTS.md per existing convention)
#   config/agents/gemini/SOUL.runtime.md
#   config/agents/agy/SOUL.runtime.md
#
# Idempotent: re-running with no source changes produces identical outputs.
# Drift detection: scripts/enforcement/check-soul-runtime-drift.sh.
#
# Refs: workspace-hub#2719 Phase 3.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SHARED="${REPO_ROOT}/config/agents/SHARED_SOUL.md"
source "${REPO_ROOT}/scripts/agents/soul-runtime-lib.sh"

[[ -f "${SHARED}" ]] || { echo "ERROR: ${SHARED} not found" >&2; exit 1; }

emit_runtime() {
    local provider="$1" delta_file="$2" out_file="$3"
    local delta_path="${REPO_ROOT}/config/agents/${provider}/${delta_file}"
    local out_path="${REPO_ROOT}/config/agents/${provider}/${out_file}"

    if [[ ! -f "${delta_path}" ]]; then
        echo "SKIP ${provider}/${out_file} — source ${delta_file} missing"
        return
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
    } > "${out_path}"
    echo "BUILT ${provider}/${out_file} ($(wc -l < "${out_path}") lines)"
}

# Codex-only post-emit append (#2841 Phase B): a Skill index + inlined UNIVERSAL rules.
# Applied to AGENTS.runtime.md ONLY — NOT codex/claude SOUL.runtime.md (F3 divergence).
# emit_runtime overwrites AGENTS.runtime.md each build, so this append is idempotent.
append_codex_agents_extras_to_runtime() {
    local out="${REPO_ROOT}/config/agents/codex/AGENTS.runtime.md"
    [[ -f "${out}" ]] || { echo "SKIP codex extras — AGENTS.runtime.md missing"; return; }
    append_codex_agents_extras "${REPO_ROOT}" "${out}"
    echo "APPENDED codex/AGENTS.runtime.md (skill index + universal rules)"
}

emit_runtime hermes SOUL.md       SOUL.runtime.md
emit_runtime claude SOUL.delta.md SOUL.runtime.md
emit_runtime codex  SOUL.delta.md SOUL.runtime.md
emit_runtime codex  SOUL.delta.md AGENTS.runtime.md
append_codex_agents_extras_to_runtime
emit_runtime gemini SOUL.delta.md SOUL.runtime.md
emit_runtime agy    SOUL.delta.md SOUL.runtime.md
