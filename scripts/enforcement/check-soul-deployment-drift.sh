#!/usr/bin/env bash
# check-soul-deployment-drift.sh — Verify what a MACHINE actually loads matches
# what origin/main holds.
#
# Sibling to check-soul-runtime-drift.sh, which checks whether committed runtime
# artifacts match a rebuild from source. That is in-repo drift. This is
# DEPLOYMENT drift: whether the file an agent loads on this box is the file
# origin says it should load.
#
# The gap this closes was measured, not imagined. On 2026-09-10 four machines
# carried correct, working symlinks into valid checkouts and were 70, 88, 11 and
# 120 commits stale. Every one loaded the engineering register; not one loaded
# the raw-data rule committed after it. The link was live and pointing at the
# right path; the checkout behind it was months old. Nothing reported this,
# because no check looked past the repository.
#
# TRANSPORT-AGNOSTIC BY DESIGN. It compares CONTENT, so a symlink, a copy and a
# hard link are all acceptable and all equally checked. That matters on Windows
# accounts without symlink privilege, where install-soul-runtime.sh refuses to
# leave a copy precisely because a copy "would rot invisibly" — with this gate,
# it no longer rots invisibly, and the transport becomes a detail.
#
# Usage:
#   check-soul-deployment-drift.sh            # human-readable table
#   check-soul-deployment-drift.sh --quiet    # exit code only
#   check-soul-deployment-drift.sh --no-fetch # skip git fetch (offline)
#   check-soul-deployment-drift.sh --self-test
#
# Exit 0 all current, 1 on any drift, 2 on usage or environment error.

set -uo pipefail

QUIET=0; NO_FETCH=0; SELF_TEST=0
for a in "$@"; do
    case "$a" in
        --quiet)     QUIET=1 ;;
        --no-fetch)  NO_FETCH=1 ;;
        --self-test) SELF_TEST=1 ;;
        -h|--help)   sed -n '2,28p' "$0"; exit 0 ;;
        *) echo "unknown argument: $a" >&2; exit 2 ;;
    esac
done

# sha256 differs by platform: coreutils on Linux and git-bash, shasum on macOS.
sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" 2>/dev/null | cut -d' ' -f1
    elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1
    else echo "no sha256 tool available" >&2; return 2; fi
}
sha256_stdin() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -d' ' -f1
    else shasum -a 256 | cut -d' ' -f1; fi
}

# provider : runtime path in the repo : destination relative to HOME
PROVIDERS=(
    "claude:config/agents/claude/SOUL.runtime.md:.claude/CLAUDE.md"
    "codex:config/agents/codex/AGENTS.runtime.md:.codex/AGENTS.md"
    "hermes:config/agents/hermes/SOUL.runtime.md:.hermes/SOUL.md"
    "gemini:config/agents/gemini/SOUL.runtime.md:.gemini/GEMINI.md"
    "agy:config/agents/agy/SOUL.runtime.md:.agy/SOUL.md"
)

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: not inside a git checkout. Run from workspace-hub." >&2; exit 2; }

if [[ "${NO_FETCH}" -eq 0 ]]; then
    git -C "${REPO_ROOT}" fetch -q origin main 2>/dev/null || \
        echo "WARN: could not fetch origin/main; comparing against the last known ref" >&2
fi

BEHIND="$(git -C "${REPO_ROOT}" rev-list --count HEAD..origin/main 2>/dev/null || echo '?')"
HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || echo '?')"
ORIGIN_SHA="$(git -C "${REPO_ROOT}" rev-parse --short origin/main 2>/dev/null || echo '?')"

drift=0; absent=0; current=0
[[ "${QUIET}" -eq 0 ]] && {
    printf '%-9s %-11s %-9s %s\n' PROVIDER STATE TRANSPORT DESTINATION
    printf '%-9s %-11s %-9s %s\n' --------- ----------- --------- -----------
}

for entry in "${PROVIDERS[@]}"; do
    IFS=: read -r name runtime_rel dest_rel <<< "${entry}"
    dest="${HOME}/${dest_rel}"

    # The authority is origin/main's blob, never the working tree — a stale or
    # dirty checkout must not be able to declare itself current.
    want="$(git -C "${REPO_ROOT}" show "origin/main:${runtime_rel}" 2>/dev/null | sha256_stdin)"
    if [[ -z "${want}" || "${want}" == "$(printf '' | sha256_stdin)" ]]; then
        [[ "${QUIET}" -eq 0 ]] && printf '%-9s %-11s %-9s %s\n' "${name}" "NO-SOURCE" "-" "${runtime_rel}"
        continue
    fi

    if [[ ! -e "${dest}" ]]; then
        state=ABSENT; transport="-"; absent=$((absent + 1)); drift=$((drift + 1))
    else
        if [[ -L "${dest}" ]]; then transport="symlink"; else transport="copy"; fi
        got="$(sha256_of "${dest}")"
        if [[ "${got}" == "${want}" ]]; then state=CURRENT; current=$((current + 1))
        else state=STALE; drift=$((drift + 1)); fi
    fi
    [[ "${QUIET}" -eq 0 ]] && printf '%-9s %-11s %-9s %s\n' "${name}" "${state}" "${transport}" "~/${dest_rel}"
done

if [[ "${QUIET}" -eq 0 ]]; then
    echo
    echo "${current} current, ${drift} drifted (${absent} absent)"
    echo "checkout ${HEAD_SHA}, origin/main ${ORIGIN_SHA}, behind by ${BEHIND} commit(s)"
    if [[ "${BEHIND}" != "0" && "${BEHIND}" != "?" && "${drift}" -eq 0 ]]; then
        echo "  The checkout is behind on other paths; the agent runtimes match origin."
        echo "  That is the distinction this gate exists to make: a stale checkout is"
        echo "  informational, a stale runtime is the failure."
    fi
    if [[ "${drift}" -gt 0 ]]; then
        echo
        echo "To correct:"
        echo "  git -C ${REPO_ROOT} checkout origin/main -- config/agents"
        echo "  scripts/agents/install-soul-runtime.sh"
        echo "Where symlink creation is unavailable, a copy is acceptable — this"
        echo "gate checks content, so a copy that is refreshed is as good as a link."
    fi
fi

exit $(( drift > 0 ? 1 : 0 ))
