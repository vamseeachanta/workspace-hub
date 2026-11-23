#!/usr/bin/env bash
# code-version-guard.sh — Design code edition check for session start
# Reads data/design-codes/code-registry.yaml and warns when a code's registered
# edition differs from the latest known edition (status: check | superseded).
# Always exits 0 — informational only; never blocking.
# WRK-176
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}}"
REGISTRY="${WORKSPACE}/data/design-codes/code-registry.yaml"

# ─────────────────────────────────────────────────────────────────────────────
# Dependency check
# ─────────────────────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "code-version-guard: python3 not found — skipping design code check" >&2
    exit 0
fi

if [[ ! -f "$REGISTRY" ]]; then
    echo "code-version-guard: registry not found at ${REGISTRY} — skipping" >&2
    exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# Parse registry and emit warnings via Python (avoids yq/pyyaml dep)
# ─────────────────────────────────────────────────────────────────────────────
python3 - "$REGISTRY" <<'PYEOF'
import sys
import re

registry_path = sys.argv[1]

# Minimal YAML block parser — handles the registry structure without pyyaml.
# Parses top-level "codes:" list; each entry is a mapping of scalar fields.
def parse_registry(path):
    codes = []
    current = None
    in_codes = False

    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.lstrip()

        # Skip comments and blank lines
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(stripped)

        if stripped == "codes:":
            in_codes = True
            continue

        if not in_codes:
            continue

        # New list item — start of a code entry
        if indent == 2 and stripped.startswith("- "):
            if current is not None:
                codes.append(current)
            current = {}
            # Handle inline "- key: value" on the same line
            rest = stripped[2:]
            if ":" in rest:
                key, _, val = rest.partition(":")
                current[key.strip()] = val.strip().strip('"').strip("'")
            continue

        # Key-value pair inside a list item
        if indent == 4 and current is not None and ":" in stripped:
            key, _, val = stripped.partition(":")
            val = val.strip()
            # Skip block scalar indicators and list values
            if val and val[0] in ("|", ">", "["):
                continue
            current[key.strip()] = val.strip().strip('"').strip("'")
            continue

    if current is not None:
        codes.append(current)

    return codes


def summarise(codes):
    checks = []
    superseded = []
    current_count = 0
    missing_fields = []

    for entry in codes:
        code_id = entry.get("id", "<unknown>")
        status = entry.get("status", "")
        our_ed = entry.get("our_edition", "")
        latest_ed = entry.get("latest_known_edition", "")
        notes = entry.get("notes", "")
        title = entry.get("title", "")

        required = ["id", "our_edition", "latest_known_edition", "status"]
        for field in required:
            if field not in entry:
                missing_fields.append(f"{code_id}: missing field '{field}'")

        if status == "current":
            current_count += 1
        elif status == "check":
            checks.append((code_id, title, our_ed, latest_ed, notes))
        elif status == "superseded":
            superseded.append((code_id, title, our_ed, latest_ed, notes))

    return current_count, checks, superseded, missing_fields


codes = parse_registry(registry_path)
current_count, checks, superseded, missing_fields = summarise(codes)

total = len(codes)
issue_count = len(checks) + len(superseded)

header = f"Design Code Registry: {total} codes — {current_count} current"
if issue_count:
    header += f", {issue_count} requiring attention"

print(header)

if superseded:
    print()
    print("  SUPERSEDED — update required before use in calculations:")
    for cid, title, our_ed, latest_ed, notes in superseded:
        print(f"    ! {cid} (our: {our_ed} → latest: {latest_ed})")
        if title:
            print(f"      {title}")
        if notes:
            print(f"      Note: {notes}")

if checks:
    print()
    print("  CHECK — newer edition available; verify applicability:")
    for cid, title, our_ed, latest_ed, notes in checks:
        print(f"    ? {cid} (our: {our_ed} → latest: {latest_ed})")
        if title:
            print(f"      {title}")
        if notes:
            print(f"      Note: {notes}")

if missing_fields:
    print()
    print("  REGISTRY ERRORS — fix data/design-codes/code-registry.yaml:")
    for msg in missing_fields:
        print(f"    * {msg}")

if not issue_count and not missing_fields:
    print("  All design codes current.")

sys.exit(0)
PYEOF

exit 0
