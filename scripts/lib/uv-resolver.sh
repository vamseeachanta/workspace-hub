#!/usr/bin/env bash
# Source-safe uv binary resolver for shell entrypoints.

_uv_resolve_candidate_path() {
    local candidate="${1:-}"

    if [[ -z "$candidate" ]]; then
        return 1
    fi

    if [[ "$candidate" == */* ]]; then
        if [[ -x "$candidate" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
        return 1
    fi

    command -v "$candidate" 2>/dev/null || return 1
}

_uv_validate_candidate() {
    local candidate="${1:-}"
    local label="${2:-uv candidate}"
    local resolved=""

    if [[ -z "$candidate" ]]; then
        return 1
    fi

    if ! resolved="$(_uv_resolve_candidate_path "$candidate")"; then
        echo "uv candidate is not executable: ${label} (${candidate})" >&2
        return 1
    fi

    if "$resolved" --version >/dev/null 2>&1; then
        printf '%s\n' "$resolved"
        return 0
    fi

    echo "uv candidate failed validation: ${label} (${resolved})" >&2
    return 1
}

resolve_uv() {
    local home_dir="${HOME:-}"
    local candidate=""
    local resolved=""
    local searched=(
        "UV_BIN"
        "PATH"
        "\$HOME/.local/bin/uv"
        "\$HOME/.cargo/bin/uv"
        "/usr/local/bin/uv"
    )

    if [[ -n "${UV_BIN:-}" ]]; then
        _uv_validate_candidate "$UV_BIN" "UV_BIN" || {
            echo "UV_BIN is set but is not a usable uv executable" >&2
            return 1
        }
        return 0
    fi

    if resolved="$(command -v uv 2>/dev/null)"; then
        if _uv_validate_candidate "$resolved" "PATH uv"; then
            return 0
        fi
    fi

    local candidates=()
    if [[ -n "$home_dir" ]]; then
        candidates+=("$home_dir/.local/bin/uv" "$home_dir/.cargo/bin/uv")
    fi
    candidates+=("/usr/local/bin/uv")

    for candidate in "${candidates[@]}"; do
        if [[ -e "$candidate" ]] && _uv_validate_candidate "$candidate" "common path"; then
            return 0
        fi
    done

    echo "uv is required to validate skill frontmatter" >&2
    echo "Looked in: ${searched[*]}" >&2
    if [[ -z "$home_dir" ]]; then
        echo "HOME-derived paths were skipped because HOME is empty or unset." >&2
    fi
    echo "Install uv or set UV_BIN=/path/to/uv." >&2
    return 1
}
