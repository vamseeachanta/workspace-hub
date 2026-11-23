#!/usr/bin/env bash
# ABOUTME: Shared helper for robust Gemini CLI invocation with retry/fallback.
# ABOUTME: Handles exit-0-on-error, stderr capture, empty output detection, and model fallback.
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/../lib/gemini-invoke.sh"
#   gemini_invoke --prompt "Review this code" --stdin-file /tmp/context.md --out /tmp/result.md
#
# The function writes model output to --out (stdout only) and returns:
#   0  valid output (non-empty, no capacity errors)
#   1  empty output or capacity exhausted (NO_OUTPUT written to --out)
#   2  gemini CLI not found
#   3  prompt error or bad arguments

# Fallback model when primary is capacity-exhausted
GEMINI_FALLBACK_MODEL="${GEMINI_FALLBACK_MODEL:-gemini-2.5-flash}"
GEMINI_MAX_RETRIES="${GEMINI_MAX_RETRIES:-1}"
GEMINI_INVOKE_TIMEOUT="${GEMINI_INVOKE_TIMEOUT:-120}"

# gemini_invoke [options]
#   --prompt TEXT         The -p prompt instruction (required)
#   --stdin-file FILE     File to pipe as stdin context (optional)
#   --stdin-text TEXT     Text to pipe as stdin context (optional)
#   --out FILE            Output file path (required)
#   --err FILE            Stderr capture file (optional, uses temp if not set)
#   --yolo                Pass -y flag to gemini
#   --timeout SECONDS     Override timeout (default: $GEMINI_INVOKE_TIMEOUT)
#   --model MODEL         Override model (default: use gemini's configured model)
gemini_invoke() {
    local prompt="" stdin_file="" stdin_text="" out_file="" err_file=""
    local use_yolo=false timeout_secs="$GEMINI_INVOKE_TIMEOUT" model=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prompt)    prompt="$2";     shift 2 ;;
            --stdin-file) stdin_file="$2"; shift 2 ;;
            --stdin-text) stdin_text="$2"; shift 2 ;;
            --out)       out_file="$2";   shift 2 ;;
            --err)       err_file="$2";   shift 2 ;;
            --yolo)      use_yolo=true;   shift ;;
            --timeout)   timeout_secs="$2"; shift 2 ;;
            --model)     model="$2";      shift 2 ;;
            *) echo "gemini_invoke: unknown option: $1" >&2; return 3 ;;
        esac
    done

    [[ -z "$prompt" ]]   && { echo "gemini_invoke: --prompt required" >&2; return 3; }
    [[ -z "$out_file" ]] && { echo "gemini_invoke: --out required" >&2; return 3; }

    command -v gemini >/dev/null 2>&1 || {
        echo "NO_OUTPUT: gemini CLI not found" > "$out_file"
        return 2
    }

    # Set up stderr capture
    local _own_err=false
    if [[ -z "$err_file" ]]; then
        err_file="$(mktemp)"
        _own_err=true
    fi

    # Build gemini args
    local -a gemini_args=(-p "$prompt")
    [[ "$use_yolo" == "true" ]] && gemini_args+=(-y)
    [[ -n "$model" ]] && gemini_args+=(-m "$model")

    # Determine stdin source
    local stdin_source="/dev/null"
    if [[ -n "$stdin_file" ]] && [[ -f "$stdin_file" ]]; then
        stdin_source="$stdin_file"
    fi

    # Portable timeout
    local timeout_cmd=""
    if command -v timeout >/dev/null 2>&1; then
        timeout_cmd="timeout $timeout_secs"
    elif command -v gtimeout >/dev/null 2>&1; then
        timeout_cmd="gtimeout $timeout_secs"
    fi

    # --- Attempt 1: primary model ---
    local exit_code=0
    if [[ -n "$stdin_text" ]]; then
        echo "$stdin_text" | $timeout_cmd gemini "${gemini_args[@]}" > "$out_file" 2>"$err_file" || exit_code=$?
    else
        $timeout_cmd gemini "${gemini_args[@]}" < "$stdin_source" > "$out_file" 2>"$err_file" || exit_code=$?
    fi

    # --- Validate output ---
    if _gemini_output_valid "$out_file" "$err_file"; then
        [[ "$_own_err" == "true" ]] && rm -f "$err_file"
        return 0
    fi

    # --- Detect capacity exhaustion and retry with fallback model ---
    local stderr_content=""
    [[ -f "$err_file" ]] && stderr_content="$(cat "$err_file")"

    if echo "$stderr_content" | grep -qE "RESOURCE_EXHAUSTED|MODEL_CAPACITY_EXHAUSTED|429|No capacity available"; then
        # Capacity exhausted — retry with fallback model if different
        local current_model="${model:-default}"
        if [[ "$current_model" != "$GEMINI_FALLBACK_MODEL" ]]; then
            echo "gemini_invoke: capacity exhausted, retrying with fallback model ${GEMINI_FALLBACK_MODEL}" >&2
            local -a fallback_args=(-p "$prompt" -m "$GEMINI_FALLBACK_MODEL")
            [[ "$use_yolo" == "true" ]] && fallback_args+=(-y)

            exit_code=0
            if [[ -n "$stdin_text" ]]; then
                echo "$stdin_text" | $timeout_cmd gemini "${fallback_args[@]}" > "$out_file" 2>"$err_file" || exit_code=$?
            else
                $timeout_cmd gemini "${fallback_args[@]}" < "$stdin_source" > "$out_file" 2>"$err_file" || exit_code=$?
            fi

            if _gemini_output_valid "$out_file" "$err_file"; then
                [[ "$_own_err" == "true" ]] && rm -f "$err_file"
                return 0
            fi
        fi
    fi

    # --- All attempts failed — write diagnostic NO_OUTPUT ---
    local diag_reason="unknown"
    if echo "$stderr_content" | grep -qE "RESOURCE_EXHAUSTED|MODEL_CAPACITY_EXHAUSTED|429"; then
        diag_reason="MODEL_CAPACITY_EXHAUSTED"
    elif echo "$stderr_content" | grep -qE "YOLO mode"; then
        # YOLO messages present but no model output — likely empty response
        diag_reason="EMPTY_RESPONSE_WITH_YOLO"
    elif [[ $exit_code -eq 124 ]]; then
        diag_reason="TIMEOUT"
    elif [[ ! -s "$out_file" ]]; then
        diag_reason="EMPTY_STDOUT"
    fi

    {
        echo "NO_OUTPUT: gemini invocation failed (${diag_reason})"
        echo "# exit_code: ${exit_code}"
        echo "# stderr (first 5 lines):"
        head -5 "$err_file" 2>/dev/null | sed 's/^/# /'
    } > "$out_file"

    [[ "$_own_err" == "true" ]] && rm -f "$err_file"
    return 1
}

# Internal: check if gemini output is valid (non-empty, no error markers)
_gemini_output_valid() {
    local out_file="$1" err_file="$2"

    # Must exist and be non-empty
    [[ -f "$out_file" ]] || return 1
    local out_size
    out_size=$(wc -c < "$out_file" 2>/dev/null || echo 0)
    [[ $out_size -lt 10 ]] && return 1

    # Check stdout doesn't contain only YOLO/credential noise
    local first_meaningful
    first_meaningful=$(grep -v -E "^(YOLO|Loaded cached|$)" "$out_file" | head -1)
    [[ -z "$first_meaningful" ]] && return 1

    # Check stderr for capacity errors (exit 0 but no real output)
    if [[ -f "$err_file" ]] && [[ -s "$err_file" ]]; then
        if grep -qE "RESOURCE_EXHAUSTED|MODEL_CAPACITY_EXHAUSTED|429|No capacity available" "$err_file"; then
            # Capacity error — even if some stdout, it's likely noise
            # But if stdout has substantial content (>200 bytes), trust it
            [[ $out_size -lt 200 ]] && return 1
        fi
    fi

    return 0
}
