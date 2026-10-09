---
name: bash-cli-framework-5-error-handling
description: 'Sub-skill of bash-cli-framework: 5. Error Handling (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Error Handling (+1)

## 5. Error Handling


Robust error handling with cleanup:

```bash
#!/bin/bash
# ABOUTME: Error handling and cleanup functions
# ABOUTME: Ensures graceful exit and resource cleanup

# Trap for cleanup on exit
cleanup() {
    local exit_code=$?

    # Remove temporary files
    [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]] && rm -rf "$TEMP_DIR"

    # Log exit status
    if [[ $exit_code -eq 0 ]]; then
        log_info "Script completed successfully"
    else
        log_error "Script exited with code $exit_code"
    fi

    exit $exit_code
}

# Set trap
trap cleanup EXIT INT TERM

# Error handler
die() {
    local message="$1"
    local exit_code="${2:-1}"

    log_critical "$message"
    exit "$exit_code"
}

# Assert function
assert() {
    local condition="$1"
    local message="${2:-Assertion failed}"

    if ! eval "$condition"; then
        die "$message"
    fi
}
```


## 6. Argument Parsing


Standard argument parsing pattern:

```bash
#!/bin/bash
# ABOUTME: Argument parsing framework
# ABOUTME: Supports short/long options with values

# Default values
VERBOSE=false
DRY_RUN=false
CONFIG_FILE=""

show_usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <arguments>

Options:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -n, --dry-run       Show what would be done without doing it
    -c, --config FILE   Use specified configuration file
    --version           Show version information

Examples:
    $SCRIPT_NAME --verbose process
    $SCRIPT_NAME -c config.yaml --dry-run

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --version)
                echo "$SCRIPT_NAME version $VERSION"
                exit 0
                ;;
            --)
                shift
                break
                ;;
            -*)
                die "Unknown option: $1"
                ;;
            *)
                break
                ;;
        esac
    done

    # Remaining arguments
    ARGS=("$@")
}
```
