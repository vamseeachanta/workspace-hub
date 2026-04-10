#!/usr/bin/env bash
# query-knowledge.sh — Query the knowledge base by keyword or category
# Usage: query-knowledge.sh [--query KEYWORD] [--category CAT] [--limit N]
# Outputs: Markdown to stdout
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KNOWLEDGE_BASE_DIR="${KNOWLEDGE_BASE_DIR:-${REPO_ROOT}/knowledge-base}"
KNOWLEDGE_SEEDS_DIR="${KNOWLEDGE_SEEDS_DIR:-${REPO_ROOT}/knowledge/seeds}"

QUERY=""
CATEGORY=""
LIMIT=5

while [[ $# -gt 0 ]]; do
    case "$1" in
        --query)    QUERY="$2";    shift 2 ;;
        --category) CATEGORY="$2"; shift 2 ;;
        --limit)    LIMIT="$2";    shift 2 ;;
        *) shift ;;
    esac
done

uv run --no-project --with pyyaml python - <<PYEOF
import json, os, sys, re

kb_dir = "${KNOWLEDGE_BASE_DIR}"
seeds_dir = "${KNOWLEDGE_SEEDS_DIR}"
query = "${QUERY}".lower()
category = "${CATEGORY}".lower()
limit = ${LIMIT}

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
                    pass  # skip malformed lines
    except FileNotFoundError:
        pass
    return out

# Determine whether to use index.jsonl (source-mtime check)
index_path = os.path.join(kb_dir, "index.jsonl")
career_path = os.path.join(seeds_dir, "career-learnings.yaml")
wrk_path = os.path.join(kb_dir, "wrk-completions.jsonl")

use_index = False
if os.path.exists(index_path):
    idx_mtime = os.path.getmtime(index_path)
    src_mtimes = []
    for p in [wrk_path, career_path]:
        if os.path.exists(p):
            src_mtimes.append(os.path.getmtime(p))
    if src_mtimes and all(m <= idx_mtime for m in src_mtimes):
        use_index = True

if use_index:
    entries = load_jsonl(index_path)
else:
    # Load all *.jsonl except index.jsonl
    if os.path.isdir(kb_dir):
        for fname in os.listdir(kb_dir):
            if fname.endswith(".jsonl") and fname != "index.jsonl":
                entries.extend(load_jsonl(os.path.join(kb_dir, fname)))
    # Normalize career-learnings.yaml entries
    if os.path.exists(career_path):
        try:
            import yaml  # type: ignore[import]
            with open(career_path) as f:
                seed = yaml.safe_load(f) or {}
            for e in seed.get("entries", []):
                entries.append(e)
        except Exception:
            pass

# Dedup by id
deduped = []
for e in entries:
    eid = e.get("id", "")
    if eid not in seen_ids:
        seen_ids.add(eid)
        deduped.append(e)

# Filter by category
if category:
    deduped = [e for e in deduped if e.get("category", "").lower() == category]

# Score by keyword
def score(e):
    if not query:
        return 1
    text = " ".join([
        e.get("title", ""),
        e.get("mission", ""),
        e.get("context", ""),
        " ".join(e.get("patterns", [])),
    ]).lower()
    return text.count(query)

if query:
    deduped = [(score(e), e) for e in deduped]
    deduped = [(s, e) for s, e in deduped if s > 0]
    deduped.sort(key=lambda x: x[0], reverse=True)
    deduped = [e for _, e in deduped[:limit]]
else:
    deduped = deduped[:limit]

if not deduped:
    print("No knowledge entries found.")
    sys.exit(0)

for e in deduped:
    eid = e.get("id", "?")
    title = e.get("title", "")
    cat = e.get("category", "")
    etype = e.get("type", "wrk")
    if etype == "career":
        archived = e.get("learned_at", "")
        header_id = eid
        content_field = e.get("context", "")
    else:
        archived = e.get("archived_at", "")
        header_id = eid
        content_field = e.get("mission", "")

    print(f"## {header_id}: {title}")
    print(f"Category: {cat} | Archived: {archived}")
    if content_field:
        print(content_field[:150])
    patterns = e.get("patterns", [])
    if patterns:
        print("Patterns: " + "; ".join(str(p) for p in patterns[:3]))
    follow_ons = e.get("follow_ons", [])
    if follow_ons:
        print("Follow-ons: " + ", ".join(str(f) for f in follow_ons[:5]))
    print()

PYEOF
