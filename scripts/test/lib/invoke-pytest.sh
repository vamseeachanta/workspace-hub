#!/usr/bin/env bash
# invoke-pytest.sh — Standardized pytest invocation per repo.
# Usage: invoke-pytest.sh <repo_name> <tier> [pytest_args...]
#   repo_name: worldenergydata | digitalmodel | workspace-hub
#   tier: 1 (commit) | 2 (task) | 3 (session)
#   pytest_args: additional args passed to pytest (test paths, markers, etc.)

set -euo pipefail

_INVOKE_PYTEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_INVOKE_CONFIG_DIR="${_INVOKE_PYTEST_DIR}/../config"

invoke_pytest() {
    local repo_name="$1"
    local tier="$2"
    shift 2
    local pytest_args=("$@")

    # Validate repo name — only alphanumeric, hyphens, underscores allowed
    if [[ ! "$repo_name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "ERROR: Invalid repo name '${repo_name}' (must be alphanumeric/hyphens/underscores)" >&2
        return 1
    fi

    # Load repo config
    local config_file="${_INVOKE_CONFIG_DIR}/${repo_name}.conf"
    if [[ ! -f "$config_file" ]]; then
        echo "ERROR: No config for repo '${repo_name}' at ${config_file}" >&2
        return 1
    fi
    # shellcheck source=/dev/null
    source "$config_file"

    # Check if repo directory exists
    if [[ ! -d "$REPO_ROOT" ]]; then
        echo "ERROR: Repo directory not found: ${REPO_ROOT}" >&2
        return 1
    fi

    # Build pytest command
    local pytest_cmd
    local extra_args=()

    # Determine pytest binary
    if [[ "$PYTEST_BIN" == .venv/* ]]; then
        local venv_bin="${REPO_ROOT}/${PYTEST_BIN}"
        if [[ -x "$venv_bin" ]]; then
            pytest_cmd="$venv_bin"
        else
            echo "WARN: Venv pytest not found at ${venv_bin}, falling back to system" >&2
            pytest_cmd="python3 -m pytest"
        fi
    else
        pytest_cmd="$PYTEST_BIN"
    fi

    # Tier-specific configuration
    case "$tier" in
        1)  # Pre-commit: fast, no coverage, unit-only
            extra_args+=(-x --no-header -q)
            extra_args+=(-o "addopts=-v --tb=short")
            extra_args+=(-o "timeout=30")
            extra_args+=(-m "not slow and not benchmark and not performance and not integration")
            ;;
        2)  # Per-task: module-scoped with coverage
            extra_args+=(-o "addopts=-v --tb=short --strict-markers")
            extra_args+=(-o "timeout=60")
            extra_args+=(-m "not slow and not benchmark")
            ;;
        3)  # Per-session: full suite
            # Use pytest.ini defaults (full addopts) if possible
            if [[ "$PYTEST_BIN" == .venv/* ]] && [[ -x "${REPO_ROOT}/${PYTEST_BIN}" ]]; then
                # Venv has all plugins — use full config
                extra_args+=(-n auto --dist loadscope)
            else
                # System python — override addopts to avoid missing plugins
                extra_args+=(-o "addopts=-v --tb=short --strict-markers")
            fi
            ;;
        *)
            echo "ERROR: Unknown tier '${tier}'. Use 1, 2, or 3." >&2
            return 1
            ;;
    esac

    # Execute in subshell to avoid polluting caller's environment
    echo "--- [${repo_name}] Tier ${tier} ---"

    # Combine extra_args and pytest_args
    local full_cmd=($pytest_cmd "${extra_args[@]}" "${pytest_args[@]}")

    if [[ "${DRY_RUN:-}" == "1" ]]; then
        echo "DRY_RUN: ${full_cmd[*]}"
        return 0
    fi

    # Subshell isolates cd and PYTHONPATH changes from caller
    (
        export PYTHONPATH="${PYTHONPATH_EXTRA}"
        cd "$REPO_ROOT"
        "${full_cmd[@]}"
    )
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 2 ]]; then
        echo "Usage: invoke-pytest.sh <repo_name> <tier> [pytest_args...]" >&2
        echo "  repo_name: worldenergydata | digitalmodel | workspace-hub" >&2
        echo "  tier: 1 (commit) | 2 (task) | 3 (session)" >&2
        exit 1
    fi
    invoke_pytest "$@"
fi
