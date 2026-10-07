#!/usr/bin/env bash
# Real generation/checking occurs only in a disposable Git fixture.
set -euo pipefail
# Git hooks export repository bindings; clear them in this child before locating roots.
while IFS= read -r git_binding; do unset "${git_binding}"; done < <(git rev-parse --local-env-vars)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SOURCE_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
TEMP_PARENT="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
FIXTURE="$(mktemp -d "${TEMP_PARENT}/soul-runtime-test.XXXXXXXX")"
FIXTURE="$(cd "${FIXTURE}" && pwd -P)"
touch "${FIXTURE}/.owned-soul-runtime-fixture"
cleanup() {
    [[ -d "${FIXTURE}" && ! -L "${FIXTURE}" ]] || return 1
    local resolved
    resolved="$(cd "${FIXTURE}" && pwd -P)" || return 1
    [[ "${resolved}" == "${FIXTURE}" && "${resolved%/*}" == "${TEMP_PARENT}" ]] || return 1
    [[ "${resolved##*/}" == soul-runtime-test.* && -f "${resolved}/.owned-soul-runtime-fixture" ]] || return 1
    [[ "${resolved}" != "${SOURCE_ROOT}" ]] || return 1
    cd "${TEMP_PARENT}" || return 1
    rm -rf -- "${resolved}"
}
trap cleanup EXIT
outputs=(hermes/SOUL.runtime.md claude/SOUL.runtime.md codex/SOUL.runtime.md
         codex/AGENTS.runtime.md gemini/SOUL.runtime.md agy/SOUL.runtime.md)
sources=(config/agents/SHARED_SOUL.md config/agents/hermes/SOUL.md
         config/agents/claude/SOUL.delta.md config/agents/codex/SOUL.delta.md
         config/agents/gemini/SOUL.delta.md config/agents/agy/SOUL.delta.md)
inputs=("${sources[@]}" scripts/agents/build-soul-runtime.sh
        scripts/agents/soul-runtime-lib.sh scripts/enforcement/check-soul-runtime-drift.sh
        .claude/rules/coding-style.md .claude/rules/patterns.md GEMINI.md)
for path in "${inputs[@]}"; do
    mkdir -p "${FIXTURE}/$(dirname "${path}")"
    cp "${SOURCE_ROOT}/${path}" "${FIXTURE}/${path}"
done
mkdir -p "${FIXTURE}/.claude/skills/fixture/sample" "${FIXTURE}/.claude/skills/_archive/ignored"
printf '%s\n' '---' 'name: sample' 'description: Fixture skill' '---' > "${FIXTURE}/.claude/skills/fixture/sample/SKILL.md"
printf '%s\n' 'archive fixture' > "${FIXTURE}/.claude/skills/_archive/ignored/SKILL.md"
git -c init.templateDir= -C "${FIXTURE}" init -q
git -C "${FIXTURE}" config core.autocrlf false
cd "${FIXTURE}"
fail=0
checks=0
check() {
    checks=$((checks + 1))
    if "$@"; then echo "PASS ${checks}"; else echo "FAIL ${checks}: $*"; fail=$((fail + 1)); fi
}
build() { bash "${FIXTURE}/scripts/agents/build-soul-runtime.sh" >/dev/null; }
drift() { bash "${FIXTURE}/scripts/enforcement/check-soul-runtime-drift.sh" --quiet >/dev/null; }
reject_drift() {
    local rc=0
    bash "${FIXTURE}/scripts/enforcement/check-soul-runtime-drift.sh" "$@" > "${FIXTURE}/drift.log" 2>&1 || rc=$?
    [[ "${rc}" == 1 ]]
}
check build
actual=$(find config/agents -type f -name '*.runtime.md' | wc -l | tr -d ' ')
check test "${actual}" -eq 6
for path in "${outputs[@]}"; do
    check test -f "config/agents/${path}"
    check grep -Fq 'Subagent Write phantom hazard' "config/agents/${path}"
    if [[ "${path}" == codex/AGENTS.runtime.md ]]; then
        check grep -Fq '## Skill index' "config/agents/${path}"
        check grep -Fq '## Universal rules (inlined for Codex)' "config/agents/${path}"
        check grep -Fq 'fixture/' "config/agents/${path}"
    else
        check bash -c '! grep -Fq "## Skill index" "$1"' _ "config/agents/${path}"
        check bash -c '! grep -Fq "## Universal rules (inlined for Codex)" "$1"' _ "config/agents/${path}"
    fi
done
check drift
mkdir snapshots
for path in "${outputs[@]}"; do cp "config/agents/${path}" "snapshots/${path//\//-}"; done
check build
for path in "${outputs[@]}"; do check cmp -s "config/agents/${path}" "snapshots/${path//\//-}"; done
for path in "${outputs[@]}"; do
    printf '%s\n' 'tampered fixture content' >> "config/agents/${path}"
    check reject_drift --quiet
    cp "snapshots/${path//\//-}" "config/agents/${path}"
    mv "config/agents/${path}" "${FIXTURE}/held-runtime"
    check reject_drift --quiet
    mv "${FIXTURE}/held-runtime" "config/agents/${path}"
done
for path in "${sources[@]}"; do
    mv "${path}" "${FIXTURE}/held-source"
    check reject_drift --quiet
    mv "${FIXTURE}/held-source" "${path}"
done
# A verbose negative must complete its report rather than exit at diff|head.
printf '%s\n' 'verbose drift' >> config/agents/agy/SOUL.runtime.md
check reject_drift
check grep -Fq 'DRIFT DETECTED:' "${FIXTURE}/drift.log"
cp snapshots/agy-SOUL.runtime.md config/agents/agy/SOUL.runtime.md
mkdir foreign
git -c init.templateDir= -C foreign init -q
cd foreign
check drift
check test ! -e config
echo "RESULT: ${checks} checks, ${fail} failures; fixture-only generation"
[[ "${fail}" == 0 ]]
