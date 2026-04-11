#!/usr/bin/env bash
# bridge-hermes-claude.sh — Refresh repo-tracked memory outputs (.claude/memory/)
#
# Architecture: Memory travels with the repository via git.
#   On Linux (ace-linux-1): Hermes writes memory → ~/.hermes/memories/ → this
#     script extracts canonical facts → .claude/memory/ → git commit + push
#   On Windows (licensed-win-1, Git Bash): No Hermes — this script still
#     refreshes context.md, snapshots Claude auto-memory, and mirrors topic
#     files → git commit + push.  Hermes-specific steps are skipped gracefully.
#   Any machine doing git pull gets the same context automatically.
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

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
MEMORY_DIR="${REPO_ROOT}/.claude/memory"
TEMPLATE_DIR="${MEMORY_DIR}/templates"
TOPICS_DIR="${MEMORY_DIR}/topics"
HERMES_MEM_DIR="${HOME}/.hermes/memories"
# Derive Claude auto-memory path from workspace root (portable across Linux / Windows Git Bash)
_project_slug="$(cd "${REPO_ROOT}" && pwd | tr '/' '-')"
CLAUDE_MEM_DIR="${HOME}/.claude/projects/${_project_slug}/memory"
TIMESTAMP="$(date +%Y-%m-%d)"
COMMIT_MODE="${1:-}"

# Colours
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

mkdir -p "${MEMORY_DIR}" "${TOPICS_DIR}"

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

> Git-tracked. Travels with the repo. Managed by scripts/memory/bridge-hermes-claude.sh
> Source of truth for environment conventions on every machine that clones workspace-hub.

## Machines

| Machine | OS | Hermes | Python cmd | Workspace root |
|---------|----|--------|------------|----------------|
| ace-linux-1 | Linux | YES | `uv run` | `/mnt/local-analysis/workspace-hub` |
| licensed-win-1 | Windows | NO | `python` | `D:\workspace-hub` |

## Python Command Rule

- **Linux**: ALWAYS `uv run` — never bare `python3` or `pip`
- **Windows**: Use `python` — uv is NOT installed on licensed-win-1

## Workspace Layout (Linux)

- `/mnt/local-analysis/workspace-hub/` — the real git repo mount
- `~/workspace-hub` — **sparse overlay** on ace-linux-1; writes may fail silently
  - If a write via tool fails: write to `/tmp/` first, then `mv` via terminal to the real mount
- `digitalmodel/` — **separate git repo** (vamseeachanta/digitalmodel.git), gitignored by parent
  - Commits MUST be made from inside `digitalmodel/` — not from workspace-hub root
- `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent
- `worldenergydata/` — energy data sub-repo

## Windows Path Conventions

- MINGW64 bash: paths use `/d/workspace-hub/` (not `D:\workspace-hub`)
- `core.symlinks=false` — git treats junctions as dirs; never commit symlinks cross-platform
- Shell scripts: `#!/usr/bin/env bash`, LF line endings

## Memory Sync Model

Memory travels with the repo via git. No Hermes needed on Windows.

1. **Hermes (ace-linux-1)**: Writes authoritative facts to `~/.hermes/memories/`
2. **Bridge script** (`scripts/memory/bridge-hermes-claude.sh`): Reads Hermes memory
   (if present), injects it into `agents.md` via template, regenerates `context.md`,
   snapshots Claude auto-memory, mirrors topic files, commits and pushes.
   Runs on both Linux (cron) and Windows (Task Scheduler).
3. **Windows (licensed-win-1)**: Runs the same bridge script via Task Scheduler.
   Hermes steps are skipped (no Hermes on Windows); context.md, auto-memory
   snapshot, and topic mirrors are refreshed and pushed back to repo.
4. **Return enrichment**: New lessons learned on any machine go into `KNOWLEDGE.md`
   or topic files, committed and pushed. Next `git pull` on any machine picks them up.

Git IS the sync mechanism.

## Legal Compliance

- `.legal-deny-list.yaml` — 15 client name patterns, repo root
- Run `scripts/legal/legal-sanity-scan.sh` before committing any generated documents
- Catalogs (`dde-*`, `conference-*`) are excluded from scanning
- MANDATORY for all document-intelligence and resource work
CONTEXT_EOF

echo "[bridge] context.md regenerated"

# ---------------------------------------------------------------------------
# 5. Snapshot Claude auto-memory MEMORY.md index
# ---------------------------------------------------------------------------
CLAUDE_AUTO="${CLAUDE_MEM_DIR}/MEMORY.md"
SNAPSHOT_OUT="${MEMORY_DIR}/claude-auto-memory.md"

if [[ -f "${CLAUDE_AUTO}" ]]; then
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
# 6. Mirror Claude auto-memory topic files → .claude/memory/topics/
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
    echo "[bridge] Mirrored ${MIRRORED} topic files to .claude/memory/topics/"
fi

# ---------------------------------------------------------------------------
# 7. Report
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}[bridge] Files updated:${NC}"
for file in agents.md context.md claude-auto-memory.md; do
    fp="${MEMORY_DIR}/${file}"
    [[ -f "${fp}" ]] && printf "  ✅ %-30s (%d lines)\n" "${file}" "$(wc -l < "${fp}")"
done
[[ ${MIRRORED} -gt 0 ]] && echo "  ✅ topics/ (${MIRRORED} files mirrored)"
echo ""

# ---------------------------------------------------------------------------
# 8. Commit (only if --commit flag and changes exist)
# ---------------------------------------------------------------------------
if [[ "${COMMIT_MODE}" == "--commit" ]]; then
    cd "${REPO_ROOT}"
    # Diff-aware: only commit if something actually changed
    git add .claude/memory/
    if git diff --cached --quiet; then
        echo "[bridge] No changes to commit — .claude/memory/ is already up to date"
        exit 0
    fi

    # Stash any unrelated uncommitted changes so pull --rebase works
    HAS_STASH=false
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "[bridge] Uncommitted changes detected — stashing before pull..."
        git stash push -m "pre-bridge-stash"
        HAS_STASH=true
    fi

    git commit -m "chore(memory): auto-refresh memory bridge (${TIMESTAMP})"
    echo "[bridge] Committed. Pulling with rebase before push..."

    # Pull with rebase — abort if conflicts
    if ! git pull --rebase --autostash 2>&1; then
        echo "[bridge] ERROR: rebase conflict during pull — resolve manually, then git push"
        # Restore stashed changes if we stashed
        if [[ "${HAS_STASH}" = true ]]; then
            echo "[bridge] Restoring previously stashed changes..."
            git stash pop --index 2>/dev/null || true
        fi
        exit 1
    fi

    git push
    echo -e "${GREEN}[bridge] Done — committed and pushed.${NC}"

    # Restore stashed changes if we stashed
    if [[ "${HAS_STASH}" = true ]]; then
        echo "[bridge] Restoring previously stashed changes..."
        git stash pop 2>/dev/null || echo "[bridge] WARNING: stash pop failed — run 'git stash pop' manually"
    fi
else
    echo -e "${YELLOW}[bridge] Dry-run complete. Add --commit to commit and push.${NC}"
fi
