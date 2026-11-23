#!/usr/bin/env bash
# Non-login Git Bash entry point for the native Windows doctor wrapper.
# USERPROFILE is authoritative here; an inherited HOME may name another profile.
set -euo pipefail

: "${USERPROFILE:?USERPROFILE must identify the scheduled task user}"
command -v cygpath >/dev/null || { echo 'Git Bash cygpath is required' >&2; exit 1; }
profile="$(cygpath -u "${USERPROFILE}")"
[[ "${profile}" == /* && -d "${profile}" ]] || {
    echo 'The scheduled task user profile is unavailable' >&2
    exit 1
}
export HOME
HOME="$(cd "${profile}" && pwd -P)"
export PATH="${HOME}/.local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
export WORKSPACE_HUB
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd -P)"
cd "${WORKSPACE_HUB}"
exec bash "${WORKSPACE_HUB}/scripts/maintenance/harness-install-doctor.sh"
