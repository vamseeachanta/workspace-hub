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
    SETUP: "582d12ed794e9b7ad1b809ff99c32dd844178bfd7eed4f85f9de70edd14ec83d",
    NEW_MACHINE: "5120de77dcec9349fc2b24f5d6889d53c88f357efcf4ca4874479471a9a53d5c",
    HARNESS: "a698b7a44194ef92dfbdf9a4d0e5b5550b21ceadb86de2055f634f59b8a1d0c8",
}


def evaluate_wrapper_attestation(name: str, records: dict[bytes, bytes]) -> bool | None:
    if name in SETUP_ATTESTATIONS:
        if not _pinned(SETUP, records):
            return False
        return _setup_shape(records.get(SETUP, b""))
    if name in NEW_MACHINE_ATTESTATIONS:
        if not _pinned(NEW_MACHINE, records):
            return False
        return _new_machine_shape(records.get(NEW_MACHINE, b""))
    if name in HARNESS_ATTESTATIONS:
        if not _pinned(HARNESS, records):
            return False
        return _harness_shape(records.get(HARNESS, b""))
    return None


def _pinned(source: bytes, records: dict[bytes, bytes]) -> bool:
    expected = WRAPPER_SHA256.get(source)
    body = records.get(source)
    return bool(expected and body is not None and hashlib.sha256(body).hexdigest() == expected)


def _setup_shape(body: bytes) -> bool:
    required = [
        b'if [[ "$SCHEDULE_VARIANT" == "contribute-minimal" ]]; then',
        b'exit 0\nfi',
        b'if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]; then',
        b'echo "Run setup-cron.sh on that machine instead." >&2\n  exit 2\nfi',
        b'APPLY_ARGS=(--machine "$CANONICAL_MACHINE")',
        b'if [[ "$DRY_RUN" == false ]]; then\n  APPLY_ARGS+=(--apply)\nelse\n  APPLY_ARGS+=(--json)\nfi',
        b'if [[ "$ALLOW_LIVE_RELOAD" == true ]]; then\n  APPLY_ARGS+=(--allow-live-reload)\nfi',
        b'exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"',
    ]
    return _ordered(body, required) and body.count(b'exec uv run --script "$CRON_APPLY"') == 1


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
  if [[ "$DRY_RUN" == "true" ]]; then
    local n
    n=$(bash "$installer" --dry-run 2>/dev/null | grep -cE '^[[:space:]]+[0-9*]' || true)
    log "CRON" "dry-run: ${n} schedule-tasks.yaml entry/entries would be ensured"
    return
  fi
  local out
  out=$(bash "$installer" 2>&1) || true
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
