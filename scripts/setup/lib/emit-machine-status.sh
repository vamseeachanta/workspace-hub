#!/usr/bin/env bash
# emit-machine-status.sh — Render per-machine harness-parity status to
# config/machine-baselines/<token>.{md,yaml} for control-plane fleet assessment.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 3, G9)
#
# Output paths (relative to repo root):
#   config/machine-baselines/<token>.yaml  — machine-readable (control-plane parses)
#   config/machine-baselines/<token>.md    — human-readable (operators comment on #2753)
#
# Hostname token policy (per r1 m4):
#   1. If config/agents/machines.yaml exists and contains `aliases: { hostname: alias }`,
#      use the alias as the file basename (e.g., "ace-linux-1").
#   2. Else: use the first 8 hex chars of sha256(hostname) (no PII leak).
#
# 22 dimensions per r2 C6 (expanded from 13 to cover all setup-critical state
# already validated by verify-setup.sh).
#
# Secret-scrub: 7 patterns per r2 C7. Status files are git-tracked → public on
# the repo → any token-shaped string must be redacted before write.

# --- Hostname token resolution ----------------------------------------------

get_raw_hostname() {
    hostname -s 2>/dev/null || hostname | cut -d. -f1
}

resolve_hostname_token() {
    local repo_root="$1"
    local raw; raw="$(get_raw_hostname)"
    local aliases_file="${repo_root}/config/agents/machines.yaml"

    if [[ -f "$aliases_file" ]]; then
        # Look for `<raw>: <alias>` under an `aliases:` heading.
        local alias
        alias=$(awk -v host="$raw" '
            /^aliases:/ { in_aliases=1; next }
            /^[^[:space:]]/ { in_aliases=0 }
            in_aliases && $1 == host":" { print $2; exit }
        ' "$aliases_file")
        if [[ -n "$alias" ]]; then
            echo "$alias"
            return 0
        fi
    fi

    # Fallback: sha256(hostname) truncated to 8 hex chars.
    printf '%s' "$raw" | sha256sum | cut -c1-8
}

# --- Secret scrubbing (7 patterns per r2 C7) --------------------------------

scrub_secrets() {
    # Apply all 7 redaction patterns. Stdin → stdout pipeline.
    local input="$1"
    printf '%s' "$input" | sed -E '
        s/gh[opsu]_[A-Za-z0-9]{20,}/[REDACTED_GH_TOKEN]/g
        s/github_pat_[A-Za-z0-9_]{20,}/[REDACTED_GH_PAT]/g
        s/sk-ant-[A-Za-z0-9_-]{20,}/[REDACTED_ANTHROPIC]/g
        s/sk-[A-Za-z0-9_-]{20,}/[REDACTED_OPENAI]/g
        s/AIza[A-Za-z0-9_-]{30,}/[REDACTED_GOOGLE]/g
        s/eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/[REDACTED_JWT]/g
        s/("(refresh_token|access_token)"):[[:space:]]*"[^"]+"/\1: "[REDACTED_OAUTH]"/g
    '
}

# --- 22 dimension checks (each returns PASS|WARN|FAIL|"machine-local-by-design"|n/a) ---
# Each is a wrapper so tests can override individual checks.

check_dimension_soul_contracts()        { [[ -f "${REPO_ROOT:-.}/config/agents/SHARED_SOUL.md" ]] && echo PASS || echo FAIL; }
check_dimension_skills()                { [[ -d "${REPO_ROOT:-.}/.claude/skills" ]] && echo PASS || echo FAIL; }
check_dimension_rules()                 { [[ -d "${REPO_ROOT:-.}/.claude/rules" ]] && echo PASS || echo FAIL; }
check_dimension_bridged_memory()        { [[ -d "${REPO_ROOT:-.}/.claude/memory" ]] && echo PASS || echo FAIL; }
check_dimension_claude_global_pointer() { [[ -f "${HOME}/.claude/CLAUDE.md" ]] && echo PASS || echo FAIL; }
check_dimension_codex_agents_symlink()  { [[ -L "${HOME}/.codex/AGENTS.md" ]] && echo PASS || echo WARN; }
check_dimension_hermes_soul_symlink()   { [[ -L "${HOME}/.hermes/SOUL.md" ]] && echo PASS || echo WARN; }
check_dimension_claude_cli_auth()       { [[ -f "${HOME}/.claude/.credentials.json" ]] && echo PASS || echo WARN; }
check_dimension_codex_cli_auth()        { [[ -f "${HOME}/.codex/auth.json" ]] && echo PASS || echo WARN; }
check_dimension_gh_cli_auth()           { gh auth status >/dev/null 2>&1 && echo PASS || echo WARN; }
check_dimension_gemini_cli_auth()       { [[ -f "${HOME}/.gemini/oauth_creds.json" ]] && echo PASS || echo WARN; }
check_dimension_hermes_can_boot()       { [[ -f "${HOME}/.hermes/config.yaml" ]] && echo PASS || echo WARN; }
check_dimension_raw_session_state()     { echo "machine-local-by-design"; }
check_dimension_submodules_initialized() {
    # The pipe-into-subshell pattern produced "PASS\nWARN" malformed output in the
    # real run because `grep -c` exit codes interact with the subshell's
    # short-circuit chain in surprising ways. Use a clean substitution capture.
    local uninit_count
    uninit_count=$(git -C "${REPO_ROOT:-.}" submodule status 2>/dev/null | grep -c '^-' || true)
    uninit_count="${uninit_count:-0}"
    if [[ "$uninit_count" == "0" ]]; then echo PASS; else echo WARN; fi
}
check_dimension_git_hooks_installed()   { [[ -x "${REPO_ROOT:-.}/.git/hooks/pre-commit" ]] && echo PASS || echo WARN; }
check_dimension_shell_profile_wired()   { grep -qF "bashrc-snippets" "${HOME}/.bashrc" 2>/dev/null && echo PASS || echo WARN; }
check_dimension_npm_global_prefix()     { [[ -n "$(npm config get prefix 2>/dev/null)" ]] && echo PASS || echo WARN; }
check_dimension_scheduler_entries()     { (crontab -l 2>/dev/null | grep -qc workspace-hub) && echo PASS || echo WARN; }
check_dimension_ssh_key_present()       { ls "${HOME}/.ssh/id_"* >/dev/null 2>&1 && echo PASS || echo WARN; }
check_dimension_env_file_present()      { [[ -f "${REPO_ROOT:-.}/.env" ]] && echo PASS || echo WARN; }
check_dimension_uv_or_python_available(){ (command -v uv >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1) && echo PASS || echo FAIL; }
check_dimension_git_bash_available() {
    # Windows-specific: detect Git Bash. On other OSes returns "n/a".
    case "$(uname -s 2>/dev/null)" in
        MINGW*|CYGWIN*|MSYS*)
            [[ -x "/c/Program Files/Git/bin/bash.exe" ]] && echo PASS || echo FAIL ;;
        *) echo "n/a" ;;
    esac
}

# --- CLI version helpers -----------------------------------------------------

cli_version() {
    # $1 = cli name; returns version string or "absent"
    if command -v "$1" >/dev/null 2>&1; then
        "$1" --version 2>/dev/null | head -1 | awk '{print $NF}'
    else
        echo "absent"
    fi
}

# --- Main entry point --------------------------------------------------------

emit_machine_status() {
    local repo_root="$1"
    REPO_ROOT="$repo_root"   # exposed so dimension checks can read it

    local token; token="$(resolve_hostname_token "$repo_root")"
    local hostname_raw; hostname_raw="$(get_raw_hostname)"
    local os_token; os_token="$(uname -s 2>/dev/null)"
    case "$os_token" in
        Linux*)               os_token="linux" ;;
        Darwin*)              os_token="macos" ;;
        MINGW*|CYGWIN*|MSYS*) os_token="windows" ;;
        *)                    os_token="unknown" ;;
    esac
    local timestamp; timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    local out_dir="${repo_root}/config/machine-baselines"
    mkdir -p "$out_dir"
    local yaml_file="${out_dir}/${token}.yaml"
    local md_file="${out_dir}/${token}.md"

    # --- Collect dimension status into a temp buffer ---
    local dims_yaml=""
    for dim in soul_contracts skills rules bridged_memory claude_global_pointer \
               codex_agents_symlink hermes_soul_symlink claude_cli_auth \
               codex_cli_auth gh_cli_auth gemini_cli_auth hermes_can_boot \
               raw_session_state submodules_initialized git_hooks_installed \
               shell_profile_wired npm_global_prefix scheduler_entries \
               ssh_key_present env_file_present uv_or_python_available \
               git_bash_available; do
        local status
        status="$("check_dimension_${dim}" 2>/dev/null || echo "WARN")"
        # Quote strings that look like they might be misparsed as YAML scalars
        if [[ "$status" =~ ^(PASS|WARN|FAIL)$ ]]; then
            dims_yaml="${dims_yaml}  ${dim}: ${status}"$'\n'
        else
            dims_yaml="${dims_yaml}  ${dim}: \"${status}\""$'\n'
        fi
    done

    # --- CLI versions ---
    local clis_yaml=""
    for cli in claude codex gh gemini hermes node npm uv; do
        local ver; ver="$(cli_version "$cli")"
        clis_yaml="${clis_yaml}  ${cli}: \"${ver}\""$'\n'
    done

    # --- Render YAML ---
    local yaml_content
    yaml_content="$(cat <<YAMLEOF
# Per-machine harness-parity status — issue #2751 G9
# Generated by scripts/setup/lib/emit-machine-status.sh
# Token resolution: ${token}  (alias or sha256 of raw hostname per r1 m4 policy)
# Posted to operational tracker: #2753

hostname: "${hostname_raw}"
os: "${os_token}"
last_updated: "${timestamp}"

dimensions:
${dims_yaml%$'\n'}

cli_versions:
${clis_yaml%$'\n'}
YAMLEOF
)"

    # Scrub secrets before write (defense-in-depth — versions/hostnames shouldn't
    # contain tokens, but if a malformed cli --version ever emits one we redact).
    yaml_content="$(scrub_secrets "$yaml_content")"
    printf '%s\n' "$yaml_content" > "$yaml_file"

    # --- Render MD (human-readable rendering of same data) ---
    local md_content
    md_content="$(cat <<MDEOF
# Machine baseline: ${hostname_raw}

> **Token**: \`${token}\`  •  **OS**: \`${os_token}\`  •  **Last updated**: \`${timestamp}\`
> Source: \`scripts/setup/lib/emit-machine-status.sh\` (issue #2751 G9)
> Operational tracker: #2753 — paste this report there after running setup

## Harness-parity dimensions (22)

| Dimension | Status |
|---|---|
$(printf '%s' "$dims_yaml" | sed -E 's/^  ([a-z_]+): (.+)$/| \1 | \2 |/' | sort)

## CLI versions

| CLI | Version |
|---|---|
$(printf '%s' "$clis_yaml" | sed -E 's/^  ([a-z]+): "(.+)"$/| \1 | \2 |/' | sort)
MDEOF
)"
    md_content="$(scrub_secrets "$md_content")"
    printf '%s\n' "$md_content" > "$md_file"

    echo "[emit-machine-status] wrote ${yaml_file} and ${md_file}"
}
