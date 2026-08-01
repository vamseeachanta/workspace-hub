#!/usr/bin/env bash
# install-soul-runtime.sh — Create/retarget runtime symlinks for SOUL artifacts.
#
# Idempotent. Safe to re-run on any machine. Operates on:
#   ~/.claude/CLAUDE.md → config/agents/claude/SOUL.runtime.md
#   ~/.hermes/SOUL.md   → config/agents/hermes/SOUL.runtime.md
#   ~/.codex/AGENTS.md  → config/agents/codex/AGENTS.runtime.md   (replaces any broken-sed copy)
#   ~/.codex/SOUL.md    → config/agents/codex/SOUL.runtime.md    (loader-pending; see Phase 5)
#   ~/.gemini/SOUL.md   → config/agents/gemini/SOUL.runtime.md   (loader-pending; see Phase 5)
#
# Pre-existing non-symlink files at these paths are backed up to
#   <path>.pre-install-backup.<timestamp>
# before being replaced — so a broken sed-derived ~/.codex/AGENTS.md
# is preserved for forensics, not silently overwritten.
#
# Source build: scripts/agents/build-soul-runtime.sh must have been run
# (or the committed *.runtime.md artifacts must be present and current).
# Use scripts/enforcement/check-soul-runtime-drift.sh to verify before install.
#
# Refs: workspace-hub#2719 Phase 4.

set -euo pipefail

# Self-locating rather than cwd-derived (#3752): under cron / Task Scheduler the cwd
# is not guaranteed, and `git rev-parse` would resolve whatever repo the shell landed
# in — silently installing links that point at the wrong tree.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"   # -u: the filename suffix claims Z, so make it true
created=0
unchanged=0
backed_up=0
skipped=0
failed=0

# Canonical token set: linux/macos/windows. Same helper bootstrap-machine.sh uses.
# shellcheck source=../setup/lib/detect-os.sh
source "${REPO_ROOT}/scripts/setup/lib/detect-os.sh"
OS="$(detect_os)" || { echo "Unsupported OS — aborting install." >&2; exit 1; }

# Create the link, or fail LOUDLY rather than leaving a copy behind.
#
# Under MSYS/MINGW (git-bash on ace-win-1/ace-win-2) a bare `ln -s` COPIES by
# default instead of linking. A silent copy is the worst outcome available here:
# it reintroduces the duplicate-content problem this wiring exists to avoid, it
# never tracks later SOUL.runtime.md rebuilds, and no CI covers ~/.claude — so it
# would rot invisibly. Force a native symlink, verify it, and clean up otherwise.
create_link() {
    local resolved="$1" runtime_path="$2"

    if [[ "${OS}" != "windows" ]]; then
        ln -s "${resolved}" "${runtime_path}"
        return 0
    fi

    # Capture stderr rather than discarding it (#3752): an ACL denial, a missing
    # parent dir, a cross-volume target and a path-length overflow all land here, and
    # reporting every one of them as "enable Developer Mode" sends the operator down
    # the wrong path.
    LINK_ERR="$(MSYS=winsymlinks:nativestrict ln -s "${resolved}" "${runtime_path}" 2>&1)" || true
    [[ -L "${runtime_path}" ]] && return 0

    # Native symlink unavailable (no Developer Mode / not elevated). Remove only a
    # plain regular file we just created — pre-existing content was already backed
    # up by the caller. NEVER touch a directory or reparse point: per
    # .claude/rules/windows-junction-restore-safety.md, recursive removal through a
    # junction follows the link and empties the target (#3571, 4,215 files lost).
    if [[ -f "${runtime_path}" && ! -L "${runtime_path}" && ! -d "${runtime_path}" ]]; then
        rm -f "${runtime_path}"
    fi
    return 1
}

link_if_needed() {
    local repo_relative_target="$1" runtime_path="$2"
    local resolved="${REPO_ROOT}/${repo_relative_target}"

    if [[ ! -f "${resolved}" ]]; then
        echo "SKIP   ${runtime_path} — source ${repo_relative_target} missing (run build-soul-runtime.sh first?)"
        skipped=$((skipped + 1))
        return 0
    fi

    if [[ -L "${runtime_path}" ]]; then
        local cur="$(readlink "${runtime_path}")"
        if [[ "${cur}" == "${resolved}" ]]; then
            echo "OK     ${runtime_path} → already points to ${repo_relative_target}"
            unchanged=$((unchanged + 1))
            return 0
        fi
    fi

    if [[ -e "${runtime_path}" || -L "${runtime_path}" ]]; then
        local backup="${runtime_path}.pre-install-backup.${TS}"
        # Do not let one path abort the whole run (#3752). Under `set -e` a failed mv
        # kills the installer outright and the remaining providers are never
        # processed. Windows uses mandatory file locking, so a live Claude/Codex
        # process holding this file makes that a routine event on a 6-hourly schedule.
        if ! mv "${runtime_path}" "${backup}" 2>/dev/null; then
            echo "NEEDS-ATTENTION ${runtime_path} — could not back up (file locked by a running provider?)"
            echo "                Skipped so the remaining providers still get processed."
            failed=$((failed + 1))
            return 0
        fi
        echo "BACKUP ${runtime_path} → ${backup}"
        backed_up=$((backed_up + 1))
    fi

    if create_link "${resolved}" "${runtime_path}"; then
        echo "LINK   ${runtime_path} → ${resolved}"
        created=$((created + 1))
    else
        echo "NEEDS-ATTENTION ${runtime_path} — native symlink not created."
        echo "                ln: ${LINK_ERR:-(no error text)}"
        echo "                Common cause is no Developer Mode / not elevated, but check the error above"
        echo "                first — ACL denial, missing parent dir and path-length also land here."
        echo "                No copy was left behind: a copy would silently drift from"
        echo "                ${repo_relative_target} and nothing checks it."
        failed=$((failed + 1))
    fi
}

# Claude (#3743 follow-up, 2026-08-01)
# The repo CLAUDE.md adapter was retired; it carried the
# `@config/agents/claude/SOUL.runtime.md` import, so Claude became the only
# provider whose runtime no longer auto-loaded. Restored here as a SYMLINK to the
# canonical artifact — the same shape as Hermes/Codex, not a hand-maintained file.
#
# This is strictly better coverage than the old wiring: the repo adapter's @import
# only fired when the session cwd was inside workspace-hub, whereas ~/.claude/CLAUDE.md
# loads in EVERY cwd. Do not replace this with a regular file — the whole point is
# that the content lives in exactly one place and is drift-checked there.
if [[ -d "${HOME}/.claude" ]]; then
    link_if_needed config/agents/claude/SOUL.runtime.md   "${HOME}/.claude/CLAUDE.md"
else
    echo "SKIP   ~/.claude/ not present"
fi

# Hermes
if [[ -d "${HOME}/.hermes" ]]; then
    link_if_needed config/agents/hermes/SOUL.runtime.md   "${HOME}/.hermes/SOUL.md"
else
    echo "SKIP   ~/.hermes/ not present"
fi

# Codex
# Phase 5 verified (2026-05-16): Codex CLI's base instructions explicitly
# cite AGENTS.md as the loaded surface; SOUL.md is not read. Only the
# AGENTS.md symlink is installed.
if [[ -d "${HOME}/.codex" ]]; then
    link_if_needed config/agents/codex/AGENTS.runtime.md  "${HOME}/.codex/AGENTS.md"
else
    echo "SKIP   ~/.codex/ not present"
fi

# Gemini
# Phase 5 verified (2026-05-16): Gemini CLI bundle references GEMINI.md
# (workspace and ~/.gemini/GEMINI.md), not SOUL.md. No user-global symlink
# is created here. Workspace GEMINI.md integration is Phase 6 (adapter
# de-duplication). config/agents/gemini/SOUL.runtime.md remains a built
# reference artifact for review and future use.
echo "SKIP   ~/.gemini/SOUL.md not created — Gemini CLI doesn't load SOUL.md (see Phase 5)"
echo "SKIP   agy SOUL symlink not created — agy loads the GEMINI.md family, not SOUL.md; config/agents/agy/SOUL.runtime.md is a built reference artifact (#3573)"

echo
echo "Summary: ${created} created, ${unchanged} unchanged, ${backed_up} backed-up, ${skipped} skipped, ${failed} needs-attention."

# Exit non-zero when a link could not be created, so harness-install-doctor.sh
# records NEEDS-ATTENTION instead of reporting a repair that did not happen.
# Silence here would look identical to success — see the R5 silent-pass defect (#3744).
if (( failed > 0 )); then
    exit 1
fi
