#!/usr/bin/env bash
# python-resolver.sh — portable Python resolver
# Source this file to get a working Python 3 command.
#
# New callers use the PYTHON_CMD Bash array so multi-word launchers such as
# `uv run --no-project python` remain safely quoted.  PYTHON is retained as a
# direct-interpreter compatibility variable for older callers.
#
# Validates each candidate to reject Windows Store shims (which report
# availability via `command -v` but exit non-zero when actually invoked).

_py_find_direct() {
    local candidate
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c 'import sys; assert sys.version_info[0] >= 3' >/dev/null 2>&1; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_CMD=()
if command -v uv >/dev/null 2>&1 &&
        uv run --no-project python -c 'import sys; assert sys.version_info[0] >= 3' >/dev/null 2>&1; then
    PYTHON_CMD=(uv run --no-project python)
    _python_via_uv() { uv run --no-project python "$@"; }
    PYTHON=_python_via_uv
else
    PYTHON=$(_py_find_direct) || {
        echo "error: no working Python 3 found (tried uv, python3, python)" >&2
        return 1 2>/dev/null || exit 1
    }
    PYTHON_CMD=("$PYTHON")
fi

# Preserve the scalar API for every successful resolution. In uv-only
# environments it names the shell wrapper above; array-aware callers should
# still use "${PYTHON_CMD[@]}".
export PYTHON
unset -f _py_find_direct
