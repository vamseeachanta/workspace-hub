#!/usr/bin/env bash
# python-resolver.sh — portable Python resolver
# Source this file to get $PYTHON set to a working Python 3 interpreter.
#
# Validates each candidate to reject Windows Store shims (which report
# availability via `command -v` but exit non-zero when actually invoked).

_py_find_working() {
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

PYTHON=$(_py_find_working) || {
    echo "error: no working Python 3 found (tried python3, python)" >&2
    exit 1
}
export PYTHON
unset -f _py_find_working
