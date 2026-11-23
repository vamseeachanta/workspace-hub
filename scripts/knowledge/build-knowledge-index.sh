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
import json, os, sys, hashlib

kb_dir = "${KNOWLEDGE_BASE_DIR}"
seeds_dir = "${KNOWLEDGE_SEEDS_DIR}"
index_tmp = "${INDEX_TMP}"

entries = []
seen_ids = set()

def _synth_id(entry):
    """Generate a deterministic ID from entry content."""
    digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:12]
    return f"learned-{digest}"

def load_jsonl(path):
    """Load JSON objects from strict JSONL or concatenated pretty-printed JSON."""
    out = []
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        return out
    if not content.strip():
        return out
    # Fast path: try strict JSONL (one object per line)
    lines = content.splitlines()
    strict_ok = True
    strict_out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            strict_out.append(json.loads(line))
        except json.JSONDecodeError:
            strict_ok = False
            break
    if strict_ok:
        return strict_out
    # Slow path: streaming decode for concatenated multi-line JSON
    decoder = json.JSONDecoder()
    idx = 0
    length = len(content)
    while idx < length:
        # Skip whitespace
        while idx < length and content[idx] in ' \t\n\r':
            idx += 1
        if idx >= length:
            break
        try:
            obj, end_idx = decoder.raw_decode(content, idx)
            out.append(obj)
            idx = idx + end_idx
        except json.JSONDecodeError:
            # Skip one character and try again
            print(f"[build-knowledge-index] WARN: skipping malformed content at offset {idx} in {path}", file=sys.stderr)
            idx += 1
    return out

# Load all *.jsonl except index.jsonl
if os.path.isdir(kb_dir):
    for fname in sorted(os.listdir(kb_dir)):
        if fname.endswith(".jsonl") and fname not in ("index.jsonl", "index.jsonl.tmp"):
            path = os.path.join(kb_dir, fname)
            for e in load_jsonl(path):
                eid = e.get("id", "")
                if not eid:
                    eid = _synth_id(e)
                    e["id"] = eid
                if eid not in seen_ids:
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
