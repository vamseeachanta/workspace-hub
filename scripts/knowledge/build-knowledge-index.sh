#!/usr/bin/env bash
# build-knowledge-index.sh — Merge all knowledge stores into index.jsonl
# Usage: build-knowledge-index.sh
# Writes knowledge-base/index.jsonl (atomic write, flock-protected)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KNOWLEDGE_BASE_DIR="${KNOWLEDGE_BASE_DIR:-${REPO_ROOT}/knowledge-base}"
KNOWLEDGE_SEEDS_DIR="${KNOWLEDGE_SEEDS_DIR:-${REPO_ROOT}/knowledge/seeds}"
LOCK_FILE="${KNOWLEDGE_BASE_DIR}/.index.lock"
INDEX_FILE="${KNOWLEDGE_BASE_DIR}/index.jsonl"
INDEX_TMP="${INDEX_FILE}.tmp"

mkdir -p "${KNOWLEDGE_BASE_DIR}"

(
    flock -w 30 200 || { echo "[build-knowledge-index] Lock timeout — skip" >&2; exit 0; }

    uv run --no-project --with pyyaml python - <<PYEOF
import json, os, sys

kb_dir = "${KNOWLEDGE_BASE_DIR}"
seeds_dir = "${KNOWLEDGE_SEEDS_DIR}"
index_tmp = "${INDEX_TMP}"

entries = []
seen_ids = set()

def load_jsonl(path):
    out = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"[build-knowledge-index] WARN: skipping malformed line in {path}", file=sys.stderr)
    except FileNotFoundError:
        pass
    return out

# Load all *.jsonl except index.jsonl
if os.path.isdir(kb_dir):
    for fname in sorted(os.listdir(kb_dir)):
        if fname.endswith(".jsonl") and fname not in ("index.jsonl", "index.jsonl.tmp"):
            path = os.path.join(kb_dir, fname)
            for e in load_jsonl(path):
                eid = e.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    entries.append(e)

# Load all *.yaml seed files from knowledge/seeds/
import glob as _glob
import yaml  # type: ignore[import]
for seed_path in sorted(_glob.glob(os.path.join(seeds_dir, "*.yaml"))):
    try:
        with open(seed_path) as f:
            seed = yaml.safe_load(f) or {}
        for e in seed.get("entries", []):
            eid = e.get("id", "")
            if eid and eid not in seen_ids:
                seen_ids.add(eid)
                entries.append(e)
    except Exception as exc:
        fname = os.path.basename(seed_path)
        print(f"[build-knowledge-index] WARN: {fname} parse error: {exc}", file=sys.stderr)

# Atomic write
with open(index_tmp, "w") as f:
    for e in entries:
        f.write(json.dumps(e) + "\n")

os.replace(index_tmp, "${INDEX_FILE}")
print(f"[build-knowledge-index] Wrote {len(entries)} entries → ${INDEX_FILE}", file=sys.stderr)
PYEOF

) 200>"${LOCK_FILE}"

exit 0
