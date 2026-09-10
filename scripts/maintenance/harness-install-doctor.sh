#!/usr/bin/env bash
# harness-install-doctor.sh — REPAIR arm for per-provider harness install drift.
#
# WHY: equivalence-sentinel.sh (#3059) DETECTS machine-equivalence drift but is
#   report-only — it never repairs. install-soul-runtime.sh is the blessed
#   installer but runs only by hand, so on secondary boxes the per-provider
#   runtime symlinks silently drift (observed 2026-06-17 on ace-linux-2:
#   ~/.codex/skills was an empty dir, not the documented symlink). This doctor
#   is the missing repair arm: it runs OUT-OF-SESSION on a schedule so the next
#   session — for ANY provider (Claude / Codex / agy) — starts pre-healed.
#   Provider-neutral by design: a SessionEnd hook would only fire after Claude.
#
# WHAT IT DOES (idempotent; composes existing blessed installers, invents nothing):
#   1. Runs scripts/agents/install-soul-runtime.sh  → SOUL/AGENTS runtime symlinks
#      (~/.hermes/SOUL.md, ~/.codex/AGENTS.md). THIS is the core repair: the
#      blessed installer otherwise runs only by hand, so it never re-heals
#      secondary boxes on its own.
#   2. Report-only: confirms ~/.codex/skills holds Codex's native .system skills
#      and is NOT a stray symlink. Codex reads WORKSPACE skills from the repo's
#      .claude/skills/<family>/ via the Skill index in AGENTS.runtime.md (no
#      native loader, line 173) — so ~/.codex/skills must be left ALONE, not
#      symlinked over (that would shadow .system). We verify, never mutate.
#   3. Reports (does NOT auto-create) deferred items: ~/.gemini/GEMINI.md is
#      Phase-6 per install-soul-runtime.sh:84 — flagged, not forced.
#   4. Verifies the repo-tracked Codex memory surface exists
#      (config/agents/codex/MEMORY.runtime.md — owned by bridge-hermes-claude.sh;
#      this doctor reports staleness, it does NOT regenerate it: that is a
#      token-heavy `claude -p` job and belongs to the provider-dream-bridge cron).
#
# Each item reports one of: OK / REPAIRED / SKIP / NEEDS-ATTENTION.
# Exit: 0 = all OK or repaired; 1 = at least one NEEDS-ATTENTION (unrepairable).
#
# Env:
#   DOCTOR_DRY_RUN=1   detect + print intended actions, change nothing.
#
# Scheduling: declare in config/scheduled-tasks/schedule-tasks.yaml
#   (id: harness-install-doctor); install via scripts/cron/setup-cron.sh.
# Refs: harden-ecosystem epic #3058; sentinel #3059; SSoT install #2719 Phase 4.

set -uo pipefail

# Under `set -u`, an unset HOME (rare restrictive cron env) would crash with a
# cryptic "unbound variable" before any report. Fail early and legibly instead.
: "${HOME:?HOME must be set}"

# Self-locating, NOT cwd- or $WORKSPACE_HUB-derived (#3752). This runs from cron /
# Task Scheduler with a non-login shell, which does not source ~/.bashrc — so
# ${WORKSPACE_HUB} is often empty, the catalog's `cd $WORKSPACE_HUB` becomes a bare
# `cd` to $HOME with rc 0, and `git rev-parse` then resolves whatever repo happens to
# be there (or the hardcoded Linux fallback). Deriving the root from this script's own
# path is the only form that cannot silently target the wrong tree. Precedent:
# scripts/cron/harness-update-windows.sh:13-14.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DRY="${DOCTOR_DRY_RUN:-0}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
needs_attention=0
declare -a results=()

record() { # status item detail
    local status="$1" item="$2" detail="${3:-}"
    results+=("${status}|${item}|${detail}")
    [[ "${status}" == "NEEDS-ATTENTION" ]] && needs_attention=1
    local c="${NC}"
    case "${status}" in
        OK)               c="${GREEN}" ;;
        REPAIRED)         c="${GREEN}" ;;
        SKIP)             c="${YELLOW}" ;;
        NEEDS-ATTENTION)  c="${RED}" ;;
    esac
    printf "  ${c}%-16s${NC} %-28s %s\n" "${status}" "${item}" "${detail}"
}

run() { # echo+run, honor dry-run
    if [[ "${DRY}" == "1" ]]; then echo "    DRY: $*"; return 0; fi
    "$@"
}

echo "harness-install-doctor @ ${TS}  (repo: ${REPO_ROOT}, host: $(hostname), dry-run: ${DRY})"
echo

# ── 1. SOUL/AGENTS runtime symlinks (delegate to blessed installer) ──────────
installer="${REPO_ROOT}/scripts/agents/install-soul-runtime.sh"
if [[ -x "${installer}" || -f "${installer}" ]]; then
    if [[ "${DRY}" == "1" ]]; then
        record SKIP "soul-runtime-symlinks" "dry-run: would run install-soul-runtime.sh"
    else
        if out="$(bash "${installer}" 2>&1)"; then
            summary="$(printf '%s\n' "${out}" | grep -i '^Summary:' || echo 'ran')"
            # Exit 0 is NOT sufficient evidence of a repair (#3752). The installer
            # returns 0 for every SKIP — missing source artifact, absent provider
            # dir, wrong repo root — and only `failed` reaches its exit gate. So a
            # run that linked NOTHING previously reported OK, making a silently
            # broken box indistinguishable from a healthy one. Inspect the summary
            # we already captured: if nothing was created AND nothing was already
            # correct, the repair arm did not repair.
            created="$(printf '%s\n' "${summary}" | sed -n 's/.*Summary: \([0-9]\{1,\}\) created.*/\1/p')"
            unchanged="$(printf '%s\n' "${summary}" | sed -n 's/.*, \([0-9]\{1,\}\) unchanged.*/\1/p')"
            if [[ -z "${created}" || -z "${unchanged}" ]]; then
                # Summary absent or in an unexpected shape — do not assume success.
                record NEEDS-ATTENTION "soul-runtime-symlinks" \
                    "installer exited 0 but its summary was unparseable: ${summary}"
                printf '%s\n' "${out}" | sed 's/^/      /'
            elif (( created + unchanged == 0 )); then
                record NEEDS-ATTENTION "soul-runtime-symlinks" \
                    "no-op run — 0 created, 0 unchanged (${summary})"
                printf '%s\n' "${out}" | sed 's/^/      /'
            else
                record OK "soul-runtime-symlinks" "${summary}"
            fi
        else
            record NEEDS-ATTENTION "soul-runtime-symlinks" "install-soul-runtime.sh failed — see output"
            printf '%s\n' "${out}" | sed 's/^/      /'
        fi
    fi
else
    record NEEDS-ATTENTION "soul-runtime-symlinks" "installer missing: ${installer}"
fi

# ── 2. ~/.codex/skills — verify native .system intact, NEVER mutate ───────────
# Codex uses workspace skills via the repo (.claude/skills/<family>/) through the
# AGENTS.runtime.md Skill index — it has no native loader (line 173). ~/.codex/
# skills holds Codex's OWN .system skills; symlinking it over .claude/skills would
# shadow them. So this is a guardrail check, not a repair.
codex_skills="${HOME}/.codex/skills"
if [[ ! -d "${HOME}/.codex" ]]; then
    record SKIP "codex-skills" "~/.codex not present on this box"
elif [[ -L "${codex_skills}" ]]; then
    record NEEDS-ATTENTION "codex-skills" "is a symlink → likely shadows native .system; expected a real dir"
elif [[ -d "${codex_skills}/.system" ]]; then
    record OK "codex-skills" "native .system present; workspace skills served from repo"
elif [[ -d "${codex_skills}" ]]; then
    record SKIP "codex-skills" "real dir, no .system (Codex may not have seeded system skills yet)"
else
    record SKIP "codex-skills" "absent (Codex CLI will create on next run)"
fi

# ── 3. Deferred items — report only, never force ──────────────────────────────
gemini_md="${HOME}/.gemini/GEMINI.md"
if [[ -d "${HOME}/.gemini" ]]; then
    if [[ -e "${gemini_md}" ]]; then
        record OK "gemini-entry" "GEMINI.md present"
    else
        record SKIP "gemini-entry" "absent — Phase-6 deferred (install-soul-runtime.sh:84); not forced"
    fi
else
    record SKIP "gemini-entry" "~/.gemini not present on this box"
fi

# ── 4. Codex repo-tracked memory surface (owned by bridge; verify only) ───────
codex_mem="${REPO_ROOT}/config/agents/codex/MEMORY.runtime.md"
codex_agents="${REPO_ROOT}/config/agents/codex/AGENTS.runtime.md"
if [[ -f "${codex_mem}" && -f "${codex_agents}" ]]; then
    age_days=$(( ( $(date +%s) - $(stat -c %Y "${codex_mem}" 2>/dev/null || echo 0) ) / 86400 ))
    if (( age_days > 14 )); then
        record SKIP "codex-memory-surface" "MEMORY.runtime.md ${age_days}d old — bridge-hermes-claude.sh owns refresh"
    else
        record OK "codex-memory-surface" "MEMORY.runtime.md fresh (${age_days}d)"
    fi
else
    record NEEDS-ATTENTION "codex-memory-surface" "missing repo-tracked codex runtime artifact(s)"
fi

# ── Report ────────────────────────────────────────────────────────────────────
echo
if (( needs_attention )); then
    echo -e "${RED}install-doctor: NEEDS-ATTENTION items present (exit 1).${NC}"
    exit 1
fi
echo -e "${GREEN}install-doctor: harness install state healthy on $(hostname) (exit 0).${NC}"
exit 0
