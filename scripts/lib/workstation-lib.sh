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
import yaml
with open('${_WS_REGISTRY}') as f:
    data = yaml.safe_load(f)
host = '${_WS_HOSTNAME}'
for name, m in data.get('machines', {}).items():
    candidates = [m['hostname']] + m.get('hostname_aliases', [])
    candidates = [c.lower() for c in candidates]
    if host in candidates:
        print(m.get('${field}', ''))
        break
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
import yaml
with open('${_WS_REGISTRY}') as f:
    data = yaml.safe_load(f)
machines = set()
for name, m in data.get('machines', {}).items():
    machines.add(name)
    machines.add(m['hostname'])
    for a in m.get('hostname_aliases', []):
        machines.add(a)
for m in sorted(machines):
    print(m)
" 2>/dev/null
}
