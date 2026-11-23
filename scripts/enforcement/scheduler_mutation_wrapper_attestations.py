"""Fail-closed source-shape attestations for scheduler wrapper modes."""
from __future__ import annotations

import hashlib

SETUP = b"scripts/cron/setup-cron.sh"
NEW_MACHINE = b"scripts/setup/new-machine-setup.sh"
HARNESS = b"scripts/cron/harness-update.sh"

SETUP_ATTESTATIONS = {
    "setup-default-apply-v1",
    "setup-dry-run-v1",
    "setup-live-reload-v1",
    "setup-remote-reject-v1",
    "setup-windows-skip-v1",
}
NEW_MACHINE_ATTESTATIONS = {
    "new-machine-default-v1",
    "new-machine-dry-run-v1",
    "new-machine-windows-v1",
}
HARNESS_ATTESTATIONS = {"harness-default-v1", "harness-dry-run-v1"}
WRAPPER_SHA256 = {
    SETUP: "1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1",
    NEW_MACHINE: "5120de77dcec9349fc2b24f5d6889d53c88f357efcf4ca4874479471a9a53d5c",
    HARNESS: "be6d0b2fa0771002423e0a698a03b2c37b9471bc9f07f2c8cb0cf215d9730607",
}
SETUP_PROTECTED_PREFIX = b'''#!/usr/bin/env bash
# setup-cron.sh \xe2\x80\x94 compatibility entrypoint for transactional cron reconciliation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
CRON_RENDER="${WORKSPACE_HUB}/scripts/cron/cron_render.py"
CRON_APPLY="${WORKSPACE_HUB}/scripts/cron/cron_''' b'''apply.py"
export UV_CACHE_DIR="${UV_CACHE_DIR:-${WORKSPACE_HUB}/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"

DRY_RUN=false
REPLACE=false
ALLOW_LIVE_RELOAD=false
TARGET_MACHINE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --replace) REPLACE=true; shift ;;
    --allow-live-reload) ALLOW_LIVE_RELOAD=true; shift ;;
    --machine)
      [[ $# -ge 2 ]] || { echo "ERROR: --machine requires a value" >&2; exit 2; }
      TARGET_MACHINE="$2"
      shift 2
      ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ "$REPLACE" == true ]]; then
  echo "ERROR: 'setup-cron.sh --replace' is disabled (#2969)" >&2
  echo "Use transactional preview/apply through setup-cron.sh instead." >&2
  exit 2
fi

if [[ -z "$TARGET_MACHINE" ]]; then
  TARGET_MACHINE="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"
fi
PHYSICAL_HOST="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"''' + b"\n\n"
SETUP_PROTECTED_SUFFIX = b'''CANONICAL_MACHINE="$(uv run --no-project python "$CRON_RENDER" \\
  --machine "$TARGET_MACHINE" --field machine_id)"
PHYSICAL_MACHINE="$(uv run --no-project python "$CRON_RENDER" \\
  --machine "$PHYSICAL_HOST" --field machine_id)"
SCHEDULE_VARIANT="$(uv run --no-project python "$CRON_RENDER" \\
  --machine "$TARGET_MACHINE" --field schedule_variant)"

echo "Host: ${TARGET_MACHINE} \xe2\x86\x92 machine: ${CANONICAL_MACHINE} \xe2\x86\x92 cron_variant: ${SCHEDULE_VARIANT}"
# #3507: key the Task-Scheduler skip on the registry os field, NOT the schedule
# variant \xe2\x80\x94 gpu-claw is a linux contribute-minimal box and must get real crons.
MACHINE_OS="$(uv run --no-project python "$CRON_RENDER" \\
  --machine "$TARGET_MACHINE" --field os)"
if [[ "$MACHINE_OS" == "windows" ]]; then
  echo "This machine uses Windows Task Scheduler; Linux cron reconciliation is skipped."
  exit 0
fi
if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]; then
  echo "ERROR: refusing to reconcile local crontab for remote machine ${CANONICAL_MACHINE}" >&2
  echo "Run setup-cron.sh on that machine instead." >&2
  exit 2
fi

APPLY_ARGS=(--machine "$CANONICAL_MACHINE")
if [[ "$DRY_RUN" == false ]]; then
  APPLY_ARGS+=(--apply)
else
  APPLY_ARGS+=(--json)
fi
if [[ "$ALLOW_LIVE_RELOAD" == true ]]; then
  APPLY_ARGS+=(--allow-live-reload)
fi

exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"'''


def evaluate_wrapper_attestation(name: str, records: dict[bytes, bytes]) -> bool | None:
    reason = wrapper_attestation_reason(name, records)
    return None if reason is None else reason == "accepted"


def wrapper_attestation_reason(name: str, records: dict[bytes, bytes]) -> str | None:
    """Report provenance before semantics without changing the boolean contract."""
    if name in SETUP_ATTESTATIONS:
        source, terminal, shape = SETUP, b'exec uv run --script "$CRON_APPLY"', _setup_shape
    elif name in NEW_MACHINE_ATTESTATIONS:
        source = NEW_MACHINE
        terminal = b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"'
        shape = _new_machine_shape
    elif name in HARNESS_ATTESTATIONS:
        source, terminal, shape = HARNESS, b"\nsync_crontab\n", _harness_shape
    else:
        return None
    if not WRAPPER_SHA256.get(source):
        return "missing-pin"
    if source not in records:
        return "missing-source"
    if not _pinned(source, records):
        return "stale-pin"
    body = records[source]
    if not _reachable_script(body, terminal):
        return "unreachable"
    return "accepted" if shape(body) else "source-shape"


def _pinned(source: bytes, records: dict[bytes, bytes]) -> bool:
    # Pins are a staged-blob drift alarm, not an authorization anchor. The
    # reachable source contract below must pass independently, so refreshing a
    # neighboring hash cannot authorize an early-exit or dead-scope wrapper.
    expected = WRAPPER_SHA256.get(source)
    body = records.get(source)
    return bool(expected and body is not None and hashlib.sha256(body).hexdigest() == expected)


def _reachable_script(body: bytes, terminal: bytes) -> bool:
    first = next((line.strip() for line in body.splitlines()
                  if line.strip() and not line.lstrip().startswith(b"#")), b"")
    terminal_at = body.find(terminal)
    offset, early_exit = 0, None
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if line == line.lstrip() and stripped.startswith((b"exit", b"return")):
            early_exit = offset
            break
        offset += len(line)
    return (first.startswith(b"set -") and first not in {b"set +e", b"set +u"}
            and terminal_at >= 0 and (early_exit is None or early_exit > terminal_at))


def _setup_shape(body: bytes) -> bool:
    protected_body = SETUP_PROTECTED_PREFIX + SETUP_PROTECTED_SUFFIX + b"\n"
    return body == protected_body


def _new_machine_shape(body: bytes) -> bool:
    block = b'''if [[ "$NO_CRON" == "true" ]]; then
  log "Skipped (--no-cron flag)."
elif [[ "$DRY_RUN" == "true" ]]; then
  dry "bash scripts/cron/setup-cron.sh --dry-run"
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" --dry-run || true
elif [[ "$WH_OS" == "windows" ]]; then
  log "Windows detected \xe2\x80\x94 printing Task Scheduler instructions:"
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" || true
else
  bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"
fi'''
    return block in body and body.count(b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"') == 3


def _harness_shape(body: bytes) -> bool:
    block = b'''sync_crontab() {
  local installer="${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"
  [[ -f "$installer" ]] || { log "CRON" "setup-cron.sh absent \xe2\x80\x94 skip"; return; }
  local out status
  if [[ "$DRY_RUN" == "true" ]]; then
    if out=$(bash "$installer" --dry-run 2>&1); then
      status=0
    else
      status=$?
    fi
    # Preserve the nonfatal contract, but report failures before counting output.
    if [[ "$status" -ne 0 ]]; then
      log "CRON" "dry-run failed (exit ${status}); inspect setup-cron.sh diagnostics: ${out}"
      return 0
    fi
    local n
    n=$(printf '%s\\n' "$out" | grep -cE '^[[:space:]]+[0-9*]' || true)
    log "CRON" "dry-run: ${n} schedule-tasks.yaml entry/entries would be ensured"
    return
  fi
  if out=$(bash "$installer" 2>&1); then
    status=0
  else
    status=$?
  fi
  if [[ "$status" -ne 0 ]]; then
    log "CRON" "apply failed (exit ${status}); inspect setup-cron.sh diagnostics: ${out}"
    return 0
  fi
  log "CRON" "$(printf '%s\\n' "$out" | grep -iE 'Installed|Replaced|already present' | tail -1)"
}'''
    return block in body and body.count(b"sync_crontab\n") == 1


def _ordered(body: bytes, tokens: list[bytes]) -> bool:
    position = -1
    for token in tokens:
        found = body.find(token, position + 1)
        if found < 0:
            return False
        position = found
    return True
