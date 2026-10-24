#!/bin/sh
# Static-only pre-push adapter; BUILD_COMMANDS.md revision 1, Hook usage.
set -eu
for argument do
    case "$argument" in
        --run|--run=*|--suggest|--suggest=*|--normalise|--normalise=*)
            echo 'CONFIG_ERROR: hook wrapper supports static checks only' >&2
            exit 2
            ;;
    esac
done
script_dir=$(CDPATH='' cd -P "$(dirname "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    interpreter=python3
elif command -v python >/dev/null 2>&1; then
    interpreter=python
else
    echo 'CONFIG_ERROR: Python is required' >&2
    exit 2
fi
exec "$interpreter" -I "$script_dir/check_build_commands.py" "$@"
