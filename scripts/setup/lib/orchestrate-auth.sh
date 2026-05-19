#!/usr/bin/env bash
# orchestrate-auth.sh — Interactive auth orchestration for AI-provider CLIs.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G3)
#
# Per the plan's UX Contract Phase C: this is "browser-blocking". Each
# `<cli> auth login` opens an OAuth browser flow; the script blocks waiting
# for the user to complete it. `--non-interactive` mode (via WH_NON_INTERACTIVE=1)
# skips all auth prompts for CI smoke tests.
#
# Auth-presence checks per the canonical paths discovered 2026-05-19:
#   claude  → ~/.claude/.credentials.json present
#   codex   → ~/.codex/auth.json present
#   gh      → `gh auth status` exits 0
#   gemini  → ~/.gemini/oauth_creds.json present
#   hermes  → ~/.hermes/.env present (populated)
#
# Gemini-specific (r1 m1 verified empirically 2026-05-19): Gemini CLI has NO
# `gemini auth` subcommand. To trigger OAuth, run `gemini -p ping` which
# provokes the browser flow on first use. Fallback: GEMINI_API_KEY env var.
#
# Hermes auth: not a `login` flow; populate ~/.hermes/.env interactively with
# values prompted via `read -s` (NEVER echoed to terminal per UX Contract
# secret-handling clause).
#
# Testability: same wrapper-function override pattern as install-provider-clis.sh.
#
# Usage:
#   source scripts/setup/lib/orchestrate-auth.sh
#   orchestrate_auth                       # interactive (default)
#   WH_NON_INTERACTIVE=1 orchestrate_auth  # CI / unattended mode

# --- Default wrapper implementations (overridable by tests) ------------------

auth_present() {
    case "$1" in
        claude)  [[ -f "${HOME}/.claude/.credentials.json" ]] ;;
        codex)   [[ -f "${HOME}/.codex/auth.json" ]] ;;
        gh)      gh auth status >/dev/null 2>&1 ;;
        gemini)  [[ -f "${HOME}/.gemini/oauth_creds.json" ]] ;;
        hermes)  [[ -s "${HOME}/.hermes/.env" ]] ;;
        *)       return 1 ;;
    esac
}

run_auth_login() {
    # $1 = cli, $2 = full command string to run
    local cli="$1" cmd="$2"
    echo ""
    echo "=== Auth: ${cli} ==="
    echo "Launching: ${cmd}"
    echo "Complete the browser flow if one opens, then return here."
    # shellcheck disable=SC2086
    eval "$cmd"
}

prompt_hermes_env() {
    # Hermes .env field prompts. Values read via `read -s` so they are NEVER
    # echoed to terminal. File written with mode 600 (user-readable only).
    # Idempotent: if file already exists and is non-empty, prompt for confirmation
    # before overwriting.
    local env_file="${HOME}/.hermes/.env"
    mkdir -p "${HOME}/.hermes"

    if [[ -s "$env_file" ]]; then
        echo "[orchestrate-auth] ${env_file} already populated — skip Hermes prompt."
        return 0
    fi

    echo ""
    echo "=== Hermes .env prompt ==="
    echo "Enter values for Hermes runtime — input is hidden (read -s); values"
    echo "are NEVER echoed and are written with mode 600. Leave blank to skip."
    echo ""

    local telegram_token openai_key anthropic_key
    printf "HERMES_TELEGRAM_BOT_TOKEN: "
    read -rs telegram_token; echo ""
    printf "HERMES_OPENAI_API_KEY:      "
    read -rs openai_key; echo ""
    printf "HERMES_ANTHROPIC_API_KEY:   "
    read -rs anthropic_key; echo ""

    {
        echo "# Hermes runtime credentials — populated by scripts/setup/lib/orchestrate-auth.sh"
        echo "# Per #2751 UX Contract: values never echoed; file mode 600."
        [[ -n "$telegram_token" ]] && echo "HERMES_TELEGRAM_BOT_TOKEN=${telegram_token}"
        [[ -n "$openai_key" ]]     && echo "HERMES_OPENAI_API_KEY=${openai_key}"
        [[ -n "$anthropic_key" ]]  && echo "HERMES_ANTHROPIC_API_KEY=${anthropic_key}"
    } > "$env_file"
    chmod 600 "$env_file"
    echo "[orchestrate-auth] Wrote ${env_file} (mode 600)."
}

# --- Main entry point --------------------------------------------------------

orchestrate_auth() {
    # --non-interactive: skip everything (CI mode)
    if [[ "${WH_NON_INTERACTIVE:-0}" == "1" ]]; then
        echo "[orchestrate-auth] WH_NON_INTERACTIVE=1 — skipping all auth flows."
        return 0
    fi

    # CLI auth flows.
    # Note Gemini uses `gemini -p ping` per r1 m1 — no `gemini auth` subcommand
    # exists in the installed Gemini CLI (verified live 2026-05-19).
    local cli cmd
    for entry in \
        "claude|claude auth login" \
        "codex|codex auth login" \
        "gh|gh auth login" \
        "gemini|gemini -p ping"; do
        cli="${entry%%|*}"
        cmd="${entry#*|}"
        if auth_present "$cli"; then
            echo "[orchestrate-auth] ${cli}: already authenticated — skip."
        else
            run_auth_login "$cli" "$cmd"
        fi
    done

    # Hermes .env prompt (separate from CLI auth flows).
    if auth_present hermes; then
        echo "[orchestrate-auth] hermes: .env populated — skip."
    else
        prompt_hermes_env
    fi
}
