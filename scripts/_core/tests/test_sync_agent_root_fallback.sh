#!/usr/bin/env bash
# Regression contract: issue #2210, repo-local fallback with no identity match.
# Isolation follows test_sync_agent_helpers.sh: copied source and temporary roots.
# Only helper definitions are loaded; synchronization and live settings are unused.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SOURCE_SCRIPT="$REPO_ROOT/scripts/_core/sync-agent-configs.sh"
# Assertion accounting starts empty and adds one per reported check.
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

run_fallback_case() (
    set -euo pipefail
    case_dir="$1"
    harness_state="$2"
    checkout_name="$3"
    ws_root="$case_dir/$checkout_name"
    source_copy="$ws_root/scripts/_core/sync-agent-configs.sh"
    template="$ws_root/config/agents/hermes/config.yaml.template"
    registry="$ws_root/config/workstations/registry.yaml"
    harness="$ws_root/scripts/readiness/harness-config.yaml"
    output="$case_dir/rendered.yaml"

    mkdir -p "$(dirname "$source_copy")" "$(dirname "$template")" \
        "$(dirname "$registry")" "$(dirname "$harness")" "$case_dir/python-stubs"
    cp "$SOURCE_SCRIPT" "$source_copy"
    cp "$source_copy" "$case_dir/source.before"

    # The registered root deliberately differs from the checkout. The expected
    # fallback below comes from this fixture layout, not from resolver output.
    cat > "$registry" <<EOF
machines:
  registered-fixture:
    hostname_aliases: []
    repo_layout: sibling
    workspace_root: "$case_dir/registered-root"
    tier1_repo_root: "$case_dir"
    repos: []
EOF
    cp "$registry" "$case_dir/registry.before"
    if [[ "$harness_state" == unmatched-identity ]]; then
        cat > "$harness" <<EOF
workstations:
  registered-fixture:
    ws_hub_path: "$case_dir/registered-root"
EOF
        cp "$harness" "$case_dir/harness.before"
    fi
    cat > "$template" <<'EOF'
skills:
  external_dirs:
    - "__WS_HUB_PATH__/.claude/skills"
    - "__TIER1_REPO_ROOT__/sibling/.claude/skills"
EOF
    cp "$template" "$case_dir/template.before"

    # sitecustomize affects the embedded Python without rewriting helper code.
    # No host identity is queried; no real identity file can be selected.
    cat > "$case_dir/python-stubs/sitecustomize.py" <<'PY'
import socket

socket.gethostname = lambda: "unknown-fixture"
PY
    export PYTHONPATH="$case_dir/python-stubs"
    export PYTHONDONTWRITEBYTECODE=1
    # The real Python launcher may use uv; dependency setup belongs to the
    # caller, and these fixture runs must never fetch from the network.
    export UV_OFFLINE=1
    export WORKSPACE_HUB_MACHINE_IDENTITY="$case_dir/absent-identity.yaml"
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR

    # Keep the actual definitions byte-for-byte, stopping before the script's
    # first top-level validation/write. Missing boundaries must fail closed.
    python3 - "$source_copy" "$case_dir/helpers.sh" <<'PY'
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text()
_, start, definitions = source.partition("\nlog_change() {")
definitions, end, _ = definitions.partition(
    "\n# Reject a pinned template before any configuration target can be written."
)
if not start or not end:
    raise SystemExit("helper isolation boundary missing")
pathlib.Path(sys.argv[2]).write_text(start + definitions)
PY
    # shellcheck source=/dev/null
    source "$case_dir/helpers.sh"
    export WS_HUB="$ws_root"
    export MACHINE=""

    roots="$(resolve_machine_roots 2>"$case_dir/resolver.stderr")"
    # The tab-delimited interface is documented at resolve_machine_roots; read
    # its named fields rather than depending on warning text or field indices.
    IFS=$'\t' read -r resolved_name resolved_root resolved_parent <<< "$roots"
    [[ "$resolved_name" == local-fallback-unknown-fixture ]]
    [[ "$resolved_root" == "$ws_root" ]]
    [[ "$resolved_parent" == "$case_dir" ]]
    [[ "$(resolve_ws_hub_path 2>"$case_dir/ws-root.stderr")" == "$ws_root" ]]

    render_hermes_template "$template" "$output" \
        "$resolved_name" "$resolved_root" "$resolved_parent"
    python3 - "$output" "$ws_root" "$case_dir" <<'PY'
import pathlib
import sys

import yaml

output, checkout, parent = map(pathlib.Path, sys.argv[1:])
data = yaml.safe_load(output.read_text())
# Independent expectation: append the fixture template's literal skill suffixes
# to the checkout and its known parent, without using any resolved value.
expected = [str(checkout / ".claude" / "skills"),
            str(parent / "sibling" / ".claude" / "skills")]
assert data["skills"]["external_dirs"] == expected, "incorrect rendered destinations"
PY

    cmp -s "$case_dir/source.before" "$source_copy"
    cmp -s "$case_dir/source.before" "$SOURCE_SCRIPT"
    cmp -s "$case_dir/template.before" "$template"
    cmp -s "$case_dir/registry.before" "$registry"
    if [[ "$harness_state" == unmatched-identity ]]; then
        cmp -s "$case_dir/harness.before" "$harness"
    else
        [[ ! -e "$harness" ]]
    fi
    [[ ! -e "$WORKSPACE_HUB_MACHINE_IDENTITY" ]]
)

if [[ "${1:-}" == --case ]]; then
    run_fallback_case "$2" "$3" "$4"
    exit
fi

echo "=== test_sync_agent_root_fallback.sh ==="
# Temporary fixtures are retained for caller-managed inspection and cleanup.
scratch="$(mktemp -d)"
for harness_state in missing-harness unmatched-identity; do
    for checkout_name in checkout 'checkout with spaces'; do
        label="$harness_state / $checkout_name"
        # Run as a standalone shell so errexit remains active for every check.
        # Calling the function in an if condition would suppress its failures.
        if bash "${BASH_SOURCE[0]}" --case \
            "$scratch/$harness_state/$checkout_name" \
            "$harness_state" "$checkout_name"; then
            pass "$label: roots, parsed YAML and unchanged input bytes"
        else
            fail "$label: roots, parsed YAML and unchanged input bytes"
        fi
    done
done

echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ "$FAIL" -eq 0 ]]
