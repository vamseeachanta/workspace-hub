#!/usr/bin/env bash
# workstation-lib.sh — Shared helpers for querying the workstation registry.
# Source this from any script that needs hostname→identity resolution.
#
# Usage:
#   source "$(git rev-parse --show-toplevel)/scripts/lib/workstation-lib.sh"
#   ws_variant       # prints schedule_variant for this host (e.g. "full")
#   ws_is "full"     # returns 0 if this host's variant matches, 1 otherwise
#   ws_role          # prints role (e.g. "primary-dev")
#   ws_field <field> # prints any top-level field from the registry for this host

_WS_REGISTRY="${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null)}/config/workstations/registry.yaml"
_WS_HOSTNAME=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
_WS_HOSTNAME=$(printf '%s' "$_WS_HOSTNAME" | tr '[:upper:]' '[:lower:]')

_ws_query() {
  local field="$1"
  uv run --no-project python -c "
import sys
from pathlib import Path

workspace_hub = Path('${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null)}')
sys.path.insert(0, str(workspace_hub / 'src'))
from workspace_hub.workstations.resolver import WorkstationPathResolver

resolver = WorkstationPathResolver.from_registry_path(Path('${_WS_REGISTRY}'))
value = resolver.field_for('${_WS_HOSTNAME}', '${field}')
if value is not None:
    print(value)
" 2>/dev/null
}

ws_variant() { _ws_query "schedule_variant"; }
ws_role()    { _ws_query "role"; }
ws_field()   { _ws_query "$1"; }

ws_is() {
  local expected="$1"
  local actual
  actual=$(ws_variant)
  [[ "$actual" == "$expected" ]]
}

# Export machine list for Python consumers
ws_valid_machines() {
  uv run --no-project python -c "
import sys
from pathlib import Path

workspace_hub = Path('${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null)}')
sys.path.insert(0, str(workspace_hub / 'src'))
from workspace_hub.workstations.resolver import WorkstationPathResolver

resolver = WorkstationPathResolver.from_registry_path(Path('${_WS_REGISTRY}'))
for machine in resolver.valid_machine_identifiers():
    print(machine)
" 2>/dev/null
}
