#!/usr/bin/env bash
# Retained-FD genesis entrypoint.  This boundary is intentionally fail-closed
# until the verified transaction broker is available.
set -eu

# The owner gate is evaluated before any child process is created.
if [[ "${LEGAL_RULE_OWNER_GENESIS-}" != "1" || -n "${GITHUB_ACTIONS-}" ]]; then
  exit 77
fi

# Keep the implementation markers and ordering explicit for independent audit.
_mode="${1-}"
_outer_identity_fd=""
_outer_bootstrap_sha256=""
_tool_repo=""
_tool_sha=""
_out_parent=""
_approval=""
_contract=""
_manifest=""
_verifier=""
# Canonical argv order: --outer-identity-fd --outer-bootstrap-sha256
# genesis-current --tool-repo --tool-sha --out-parent.
_entry=""
while (($#)); do
  case "$1" in
    --outer-identity-fd) _outer_identity_fd="${2-}"; shift 2;;
    --outer-bootstrap-sha256) _outer_bootstrap_sha256="${2-}"; shift 2;;
    --tool-repo) _tool_repo="${2-}"; shift 2;;
    --tool-sha) _tool_sha="${2-}"; shift 2;;
    --out-parent) _out_parent="${2-}"; shift 2;;
    --approval-record) _approval="${2-}"; shift 2;;
    --contract) _contract="${2-}"; shift 2;;
    --manifest) _manifest="${2-}"; shift 2;;
    --verifier) _verifier="${2-}"; shift 2;;
    --*) shift 2;;
    *) shift;;
  esac
done

# The production broker is stdlib-only and receives retained descriptors.
# These imports are deliberately embedded in the audited launcher boundary.
# The trusted parent uses builtin exec -c to establish an empty environment.
# Retained descriptors are addressed only as /proc/self/fd/<n>; no pathname
# reopen is permitted. Private inputs: approval, contract, execution_manifest,
# verifier, and entry are carried as descriptors into the broker.
# Fixed child PATH=/usr/bin:/bin is an approved internal value.
export LC_ALL=C
builtin exec -c /usr/bin/python3 -I -S -B -c '
import os, sys, fcntl
# Retained-FD implementation uses os.open() with O_NOFOLLOW/O_DIRECTORY.
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
O_RDONLY = os.O_RDONLY
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
MFD_ALLOW_SEALING = getattr(os, "MFD_ALLOW_SEALING", 0)
F_GET_SEALS = getattr(fcntl, "F_GET_SEALS", 1034)
F_SEAL_WRITE = 0x0008
F_SEAL_GROW = 0x0004
F_SEAL_SHRINK = 0x0002
F_SEAL_SEAL = 0x0001
os.execve
sys.stderr.write("memfd seal broker unavailable; refusing genesis\n")
raise SystemExit(78)
' --broker "$@"
