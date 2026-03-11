#!/usr/bin/env bash
# tidy-agent-teams.sh — Delete archived-WRK teams and stale empty orphan task dirs.
# Fires at every stage-gate Stop hook (stages 1-20 linear/monotonic).
# Usage: bash scripts/hooks/tidy-agent-teams.sh [--dry-run]
set -euo pipefail

DRY_RUN=false
for arg in "$@"; do [[ "$arg" == "--dry-run" ]] && DRY_RUN=true; done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ARCHIVE_DIR="${REPO_ROOT}/.claude/work-queue/archive"
# Allow test injection of dirs; default to standard home locations
TEAMS_DIR="${CLAUDE_TEAMS_DIR:-${HOME}/.claude/teams}"
TASKS_DIR="${CLAUDE_TASKS_DIR:-${HOME}/.claude/tasks}"

deleted_teams=0; purged_tasks=0; skipped=0

# Build archived WRK ID set once from archive filenames
declare -A archived_ids=()
if [[ -d "${ARCHIVE_DIR}" ]]; then
    while IFS= read -r f; do
        id="$(basename "${f}" .md)"
        archived_ids["${id}"]=1
    done < <(find "${ARCHIVE_DIR}" -maxdepth 2 -name "WRK-*.md" 2>/dev/null)
fi

# Tidy named teams whose WRK is archived
if [[ -d "${TEAMS_DIR}" ]]; then
    for team_dir in "${TEAMS_DIR}"/* ; do
        [[ -d "${team_dir}" ]] || continue
        team_name="$(basename "${team_dir}")"
        if [[ "${team_name}" =~ ^wrk-([0-9]+)-[a-z0-9-]+$ ]]; then
            wrk_id="WRK-${BASH_REMATCH[1]}"
            if [[ -n "${archived_ids[${wrk_id}]+_}" ]]; then
                echo "[tidy] team ${team_name} → ${wrk_id} archived, candidate for deletion"
                if [[ "${DRY_RUN}" == false ]]; then rm -rf "${team_dir}"; fi
                ((deleted_teams++)) || true
            fi
        else
            sentinel="${team_dir}/.wrk-id"
            if [[ -f "${sentinel}" ]]; then
                sentinel_id="$(tr -d '[:space:]' < "${sentinel}")"
                if [[ -n "${archived_ids[${sentinel_id}]+_}" ]]; then
                    echo "[tidy] team ${team_name} → sentinel ${sentinel_id} archived, candidate for deletion"
                    if [[ "${DRY_RUN}" == false ]]; then rm -rf "${team_dir}"; fi
                    ((deleted_teams++)) || true
                else
                    echo "[tidy] skip ${team_name} — sentinel ${sentinel_id} not archived"
                    ((skipped++)) || true
                fi
            else
                echo "[tidy] skip ${team_name} — does not match wrk-NNN-slug convention"
                ((skipped++)) || true
            fi
        fi
    done
fi

# Tidy empty stale UUID task dirs (>7 days old)
UUID_RE='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
if [[ -d "${TASKS_DIR}" ]]; then
    while IFS= read -r task_dir; do
        task_name="$(basename "${task_dir}")"
        if [[ ! "${task_name}" =~ ${UUID_RE} ]]; then ((skipped++)) || true; continue; fi
        echo "[tidy] task ${task_name} → empty+stale, candidate for purge"
        if [[ "${DRY_RUN}" == false ]]; then rm -rf "${task_dir}"; fi
        ((purged_tasks++)) || true
    done < <(find "${TASKS_DIR}" -mindepth 1 -maxdepth 1 -type d -empty -mtime +7 2>/dev/null)
fi

echo "agent_teams_tidied: deleted=${deleted_teams} tasks_purged=${purged_tasks} skipped=${skipped}"
