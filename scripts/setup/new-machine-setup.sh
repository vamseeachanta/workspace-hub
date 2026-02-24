#!/usr/bin/env bash
# new-machine-setup.sh — Single-command bootstrap for workspace-hub (WRK-313).
# Idempotent: safe to re-run after rebuilds or on existing machines.
#
# Usage:
#   bash scripts/setup/new-machine-setup.sh              # full setup
#   bash scripts/setup/new-machine-setup.sh --no-cron   # skip crontab install
#   bash scripts/setup/new-machine-setup.sh --dry-run   # preview only
#
# After completion, run: source ~/.bashrc && bash scripts/setup/verify-setup.sh
#
# Platform: bash (Linux primary, Windows Git Bash / MINGW64 secondary)
# See: .claude/docs/new-machine-setup.md for the full living reference.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ── Parse flags ───────────────────────────────────────────────────────────────
NO_CRON=false
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --no-cron)  NO_CRON=true ;;
    --dry-run)  DRY_RUN=true ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────
log()  { echo "[setup] $*"; }
step() { echo ""; echo "=== $* ==="; }
dry()  { [[ "$DRY_RUN" == "true" ]] && echo "  [dry-run] $*" || true; }

WH_OS="linux"
case "$(uname -s 2>/dev/null)" in
  MINGW*|CYGWIN*|MSYS*) WH_OS="windows" ;;
esac

HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')

echo ""
echo "=== workspace-hub new-machine setup (WRK-313) ==="
log "Host:      ${HOSTNAME_SHORT}"
log "OS:        ${WH_OS}"
log "Workspace: ${WORKSPACE_HUB}"
log "Dry-run:   ${DRY_RUN}"
log "Date:      $(date +%Y-%m-%d)"

# ── Step 1: Submodules ────────────────────────────────────────────────────────
step "1. Submodule initialisation"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "git submodule update --init --recursive"
else
  log "Initialising submodules (may take a moment)..."
  git -C "$WORKSPACE_HUB" submodule update --init --recursive
  log "Submodules ready."
fi

# ── Step 2: Git hooks ─────────────────────────────────────────────────────────
step "2. Git hooks"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/setup/install-all-hooks.sh"
else
  bash "${WORKSPACE_HUB}/scripts/setup/install-all-hooks.sh"
fi

# ── Step 3: Claude statusline ─────────────────────────────────────────────────
step "3. Claude statusline"
CLAUDE_SETTINGS_DIR="${HOME}/.claude"
CLAUDE_SETTINGS="${CLAUDE_SETTINGS_DIR}/settings.json"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "claude config set statusBarEnabled true  (or update ${CLAUDE_SETTINGS})"
else
  if command -v claude &>/dev/null; then
    claude config set statusBarEnabled true 2>/dev/null \
      && log "statusBarEnabled set via claude CLI" \
      || {
        # Fallback: direct JSON merge (handles fresh install without interactive session)
        mkdir -p "$CLAUDE_SETTINGS_DIR"
        if [[ -f "$CLAUDE_SETTINGS" ]]; then
          # Merge into existing settings.json using python3 (available on all targets)
          python3 - "$CLAUDE_SETTINGS" <<'PYSCRIPT'
import sys, json, pathlib
p = pathlib.Path(sys.argv[1])
data = json.loads(p.read_text()) if p.stat().st_size > 0 else {}
data["statusBarEnabled"] = True
p.write_text(json.dumps(data, indent=2) + "\n")
PYSCRIPT
          log "statusBarEnabled merged into ${CLAUDE_SETTINGS}"
        else
          echo '{"statusBarEnabled": true}' > "$CLAUDE_SETTINGS"
          log "Created ${CLAUDE_SETTINGS} with statusBarEnabled"
        fi
      }
  else
    mkdir -p "$CLAUDE_SETTINGS_DIR"
    if [[ -f "$CLAUDE_SETTINGS" ]]; then
      python3 - "$CLAUDE_SETTINGS" <<'PYSCRIPT'
import sys, json, pathlib
p = pathlib.Path(sys.argv[1])
data = json.loads(p.read_text()) if p.stat().st_size > 0 else {}
data["statusBarEnabled"] = True
p.write_text(json.dumps(data, indent=2) + "\n")
PYSCRIPT
      log "statusBarEnabled merged into ${CLAUDE_SETTINGS}"
    else
      echo '{"statusBarEnabled": true}' > "$CLAUDE_SETTINGS"
      log "Created ${CLAUDE_SETTINGS} with statusBarEnabled (claude CLI not found)"
    fi
    log "WARN: claude CLI not on PATH — install: npm install -g @anthropic-ai/claude-code"
  fi
fi

# ── Step 4: Shell aliases + prompt ────────────────────────────────────────────
step "4. Shell aliases"
SNIPPET="${WORKSPACE_HUB}/config/shell/bashrc-snippets.sh"

if [[ "$WH_OS" == "windows" ]]; then
  SHELL_RC="${HOME}/.bash_profile"
else
  SHELL_RC="${HOME}/.bashrc"
fi

MARKER="# workspace-hub bashrc-snippets"
if grep -qF "$MARKER" "$SHELL_RC" 2>/dev/null; then
  log "Aliases already present in ${SHELL_RC} — skipping."
elif [[ "$DRY_RUN" == "true" ]]; then
  dry "append source ${SNIPPET} to ${SHELL_RC}"
else
  {
    echo ""
    echo "${MARKER} (WRK-313)"
    echo "source \"${SNIPPET}\""
  } >> "$SHELL_RC"
  log "Appended source line to ${SHELL_RC}"
fi

# ── Step 5: PATH — npm global bin ─────────────────────────────────────────────
step "5. PATH / npm global bin"
if [[ "$WH_OS" == "linux" ]]; then
  NPM_GLOBAL="${HOME}/.npm-global"
  if command -v npm &>/dev/null; then
    if [[ "$DRY_RUN" == "true" ]]; then
      dry "npm config set prefix ${NPM_GLOBAL}"
    else
      npm config set prefix "$NPM_GLOBAL" 2>/dev/null || true
      log "npm global prefix: ${NPM_GLOBAL}"
    fi
  else
    log "WARN: npm not found — install Node.js (required for claude/codex CLIs)"
  fi
else
  log "Windows: npm global bin already on PATH via Git Bash — no action needed."
fi

# ── Step 6: Crontab ───────────────────────────────────────────────────────────
step "6. Crontab"
if [[ "$NO_CRON" == "true" ]]; then
  log "Skipped (--no-cron flag)."
elif [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/cron/setup-cron.sh --dry-run"
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" --dry-run || true
elif [[ "$WH_OS" == "windows" ]]; then
  log "Windows detected — printing Task Scheduler instructions:"
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" || true
else
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"
fi

# ── Step 7: SSH key check ─────────────────────────────────────────────────────
step "7. SSH key"
if ls "${HOME}/.ssh/id_"* &>/dev/null; then
  log "SSH key already present in ~/.ssh/"
else
  if [[ "$DRY_RUN" == "true" ]]; then
    dry "ssh-keygen -t ed25519 -C \"\$(hostname)\""
  else
    log "No SSH key found. Generating ed25519 key..."
    ssh-keygen -t ed25519 -C "${HOSTNAME_SHORT}" -f "${HOME}/.ssh/id_ed25519" -N ""
    log "Generated ${HOME}/.ssh/id_ed25519"
    log "Add public key to ace-linux-1 with: ssh-copy-id vamsee@ace-linux-1"
  fi
fi

# ── Step 8: .env.example check ───────────────────────────────────────────────
step "8. Environment variables"
ENV_EXAMPLE="${WORKSPACE_HUB}/.env.example"
ENV_LOCAL="${WORKSPACE_HUB}/.env"
if [[ ! -f "$ENV_EXAMPLE" ]]; then
  log "WARN: .env.example not found — expected at workspace root"
elif [[ -f "$ENV_LOCAL" ]]; then
  log ".env already exists — skipping copy."
elif [[ "$DRY_RUN" == "true" ]]; then
  dry "cp .env.example .env  (then fill in secrets)"
else
  cp "$ENV_EXAMPLE" "$ENV_LOCAL"
  log "Copied .env.example → .env — fill in required secrets before first session."
fi

# ── Step 9: Verify ────────────────────────────────────────────────────────────
step "9. Post-setup verification"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/setup/verify-setup.sh"
else
  bash "${WORKSPACE_HUB}/scripts/setup/verify-setup.sh" || true
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. source ${SHELL_RC}"
echo "  2. bash ${WORKSPACE_HUB}/scripts/setup/verify-setup.sh"
if [[ "$WH_OS" == "linux" ]]; then
  echo "  3. crontab -l   # confirm cron entries"
fi
echo "  4. See .claude/docs/new-machine-setup.md for manual steps."
echo ""
