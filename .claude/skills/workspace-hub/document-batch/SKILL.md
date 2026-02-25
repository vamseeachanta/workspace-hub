# document-batch

Manage overnight LLM batch summarisation of engineering documents (WRK-309).

## Quick start — overnight run

Open a **separate terminal** (not inside Claude Code):

```bash
cd /mnt/local-analysis/workspace-hub
bash scripts/data/document-index/launch-batch.sh 10 all
```

Launches 10 parallel Claude Haiku shards covering:
1. `workspace_spec` — 1,542 workspace specs (fast, ~15 min total)
2. `og_standards` — remaining ~880 non-ASTM engineering standards
3. `ace_standards` — ~55K standards PDFs (overnight, fills credits)

## Single shard (test)

```bash
python3 scripts/data/document-index/phase-b-claude-worker.py \
  --shard 0 --total 10 --source workspace_spec --dry-run
```

## Monitor

```bash
# Live logs (all shards)
tail -f data/document-index/logs/claude-shard-*.log

# Count LLM-done summaries
grep -c '"discipline"' data/document-index/summaries/*.json 2>/dev/null | \
  awk -F: '$2>0' | wc -l

# Check completions
grep -h "COMPLETE" data/document-index/logs/claude-shard-*.log
```

## After completion — update registry

```bash
uv run --no-project --with pyyaml \
  python scripts/data/document-index/phase-e-registry.py \
  --config scripts/data/document-index/config.yaml --skip-legal
```

## Architecture

- Worker: `scripts/data/document-index/phase-b-claude-worker.py`
- Launch: `scripts/data/document-index/launch-batch.sh`
- LLM: `claude -p --model haiku --tools "" --max-turns 1 --output-format json`
- Auth: `env -u CLAUDECODE` (unsets nesting guard for subprocess calls)
- Resume-safe: skips files where `discipline` field already exists
- Output: `data/document-index/summaries/<sha256>.json`

## Tune throughput

- More shards = more parallel API calls = faster (credits exhaust quicker)
- `--limit N` caps docs per source per shard (useful for test runs)
- Change `--source` to target a single source type only
