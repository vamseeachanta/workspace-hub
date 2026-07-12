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
        body = records.get(SETUP, b"")
        if not _pinned(SETUP, records) or not _reachable_script(
            body, b'exec uv run --script "$CRON_APPLY"'
        ):
            return False
        return _setup_shape(body)
    if name in NEW_MACHINE_ATTESTATIONS:
        body = records.get(NEW_MACHINE, b"")
        if not _pinned(NEW_MACHINE, records) or not _reachable_script(
            body, b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"'
        ):
            return False
        return _new_machine_shape(body)
    if name in HARNESS_ATTESTATIONS:
        body = records.get(HARNESS, b"")
        if not _pinned(HARNESS, records) or not _reachable_script(
            body, b"\nsync_crontab\n"
        ):
            return False
        return _harness_shape(body)
    return None


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
    terminal = b'\nexec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"\n'
    return (_ordered(body, required) and body.count(terminal) == 1
            and body.rstrip().endswith(terminal.strip()))


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
