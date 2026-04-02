#!/usr/bin/env bash
# track-skill-patches.sh — post-commit hook to log .claude/skills/ modifications
#
# Purpose: When any agent (Hermes, Claude, Codex, or unknown) modifies a
# .claude/skills/ file, log the change to logs/orchestrator/hermes/skill-patches.jsonl.
#
# Format: {"ts":"...","agent":"hermes|claude|codex|unknown","action":"create|modify|delete","skill_path":"...","commit":"..."}
#
# Installation:
#   Option A — Symlink:
#     ln -sf ../../scripts/hooks/track-skill-patches.sh .git/hooks/post-commit
#   Option B — Call from existing post-commit hook:
#     echo 'bash scripts/hooks/track-skill-patches.sh' >> .git/hooks/post-commit
#
# This script is safe to run outside of a git context (it will exit 0 silently).

set -euo pipefail

# --- Configuration ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
SKILL_PREFIX=".claude/skills/"
LOG_DIR="${REPO_ROOT}/logs/orchestrator/hermes"
LOG_FILE="${LOG_DIR}/skill-patches.jsonl"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# --- Get the latest commit ---
COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null)" || exit 0

# --- Find skill files changed in this commit ---
# --diff-filter=ACDMR catches Added, Copied, Deleted, Modified, Renamed
CHANGED_FILES="$(git diff-tree --no-commit-id --diff-filter=ACDMR -r --name-status "${COMMIT_SHA}" 2>/dev/null)" || exit 0

# Filter to only .claude/skills/ paths
SKILL_CHANGES="$(echo "${CHANGED_FILES}" | grep -E "^[ACDMR]\s+${SKILL_PREFIX}" || true)"

# Exit early if no skill files were changed
if [[ -z "${SKILL_CHANGES}" ]]; then
    exit 0
fi

# --- Determine the agent from commit metadata ---
detect_agent() {
    local commit="$1"

    # Check commit author name and email
    local author_name author_email commit_msg
    author_name="$(git log -1 --format='%an' "${commit}" 2>/dev/null || echo "")"
    author_email="$(git log -1 --format='%ae' "${commit}" 2>/dev/null || echo "")"
    commit_msg="$(git log -1 --format='%s' "${commit}" 2>/dev/null || echo "")"

    # Hermes detection: author contains "hermes", or commit message references hermes
    if echo "${author_name}${author_email}${commit_msg}" | grep -qi "hermes"; then
        echo "hermes"
        return
    fi

    # Claude detection: author contains "claude", or commit message has [claude] / claude-code patterns
    if echo "${author_name}${author_email}" | grep -qi "claude"; then
        echo "claude"
        return
    fi
    if echo "${commit_msg}" | grep -qiE '\[claude\]|claude.code|comprehensive-learning'; then
        echo "claude"
        return
    fi

    # Codex detection: author contains "codex", or commit message references codex
    if echo "${author_name}${author_email}${commit_msg}" | grep -qi "codex"; then
        echo "codex"
        return
    fi

    # Gemini detection
    if echo "${author_name}${author_email}${commit_msg}" | grep -qi "gemini"; then
        echo "gemini"
        return
    fi

    # Check for environment hints (set by orchestrator scripts)
    if [[ -n "${HERMES_SESSION_ID:-}" ]]; then
        echo "hermes"
        return
    fi
    if [[ -n "${CLAUDE_SESSION_ID:-}" || -n "${CLAUDECODE:-}" ]]; then
        echo "claude"
        return
    fi
    if [[ -n "${CODEX_SESSION_ID:-}" ]]; then
        echo "codex"
        return
    fi

    echo "unknown"
}

# --- Map git status letter to action ---
status_to_action() {
    case "$1" in
        A|C) echo "create" ;;
        D)   echo "delete" ;;
        M|R) echo "modify" ;;
        *)   echo "modify" ;;
    esac
}

# --- Timestamp in ISO 8601 ---
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- Detect agent once per commit ---
AGENT="$(detect_agent "${COMMIT_SHA}")"

# --- Log each changed skill file ---
while IFS=$'\t' read -r status filepath; do
    # Skip empty lines
    [[ -z "${status}" ]] && continue

    ACTION="$(status_to_action "${status}")"

    # Write JSON line (portable — no jq dependency)
    printf '{"ts":"%s","agent":"%s","action":"%s","skill_path":"%s","commit":"%s"}\n' \
        "${TS}" "${AGENT}" "${ACTION}" "${filepath}" "${COMMIT_SHA}" \
        >> "${LOG_FILE}"

done <<< "${SKILL_CHANGES}"

# Log summary to stderr for visibility in hook output (non-blocking)
CHANGE_COUNT="$(echo "${SKILL_CHANGES}" | wc -l)"
echo "[track-skill-patches] Logged ${CHANGE_COUNT} skill change(s) by ${AGENT} in ${COMMIT_SHA:0:8}" >&2

exit 0
