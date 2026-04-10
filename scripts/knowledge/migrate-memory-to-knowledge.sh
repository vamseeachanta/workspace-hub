#!/usr/bin/env bash
# migrate-memory-to-knowledge.sh — Move WRK ARCHIVED bullets from MEMORY.md to knowledge-base/
# Usage: migrate-memory-to-knowledge.sh <MEMORY.md path> [--dry-run]
# MEMORY.md WRK entries are single-line bullets:
#   - **WRK-NNN ARCHIVED** (hash): title/summary...
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
MEMORY_FILE="${1:-}"
DRY_RUN=false
KNOWLEDGE_BASE_DIR="${KNOWLEDGE_BASE_DIR:-${REPO_ROOT}/knowledge-base}"
JSONL_FILE="${KNOWLEDGE_BASE_DIR}/wrk-completions.jsonl"
LOCK_FILE="${JSONL_FILE}.lock"

if [[ -z "${MEMORY_FILE}" ]]; then
    echo "Usage: migrate-memory-to-knowledge.sh <MEMORY.md path> [--dry-run]" >&2
    exit 1
fi

shift
for arg in "$@"; do
    if [[ "${arg}" == "--dry-run" ]]; then
        DRY_RUN=true
    fi
done

if [[ ! -f "${MEMORY_FILE}" ]]; then
    echo "[migrate] MEMORY.md not found: ${MEMORY_FILE}" >&2
    exit 0
fi

uv run --no-project python - <<PYEOF
import re, json, os, sys, shutil

memory_file = "${MEMORY_FILE}"
kb_dir = "${KNOWLEDGE_BASE_DIR}"
jsonl_file = "${JSONL_FILE}"
lock_file = "${LOCK_FILE}"
dry_run = "${DRY_RUN}" == "true"

ARCHIVED_PATTERN = re.compile(r'^\s*-\s+\*\*WRK-(\d+)\s+ARCHIVED\*\*')

with open(memory_file) as f:
    lines = f.readlines()

to_migrate = []
keep_lines = []

for line in lines:
    m = ARCHIVED_PATTERN.match(line)
    if m:
        wrk_id = "WRK-" + m.group(1)
        to_migrate.append({"id": wrk_id, "raw": line.rstrip()})
    else:
        keep_lines.append(line)

if dry_run:
    print(f"Would migrate {len(to_migrate)} WRK ARCHIVED lines from MEMORY.md")
    print(f"MEMORY.md would shrink from {len(lines)} → {len(keep_lines)} lines")
    for entry in to_migrate[:3]:
        print(f"  Preview: {entry['raw'][:100]}")
    sys.exit(0)

if not to_migrate:
    print("[migrate] No WRK ARCHIVED lines found in MEMORY.md — nothing to do")
    sys.exit(0)

# Backup before writing
shutil.copy2(memory_file, memory_file + ".bak")

# Load existing IDs from knowledge-base (for idempotency)
os.makedirs(kb_dir, exist_ok=True)
existing_ids = set()
if os.path.exists(jsonl_file):
    with open(jsonl_file) as f:
        for line in f:
            try:
                existing_ids.add(json.loads(line.strip()).get("id", ""))
            except json.JSONDecodeError:
                pass

# Append new entries
new_entries = []
for entry in to_migrate:
    if entry["id"] in existing_ids:
        print(f"[migrate] Skipping {entry['id']} — already in knowledge-base", file=sys.stderr)
    else:
        new_entries.append({
            "id": entry["id"],
            "type": "wrk",
            "source": "memory-migration",
            "raw": entry["raw"],
        })
        existing_ids.add(entry["id"])

if new_entries:
    with open(jsonl_file, "a") as f:
        for e in new_entries:
            f.write(json.dumps(e) + "\n")

# Atomic write of kept lines
tmp_file = memory_file + ".tmp"
with open(tmp_file, "w") as f:
    f.writelines(keep_lines)
os.replace(tmp_file, memory_file)

print(f"[migrate] Migrated {len(new_entries)} new entries. "
      f"MEMORY.md now {len(keep_lines)} lines (was {len(lines)}).")
PYEOF

exit 0
