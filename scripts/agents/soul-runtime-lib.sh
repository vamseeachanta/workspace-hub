#!/usr/bin/env bash
# Shared helpers for SOUL runtime generation and drift checks.

append_codex_agents_extras() {
    local repo_root="$1"
    local out="$2"
    local skills_root="${repo_root}/.claude/skills"
    {
        echo
        echo "---"
        echo
        echo "## Skill index"
        echo "> Codex has no native skill loader — enumerate + USE these. Indexed by FAMILY (top-level \`.claude/skills/<family>/\`); run \`ls .claude/skills/<family>/*/SKILL.md\` to list a family's skills. Workspace \`.claude/skills/\` wins over \`.agents/skills/\` and \`~/.claude/plugins/\`. Mandatory lifecycle skills: \`coordination/issue-planning-mode\`, \`coordination/pre-completion-cleanup-audit\`. Auto-generated — do not hand-edit."
        echo
        if [[ -d "${skills_root}" ]]; then
            # FAMILY-level index (~50 lines) — NOT one line per nested SKILL.md (1000+),
            # and archive dirs excluded, so the always-loaded artifact stays compact.
            for fam in "${skills_root}"/*/; do
                [[ -d "${fam}" ]] || continue
                local famname ds cnt
                famname=$(basename "${fam}")
                [[ "${famname}" == _* ]] && continue
                if [[ -f "${fam}SKILL.md" ]]; then
                    ds=$(sed -n 's/^description:[[:space:]]*//p' "${fam}SKILL.md" 2>/dev/null | head -1)
                    ds=${ds#\"}; ds=${ds%\"}
                    echo "- **${famname}** — $(printf '%s' "${ds}" | cut -c1-130)"
                else
                    cnt=$(find "${fam}" -name SKILL.md -not -path '*_archive*' 2>/dev/null | wc -l | tr -d ' ')
                    echo "- **${famname}/** — ${cnt} skill(s); \`ls .claude/skills/${famname}/*/SKILL.md\` to enumerate"
                fi
            done
        fi
        echo
        echo "## Universal rules (inlined for Codex)"
        echo "> Claude reads .claude/rules/ natively; these are inlined here because Codex has no native rules loader. Domain/Claude-only rules (goal-invocation, calc-citation, wiki-routing) stay path-references."
        echo
        echo "### coding-style"
        cat "${repo_root}/.claude/rules/coding-style.md"
        echo
        echo "### patterns"
        cat "${repo_root}/.claude/rules/patterns.md"
    } >> "${out}"
}
