#!/usr/bin/env bash
# bridge-hermes-claude.sh — Refresh private cross-provider memory snapshots.
#
# Architecture: private memory snapshots travel through
# vamseeachanta/claude-memory-snapshots, under hosts/<role-slug>/.
#
# Usage:
#   bash scripts/memory/bridge-hermes-claude.sh           # dry-run (no commit)
#   bash scripts/memory/bridge-hermes-claude.sh --commit  # commit if changed
#
# Scheduling:
#   Linux:   cron (04:00 daily via setup-cron.sh)
#   Windows: Task Scheduler (04:30 daily via setup-scheduler-tasks.ps1)
#
# Issues: #1886 (initial), #1890 (cron), #1892 (dedup), #1893 (topic mirror),
#         #1901 (cron fix), #1918 (Windows parity)

set -euo pipefail

REPO_ROOT="${BRIDGE_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo ".")}"
PUBLIC_MEMORY_DIR="${REPO_ROOT}/.claude/memory"
TEMPLATE_DIR="${PUBLIC_MEMORY_DIR}/templates"
HERMES_MEM_DIR="${HOME}/.hermes/memories"
# Resolve Claude auto-memory across workspace moves. Deriving the slug inline from
# the CURRENT repo path silently broke when the ecosystem moved to /mnt/ace/ws:
# Claude Code pins the project slug at session start and kept writing to the old
# one, so the mirror copied nothing while still printing a tick for the stale
# snapshot. The resolver tries the exact slug, known aliases, then any slug
# ending in this repo's basename -- and fails LOUDLY rather than resolving to a
# path it cannot verify.
# shellcheck source=scripts/memory/resolve-auto-memory.sh
source "${REPO_ROOT}/scripts/memory/resolve-auto-memory.sh"
CLAUDE_MEM_DIR="$(resolve_claude_memory_dir "${REPO_ROOT}" "${HOME}")" || CLAUDE_MEM_DIR=""
TIMESTAMP="$(date +%Y-%m-%d)"
COMMIT_MODE="${1:-}"
PRIVATE_REPO="${MEMORY_PRIVATE_REPO_DIR:-${HOME}/claude-memory-snapshots}"
PRIVATE_REPO_SLUG="vamseeachanta/claude-memory-snapshots"
ALLOW_LOCAL_TEST="${MEMORY_PRIVATE_ALLOW_LOCAL_TEST:-}"
TEST_HARNESS="${MEMORY_PRIVATE_TEST_HARNESS:-}"
HOST_SLUG="${MEMORY_BRIDGE_HOST_SLUG:-}"

approved_host_slug() {
    case "$1" in
        ace-win-1|ace-win-2|ace-linux-1|ace-linux-2|gpu-claw|spark) return 0 ;;
        *) return 1 ;;
    esac
}

detect_host_slug() {
    if [[ -n "${HOST_SLUG}" ]]; then
        approved_host_slug "${HOST_SLUG}" || {
            echo "[bridge] unsupported MEMORY_BRIDGE_HOST_SLUG: ${HOST_SLUG}" >&2
            return 1
        }
        return 0
    fi
    local short
    short="$(hostname -s 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)"
    if approved_host_slug "${short}"; then
        HOST_SLUG="${short}"
        return 0
    fi
    echo "[bridge] cannot derive approved role slug; set MEMORY_BRIDGE_HOST_SLUG" >&2
    return 1
}

require_private_memory_repo() {
    detect_host_slug || return 1
    if [[ ! -d "${PRIVATE_REPO}/.git" ]]; then
        echo "[bridge] private memory repo is required and was not found: ${PRIVATE_REPO}" >&2
        return 1
    fi
    if [[ "${ALLOW_LOCAL_TEST}" == "1" && "${TEST_HARNESS}" != "1" ]]; then
        echo "[bridge] MEMORY_PRIVATE_ALLOW_LOCAL_TEST is only valid under the test harness" >&2
        return 1
    fi
    if [[ "${ALLOW_LOCAL_TEST}" == "1" ]]; then
        case "${PRIVATE_REPO}" in
            /tmp/*) ;;
            *)
                echo "[bridge] local test private repo must be under /tmp" >&2
                return 1
                ;;
        esac
    else
        local remote_url
        remote_url="$(git -C "${PRIVATE_REPO}" config --get remote.origin.url || true)"
        case "${remote_url}" in
            git@github.com:vamseeachanta/claude-memory-snapshots.git|\
https://github.com/vamseeachanta/claude-memory-snapshots.git|\
https://github.com/vamseeachanta/claude-memory-snapshots) ;;
            *)
                echo "[bridge] private memory repo origin must be ${PRIVATE_REPO_SLUG}" >&2
                return 1
                ;;
        esac
        if ! command -v gh >/dev/null 2>&1; then
            echo "[bridge] gh is required to verify private repo visibility" >&2
            return 1
        fi
        local visibility
        visibility="$(gh repo view "${PRIVATE_REPO_SLUG}" --json visibility --jq .visibility 2>/dev/null || true)"
        if [[ "${visibility}" != "PRIVATE" ]]; then
            echo "[bridge] ${PRIVATE_REPO_SLUG} visibility is not verified PRIVATE" >&2
            return 1
        fi
    fi
}

require_private_memory_repo
HOST_ROOT="${PRIVATE_REPO}/hosts/${HOST_SLUG}"
MEMORY_DIR="${HOST_ROOT}/memory"
TOPICS_DIR="${MEMORY_DIR}/topics"
READBACK_DIR="${HOST_ROOT}/readback"

# Colours
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

mkdir -p "${MEMORY_DIR}" "${TOPICS_DIR}" "${READBACK_DIR}"

echo "[bridge] Starting memory bridge — ${TIMESTAMP}"

# ---------------------------------------------------------------------------
# 1. Read Hermes memory sources
# ---------------------------------------------------------------------------
HERMES_MEMORY=""
HERMES_USER=""
HAS_HERMES=false

if [[ -f "${HERMES_MEM_DIR}/MEMORY.md" ]]; then
    HERMES_MEMORY="$(cat "${HERMES_MEM_DIR}/MEMORY.md")"
    HAS_HERMES=true
fi
if [[ -f "${HERMES_MEM_DIR}/USER.md" ]]; then
    HERMES_USER="$(cat "${HERMES_MEM_DIR}/USER.md")"
    HAS_HERMES=true
fi

if [[ "${HAS_HERMES}" = true ]]; then
    echo "[bridge] Hermes memory found at ${HERMES_MEM_DIR}"
else
    echo "[bridge] No Hermes memory found — proceeding with Claude auto-memory only"
fi

# ---------------------------------------------------------------------------
# 2. Build the BRIDGE section content (injected between markers in agents.md)
# ---------------------------------------------------------------------------
BRIDGE_CONTENT=""

if [[ "${HAS_HERMES}" = true ]]; then
    BRIDGE_CONTENT+=$'\n'"## Synced from Hermes Memory (${TIMESTAMP})"$'\n\n'

    if [[ -n "${HERMES_MEMORY}" ]]; then
        BRIDGE_CONTENT+="### Environment Facts"$'\n\n'
        while IFS= read -r line; do
            [[ -z "${line}" || "${line}" == "§" ]] && continue
            BRIDGE_CONTENT+="- ${line}"$'\n'
        done < <(tr '§' '\n' <<< "${HERMES_MEMORY}")
        BRIDGE_CONTENT+=$'\n'
    fi

    if [[ -n "${HERMES_USER}" ]]; then
        BRIDGE_CONTENT+="### User Profile"$'\n\n'
        while IFS= read -r line; do
            [[ -z "${line}" || "${line}" == "§" ]] && continue
            BRIDGE_CONTENT+="- ${line}"$'\n'
        done < <(tr '§' '\n' <<< "${HERMES_USER}")
        BRIDGE_CONTENT+=$'\n'
    fi
fi

# ---------------------------------------------------------------------------
# 3. Generate agents.md from template, injecting BRIDGE section
# ---------------------------------------------------------------------------
TEMPLATE="${TEMPLATE_DIR}/agents-template.md"
AGENTS_OUT="${MEMORY_DIR}/agents.md"

if [[ -f "${TEMPLATE}" ]]; then
    # Replace content between <!-- BRIDGE:START --> and <!-- BRIDGE:END -->
    # using awk for reliable multi-line replacement
    awk -v bridge="${BRIDGE_CONTENT}" '
        /<!-- BRIDGE:START/{
            print
            print bridge
            in_bridge=1
            next
        }
        /<!-- BRIDGE:END/{
            in_bridge=0
        }
        !in_bridge { print }
    ' "${TEMPLATE}" > "${AGENTS_OUT}"
    echo "[bridge] agents.md generated from template with injected bridge section"
else
    # Fallback: no template, write raw bridge content
    {
        echo "# Agent Workflow Facts"
        echo ""
        echo "> Git-tracked. No template found — raw bridge output. Create ${TEMPLATE} to manage baseline."
        echo ""
        echo "${BRIDGE_CONTENT}"
    } > "${AGENTS_OUT}"
    echo "[bridge] agents.md written (no template — raw fallback)"
fi

# ---------------------------------------------------------------------------
# 4. Regenerate context.md (always authoritative)
# ---------------------------------------------------------------------------
cat > "${MEMORY_DIR}/context.md" << 'CONTEXT_EOF'
# Cross-Machine Context

> Private snapshot. Managed by scripts/memory/bridge-hermes-claude.sh.
> Source of truth for environment conventions in the private memory archive.

## Machines

| Machine | OS | Hermes | Python cmd | Workspace root |
|---------|----|--------|------------|----------------|
| ace-linux-1 | Linux | YES | `uv run` | role-local workspace-hub checkout |
| ace-win-1 | Windows | NO | `python` | role-local workspace-hub checkout |

## Python Command Rule

- **Linux**: ALWAYS `uv run` — never bare `python3` or `pip`
- **Windows**: Use `python` unless the role-local environment has `uv`

## Workspace Layout (Linux)

- The role-local workspace-hub checkout is the harness/control-plane repository.
- **Tier-1 repos live as SIBLINGS of workspace-hub — NOT nested under workspace-hub.**
  `workspace-hub` is the harness/control-plane, not a parent for tier-1 checkouts. Each is a
  separate git repo; commit from inside it, never from the workspace-hub root.

## Windows Path Conventions

- MINGW64 bash: paths use `/d/workspace-hub/` (not the drive-letter backslash form)
- `core.symlinks=false` — git treats junctions as dirs; never commit symlinks cross-platform
- Shell scripts: `#!/usr/bin/env bash`, LF line endings

## Memory Sync Model

Memory snapshots travel through the private claude-memory-snapshots repository. No Hermes is needed on Windows.

1. **Hermes on control-plane Linux**: Writes authoritative facts to `~/.hermes/memories/`
2. **Bridge script** (`scripts/memory/bridge-hermes-claude.sh`): Reads Hermes memory
   (if present), injects it into `agents.md` via template, regenerates `context.md`,
   snapshots Claude auto-memory, mirrors topic files, and writes to
   `hosts/<role-slug>/memory/` in the private repository.
3. **Windows role hosts**: Run the same bridge script via Task Scheduler.
   Hermes steps are skipped (no Hermes on Windows); context.md, auto-memory
   snapshot, and topic mirrors are refreshed in the private repository.
4. **Return enrichment**: New lessons learned on any machine go into `KNOWLEDGE.md`
   or topic files in the private repository.

Private Git is the sync mechanism. The public workspace-hub repository is not a memory snapshot sink.

## Legal Compliance

- `.legal-deny-list.yaml` — 15 client name patterns, repo root
- Verify the final outgoing report per `docs/standards/FINAL_REPORT_VERIFICATION.md`; retain independent secret checks. Identifier gates are retired.
- Catalogs (`dde-*`, `conference-*`) are excluded from scanning
- MANDATORY for all document-intelligence and resource work
CONTEXT_EOF

echo "[bridge] context.md regenerated"

# ---------------------------------------------------------------------------
# 5. Snapshot Claude auto-memory MEMORY.md index
# ---------------------------------------------------------------------------
CLAUDE_AUTO="${CLAUDE_MEM_DIR}/MEMORY.md"
SNAPSHOT_OUT="${MEMORY_DIR}/claude-auto-memory.md"

if [[ -z "${CLAUDE_MEM_DIR}" || ! -f "${CLAUDE_AUTO}" ]]; then
    # Never skip silently. An unreachable source and a completed mirror looked
    # identical before this, which is how the bridge ran dead for weeks.
    echo -e "${YELLOW}[bridge] WARNING: Claude auto-memory index not found" \
            "(${CLAUDE_AUTO:-<unresolved>}) — claude-auto-memory.md left STALE," \
            "not refreshed. The snapshot below is NOT current.${NC}" >&2
else
    {
        echo "# Claude Code Auto-Memory Snapshot"
        echo ""
        echo "> Git-tracked snapshot of Claude Code's auto-generated MEMORY.md index."
        echo "> Last captured: ${TIMESTAMP}"
        echo "> Source: ${CLAUDE_AUTO}"
        echo ""
        cat "${CLAUDE_AUTO}"
    } > "${SNAPSHOT_OUT}"
    echo "[bridge] claude-auto-memory.md snapshot updated"
fi

# ---------------------------------------------------------------------------
# 6. Mirror Claude auto-memory topic files → private host topics/
#    Includes only non-sensitive feedback/preference files
# ---------------------------------------------------------------------------
MIRROR_PATTERNS=("feedback_*.md" "working-style.md" "ai-orchestration.md"
                 "shell-git-patterns.md" "data_format_guidelines.md"
                 "network_machines.md")
MIRRORED=0

if [[ -d "${CLAUDE_MEM_DIR}" ]]; then
    for pattern in "${MIRROR_PATTERNS[@]}"; do
        for src in ${CLAUDE_MEM_DIR}/${pattern}; do
            [[ -f "${src}" ]] || continue
            fname="$(basename "${src}")"
            dest="${TOPICS_DIR}/${fname}"
            {
                echo "> Git-tracked snapshot from Claude auto-memory. Captured: ${TIMESTAMP}"
                echo "> Source: ${src}"
                echo ""
                cat "${src}"
            } > "${dest}"
            MIRRORED=$((MIRRORED + 1))
        done
    done
    echo "[bridge] Mirrored ${MIRRORED} topic files to hosts/${HOST_SLUG}/memory/topics/"
fi

# ---------------------------------------------------------------------------
# 7. Report
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}[bridge] Private files updated for ${HOST_SLUG}:${NC}"
for file in agents.md context.md claude-auto-memory.md; do
    fp="${MEMORY_DIR}/${file}"
    [[ -f "${fp}" ]] && printf "  ✅ %-30s (%d lines)\n" "${file}" "$(wc -l < "${fp}")"
done
[[ ${MIRRORED} -gt 0 ]] && echo "  ✅ topics/ (${MIRRORED} files mirrored)"
echo ""

# ---------------------------------------------------------------------------
# 7b. Cross-provider read-back slices (#2841 Phase A, gap 1/2)
#   Source = the private host snapshot under claude-memory-snapshots. The bridge
#   writes provider read-back slices into the private host folder. Public
#   config/agents/*/MEMORY.runtime.md files are retained as reviewed redacted
#   subsets and are updated only through normal public repo review.
# ---------------------------------------------------------------------------
CURATE="${REPO_ROOT}/scripts/memory/curate_readback_slice.py"
if [[ -f "${CURATE}" ]]; then
    if command -v uv >/dev/null 2>&1 && uv run --no-project python -c "print(1)" >/dev/null 2>&1; then
        RBPY=(uv run --no-project python)
    else
        RBPY=(python3)
    fi
    # Topics INDEX (#3189) — regenerate inside the private host snapshot.
    _idx="${REPO_ROOT}/scripts/memory/build_topics_index.py"
    if [[ -f "${_idx}" ]]; then
        if "${RBPY[@]}" "${_idx}" --topics-dir "${TOPICS_DIR}" >/dev/null 2>&1; then
            echo "  ✅ hosts/${HOST_SLUG}/memory/topics/INDEX.md (topics index)"
        else
            echo "  ⚠️  WARN: topics INDEX generation failed — previous kept"
        fi
    fi
    for target in hermes codex gemini; do
        _tmp_slice=$(mktemp)
        if "${RBPY[@]}" "${CURATE}" --target "${target}" --source-dir "${MEMORY_DIR}" > "${_tmp_slice}"; then
            mv "${_tmp_slice}" "${READBACK_DIR}/${target}.md"
            echo "  ✅ hosts/${HOST_SLUG}/readback/${target}.md"
        else
            rm -f "${_tmp_slice}"
            echo "  ⚠️  WARN: ${target} read-back slice emit failed — previous kept"
        fi
    done
fi
echo ""

# ---------------------------------------------------------------------------
# 8. Commit (only if --commit flag and changes exist)
# ---------------------------------------------------------------------------
if [[ "${COMMIT_MODE}" == "--commit" ]]; then
    # Private-only commit path. Fails closed when the private repository is unavailable.
    # shellcheck source=scripts/memory/bridge-commit.sh
    source "${REPO_ROOT}/scripts/memory/bridge-commit.sh"
    bridge_private_commit_and_push "${PRIVATE_REPO}" "${HOST_SLUG}" "${TIMESTAMP}"
else
    echo -e "${YELLOW}[bridge] Dry-run complete. Add --commit to commit and push the private repo.${NC}"
fi
