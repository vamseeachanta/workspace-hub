#!/usr/bin/env bash
# ABOUTME: Auto-update AI CLI tools that are behind or missing per ai-tools-status.yaml
# ABOUTME: Called by ai-tools-status.sh after each status check. Skips node/gh (apt-managed).
# Usage: ./ai-tools-update.sh [--quiet] [--dry-run]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATUS_DIR="$REPO_ROOT/config/ai_agents/status"
THIS_HOST=$(hostname -s)
STATUS_FILE="$STATUS_DIR/$THIS_HOST.yaml"
QUIET="${1:-}"
DRY_RUN="${2:-}"

log()  { [[ "$QUIET" == "--quiet" ]] || echo "$*"; }
info() { log "[ai-tools-update] $*"; }

# ── detect if a tool needs sudo (installed in system prefix) ──────────────────
needs_sudo() {
    local cmd="$1"
    local path
    if path=$(command -v "$cmd" 2>/dev/null); then
        [[ "$path" == /usr/local/* || "$path" == /usr/bin/* ]] && echo "sudo" || echo ""
    else
        # Not installed — check npm prefix
        local prefix; prefix=$(npm config get prefix 2>/dev/null || echo "")
        [[ "$prefix" == /usr/local || "$prefix" == /usr ]] && echo "sudo" || echo ""
    fi
}

# ── install/update a single npm tool ─────────────────────────────────────────
update_npm_tool() {
    local tool="$1" pkg="$2"
    local sudo_prefix; sudo_prefix=$(needs_sudo "$tool")
    info "Updating $tool ($pkg)..."
    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        info "  [dry-run] ${sudo_prefix:+sudo }npm install -g ${pkg}@latest"
        return
    fi
    if ${sudo_prefix:+sudo} npm install -g "${pkg}@latest" 2>&1 | grep -v "^npm warn" | tail -3; then
        local new_ver; new_ver=$("$tool" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)
        info "  $tool updated to $new_ver"
    else
        info "  ERROR: $tool update failed — may need manual sudo or Node upgrade"
    fi
}

# ── parse status YAML for a field value ──────────────────────────────────────
get_ver()    { grep "^  $1:" "$STATUS_FILE" 2>/dev/null | awk '{print $2}' | tr -d '"'; }
get_latest() { grep "^  $1:" "$STATUS_FILE" 2>/dev/null | awk 'NR==1{print $2}' | tr -d '"'; }

# ── tool → npm package map ────────────────────────────────────────────────────
declare -A NPM_PKG=(
    [claude]="@anthropic-ai/claude-code"
    [codex]="@openai/codex"
    [gemini]="@google/gemini-cli"
)

# ── main ──────────────────────────────────────────────────────────────────────
if [[ ! -f "$STATUS_FILE" ]]; then
    info "No status file found at $STATUS_FILE — run ai-tools-status.sh first"
    exit 0
fi

overall=$(grep "^status:" "$STATUS_FILE" | awk '{print $2}')
if [[ "$overall" == "ok" ]]; then
    info "All tools up-to-date on $THIS_HOST — nothing to do"
    exit 0
fi

info "Updating tools on $THIS_HOST..."
updated=0

# Check node version — skip npm tools if node < 20, warn instead
node_v=$(get_ver node | sed 's/"//g')
node_major=$(echo "$node_v" | cut -d. -f1)
if (( node_major < 20 )); then
    info "  SKIP: Node $node_v < 20 — upgrade Node first (see WRK-576), then re-run"
    exit 1
fi

# Update each npm-managed tool if behind or missing
for tool in claude codex gemini; do
    installed=$(grep "  $tool:" "$STATUS_FILE" | head -1 | awk '{print $2}' | tr -d '"')
    latest=$(grep "^  $tool:" "$STATUS_FILE" 2>/dev/null | awk '{print $2}' | tr -d '"')

    # Re-read from versions: and latest: blocks properly
    installed=$(awk '/^versions:/{f=1} f && /  '"$tool"':/{print $2; exit}' "$STATUS_FILE" | tr -d '"')
    latest=$(awk '/^latest:/{f=1} f && /  '"$tool"':/{print $2; exit}' "$STATUS_FILE" | tr -d '"')

    if [[ "$installed" == "not-installed" || ( "$installed" != "$latest" && -n "$latest" && "$latest" != "unknown" ) ]]; then
        update_npm_tool "$tool" "${NPM_PKG[$tool]}"
        (( updated++ ))
    else
        info "  $tool $installed — ok"
    fi
done

# gh and node: apt-managed, skip with guidance
gh_v=$(awk '/^versions:/{f=1} f && /  gh:/{print $2; exit}' "$STATUS_FILE" | tr -d '"')
[[ "$gh_v" == "not-installed" ]] && info "  SKIP gh: install via 'sudo apt install gh' or GitHub CLI apt repo"

info "Done. $updated tool(s) updated on $THIS_HOST."
