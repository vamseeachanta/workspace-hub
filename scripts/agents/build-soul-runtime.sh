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
#
# Outputs (built; committed for review):
#   config/agents/hermes/SOUL.runtime.md
#   config/agents/claude/SOUL.runtime.md
#   config/agents/codex/SOUL.runtime.md
#   config/agents/codex/AGENTS.runtime.md   (Codex CLI loads ~/.codex/AGENTS.md per existing convention)
#   config/agents/gemini/SOUL.runtime.md
#
# Idempotent: re-running with no source changes produces identical outputs.
# Drift detection: scripts/enforcement/check-soul-runtime-drift.sh.
#
# Refs: workspace-hub#2719 Phase 3.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SHARED="${REPO_ROOT}/config/agents/SHARED_SOUL.md"
# Output base — overridable so the drift checker can rebuild via THIS script into a
# tmp tree (no inline-emit duplication). Sources always read from REPO_ROOT.
OUT_BASE="${SOUL_RUNTIME_OUT_BASE:-${REPO_ROOT}/config/agents}"

[[ -f "${SHARED}" ]] || { echo "ERROR: ${SHARED} not found" >&2; exit 1; }

emit_runtime() {
    local provider="$1" delta_file="$2" out_file="$3"
    local delta_path="${REPO_ROOT}/config/agents/${provider}/${delta_file}"
    local out_path="${OUT_BASE}/${provider}/${out_file}"
    mkdir -p "$(dirname "${out_path}")"

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
append_codex_agents_extras() {
    local out="${OUT_BASE}/codex/AGENTS.runtime.md"
    local skills_root="${REPO_ROOT}/.claude/skills"
    [[ -f "${out}" ]] || { echo "SKIP codex extras — AGENTS.runtime.md missing"; return; }
    {
        echo
        echo "---"
        echo
        echo "## Skill index"
        echo "> Codex has no native skill loader — enumerate + USE these. Indexed by FAMILY (top-level \`.claude/skills/<family>/\`): each \`name/\` entry shows a recursive skill count + a \`find\` command to enumerate it; a bare \`name\` entry is itself a single leaf skill (description shown). Workspace \`.claude/skills/\` wins over \`.agents/skills/\` and \`~/.claude/plugins/\`. Mandatory lifecycle skills: \`coordination/issue-planning-mode\`, \`coordination/pre-completion-cleanup-audit\`. Auto-generated from live \`.claude/skills/\` — do not hand-edit; rebuild via build-soul-runtime.sh after skill changes."
        echo
        if [[ -d "${skills_root}" ]]; then
            # FAMILY-level index (~50 lines) — NOT one line per nested SKILL.md (1000+),
            # and archive dirs excluded, so the always-loaded artifact stays compact.
            for fam in "${skills_root}"/*/; do
                [[ -d "${fam}" ]] || continue
                local famname ds cnt
                famname=$(basename "${fam}")
                [[ "${famname}" == _* ]] && continue       # skip _archive and friends
                if [[ -f "${fam}SKILL.md" ]]; then          # family dir is itself a leaf skill
                    ds=$(sed -n 's/^description:[[:space:]]*//p' "${fam}SKILL.md" 2>/dev/null | head -1)
                    ds=${ds#\"}; ds=${ds%\"}
                    echo "- **${famname}** — $(printf '%s' "${ds}" | cut -c1-130)"
                else
                    cnt=$(find "${fam}" -name SKILL.md -not -path '*_archive*' 2>/dev/null | wc -l | tr -d ' ')
                    [[ "${cnt}" -eq 0 ]] && continue   # F5: skip empty families (no noise)
                    # F2: enumerate hint is RECURSIVE to match the recursive count (families
                    # nest skills >1 level deep — a one-level `ls` undercounts badly).
                    echo "- **${famname}/** — ${cnt} skill(s); \`find .claude/skills/${famname} -name SKILL.md -not -path '*_archive*'\` to enumerate"
                fi
            done
        fi
        echo
        echo "## Universal rules (inlined for Codex)"
        echo "> Claude reads .claude/rules/ natively; these are inlined here because Codex has no native rules loader. Domain/Claude-only rules (goal-invocation, calc-citation, wiki-routing) stay path-references."
        echo
        echo "### coding-style"
        cat "${REPO_ROOT}/.claude/rules/coding-style.md"
        echo
        echo "### patterns"
        cat "${REPO_ROOT}/.claude/rules/patterns.md"
    } >> "${out}"
    echo "APPENDED codex/AGENTS.runtime.md (skill index + universal rules)"
}

emit_runtime hermes SOUL.md       SOUL.runtime.md
emit_runtime claude SOUL.delta.md SOUL.runtime.md
emit_runtime codex  SOUL.delta.md SOUL.runtime.md
emit_runtime codex  SOUL.delta.md AGENTS.runtime.md
append_codex_agents_extras
emit_runtime gemini SOUL.delta.md SOUL.runtime.md
