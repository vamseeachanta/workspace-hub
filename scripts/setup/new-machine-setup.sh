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

# ── Step 3b: Keybindings — Ctrl+Enter to submit (WRK-228) ───────────────────
step "3b. Claude keybindings (submit = Ctrl+Enter)"
CLAUDE_KB_SRC="${WORKSPACE_HUB}/config/claude/keybindings.json"
CLAUDE_KB_DST="${HOME}/.claude/keybindings.json"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "cp ${CLAUDE_KB_SRC} ${CLAUDE_KB_DST}"
elif [[ ! -f "$CLAUDE_KB_SRC" ]]; then
  log "WARN: config/claude/keybindings.json not found — skipping keybindings install"
elif [[ -f "$CLAUDE_KB_DST" ]]; then
  if cmp -s "$CLAUDE_KB_SRC" "$CLAUDE_KB_DST"; then
    log "keybindings.json already current — no change."
  else
    cp "$CLAUDE_KB_SRC" "$CLAUDE_KB_DST"
    log "keybindings.json updated (submitPrompt=ctrl+enter)"
  fi
else
  mkdir -p "${HOME}/.claude"
  cp "$CLAUDE_KB_SRC" "$CLAUDE_KB_DST"
  log "keybindings.json installed: ${CLAUDE_KB_DST}"
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

# ── Step 5b: Codex CLI pin (#2479) ────────────────────────────────────────────
step "5b. Codex CLI pin"
if command -v npm &>/dev/null; then
  if [[ "$DRY_RUN" == "true" ]]; then
    dry "PATH=\"${NPM_GLOBAL:-${HOME}/.npm-global}/bin:\$PATH\" bash scripts/install/pin-codex.sh"
  else
    PATH="${NPM_GLOBAL:-${HOME}/.npm-global}/bin:$PATH" bash "${WORKSPACE_HUB}/scripts/install/pin-codex.sh" || \
      log "WARN: Codex pin failed — run manually: bash scripts/install/pin-codex.sh"
  fi
else
  log "WARN: npm not found — skipping Codex pin"
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
    log "Add public key to dev-primary with: ssh-copy-id vamsee@dev-primary"
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

# ── Step 8b: tmux config ──────────────────────────────────────────────────────
step "8b. tmux config"
if command -v tmux &>/dev/null; then
  if [[ "$DRY_RUN" == "true" ]]; then
    dry "bash scripts/setup/deploy-tmux.sh"
  else
    bash "${WORKSPACE_HUB}/scripts/setup/deploy-tmux.sh"
  fi
else
  log "tmux not found — install with: sudo apt install tmux (Linux) or brew install tmux (macOS)"
fi

# ── Step 9: AI-provider harness (per #2751 G1) ───────────────────────────────
# Wires the AI-provider SOUL-runtime install into the main entry point.
# Calls bootstrap-machine.sh which now unconditionally creates ~/.hermes,
# ~/.codex, ~/.gemini parent directories before invoking install-soul-runtime.sh,
# closing the fresh-machine gap surfaced by Codex r2 finding C1.
step "9. AI-provider harness (SOUL-runtime symlinks)"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/memory/bootstrap-machine.sh"
else
  bash "${WORKSPACE_HUB}/scripts/memory/bootstrap-machine.sh"
fi

# ── Step 10: Auto-install provider CLIs (per #2751 G2) ────────────────────────
# Channel-branched install: gh via system pkg, claude/gemini via npm, codex via
# the existing scripts/install/pin-codex.sh. Hermes binary out-of-band (warn-only).
step "10. Auto-install provider CLIs"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "source scripts/setup/lib/install-provider-clis.sh && install_provider_clis ${WH_OS}"
else
  # shellcheck source=lib/install-provider-clis.sh
  source "${WORKSPACE_HUB}/scripts/setup/lib/install-provider-clis.sh"
  install_provider_clis "${WH_OS}" || log "WARN: CLI auto-install partial — re-run manually if needed"
fi

# ── Step 11: Auth orchestration (per #2751 G3) ────────────────────────────────
# Interactive: launches claude/codex/gh auth login + gemini -p ping + Hermes .env prompt.
# Bypass via WH_NON_INTERACTIVE=1 for CI smoke tests.
step "11. Auth orchestration"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "source scripts/setup/lib/orchestrate-auth.sh && orchestrate_auth"
else
  # shellcheck source=lib/orchestrate-auth.sh
  source "${WORKSPACE_HUB}/scripts/setup/lib/orchestrate-auth.sh"
  orchestrate_auth || log "WARN: auth orchestration partial — re-run to complete"
fi

# ── Step 12: Render Hermes config from template (per #2751 G4) ────────────────
# Idempotent — skips if ~/.hermes/config.yaml exists (preserves user edits).
step "12. Hermes config (~/.hermes/config.yaml)"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "source scripts/setup/lib/instantiate-hermes-config.sh && instantiate_hermes_config ${WORKSPACE_HUB}"
else
  # shellcheck source=lib/instantiate-hermes-config.sh
  source "${WORKSPACE_HUB}/scripts/setup/lib/instantiate-hermes-config.sh"
  instantiate_hermes_config "${WORKSPACE_HUB}" || log "WARN: Hermes config render failed"
fi

# ── Step 13: Emit machine-status report (per #2751 G9) ───────────────────────
# Writes config/machine-baselines/<token>.{md,yaml} with 22-dimension status.
# Hostname token uses alias-or-sha256 policy per r1 m4 (no PII leak).
# 7-pattern secret scrub applied to all output per r2 C7.
step "13. Emit machine-status report"
if [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/setup/emit-machine-status.sh ${WORKSPACE_HUB}"
else
  bash "${WORKSPACE_HUB}/scripts/setup/emit-machine-status.sh" "${WORKSPACE_HUB}" || \
    log "WARN: machine-status emission failed (non-fatal — re-run manually to capture)"
fi

# ── Step 14: Verify (renumbered from Step 9 per #2751 r2 — verify must run
#             LAST so it sees the new AI-provider state from Step 9) ──────────
step "14. Post-setup verification"
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
