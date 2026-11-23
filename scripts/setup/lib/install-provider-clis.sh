#!/usr/bin/env bash
# install-provider-clis.sh — Channel-branched auto-install for AI-provider CLIs.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G2)
#
# Per the plan's UX Contract Phase B: this is "elevation-required" — sudo/admin
# prompts may appear during system-package installs; `-y` auto-confirmation is
# pre-supplied but elevation itself is unavoidable on most OSes.
#
# Channel-branched per r2 C2 finding (the original `pkg_install <cli>` pseudocode
# was wrong — 3 of 4 CLIs are npm packages, only `gh` is a system pkg):
#   - gh       → system pkg (apt-get/brew/choco/winget)
#   - claude   → npm: @anthropic-ai/claude-code
#   - gemini   → npm: @google/gemini-cli  (verified live 2026-05-19)
#   - codex    → custom: reuse scripts/install/pin-codex.sh (existing precedent)
#   - hermes   → out-of-band (warn-only; documented in PROVIDER_AUTH_GUIDE.md)
#
# Testability: install/check operations are wrapped in functions (has_cli,
# run_pkg_install, run_npm_install_global, run_pin_codex, run_node_install,
# elevate_check) so tests can override them via `function name() { ... }` after
# sourcing. See tests/setup/test_install_provider_clis.sh for the pattern.
#
# Usage:
#   source scripts/setup/lib/install-provider-clis.sh
#   install_provider_clis "$(detect_os)"

# Constants — npm package names for provider CLIs
WH_NPM_CLAUDE="@anthropic-ai/claude-code"
WH_NPM_GEMINI="@google/gemini-cli"

# --- Default wrapper implementations (overridable by tests) ------------------

has_cli() {
    # Returns 0 if $1 is on PATH, 1 otherwise.
    command -v "$1" >/dev/null 2>&1
}

elevate_check() {
    # On linux/macos: warn if not root and sudo is unavailable.
    # On windows: PowerShell sibling handles UAC; bash path is best-effort.
    if [[ "$(id -u 2>/dev/null)" != "0" ]] && ! command -v sudo >/dev/null 2>&1; then
        echo "[install-provider-clis] elevation required but sudo not found — install may fail" >&2
    fi
}

run_pkg_install() {
    # $1 = os, $2 = cli (only `gh` uses this channel in v1)
    local os="$1" cli="$2"
    case "$os" in
        linux)   sudo apt-get install -y "$cli" ;;
        macos)   brew install "$cli" ;;
        windows) choco install -y "$cli" || winget install -e --id "GitHub.cli" ;;
        *) echo "[install-provider-clis] unknown OS for pkg_install: $os" >&2; return 1 ;;
    esac
}

run_npm_install_global() {
    # $1 = npm package name
    npm install -g "$1"
}

run_pin_codex() {
    # Reuse the existing pin-codex.sh script (per scripts/install/pin-codex.sh).
    # Resolves repo root from BASH_SOURCE because this helper may be sourced
    # from anywhere (test fixtures, new-machine-setup.sh, ad-hoc).
    local helper_dir; helper_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local repo_root; repo_root="$(cd "${helper_dir}/../../.." && pwd)"
    bash "${repo_root}/scripts/install/pin-codex.sh"
}

run_node_install() {
    # $1 = os
    local os="$1"
    case "$os" in
        linux)   sudo apt-get install -y nodejs npm ;;
        macos)   brew install node ;;
        windows) choco install -y nodejs || winget install -e --id "OpenJS.NodeJS" ;;
        *) echo "[install-provider-clis] unknown OS for node_install: $os" >&2; return 1 ;;
    esac
}

# --- Main entry point --------------------------------------------------------

install_provider_clis() {
    local os="$1"

    # --- gh: system-package channel ---
    if ! has_cli gh; then
        elevate_check
        run_pkg_install "$os" gh
    fi

    # --- Determine whether any npm-channel CLI is needed ---
    local needs_node=false
    if ! has_cli claude; then needs_node=true; fi
    if ! has_cli gemini; then needs_node=true; fi

    if [[ "$needs_node" == "true" ]]; then
        if ! has_cli node || ! has_cli npm; then
            elevate_check
            run_node_install "$os"
        fi
    fi

    # --- claude, gemini: npm channel ---
    if ! has_cli claude; then
        run_npm_install_global "$WH_NPM_CLAUDE"
    fi
    if ! has_cli gemini; then
        run_npm_install_global "$WH_NPM_GEMINI"
    fi

    # --- codex: custom pin script ---
    if ! has_cli codex; then
        run_pin_codex
    fi

    # --- hermes: out-of-band ---
    if ! has_cli hermes; then
        echo "[install-provider-clis] hermes binary not detected." >&2
        echo "  Install per docs/setup/PROVIDER_AUTH_GUIDE.md (out-of-band; not auto-installed in v1)." >&2
    fi
}
