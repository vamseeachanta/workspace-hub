# WRK-1140: Nightly Release-Notes Scan and WRK Capture

## Context

The `release-notes-adoption` skill is manual — someone must remember to check for new AI tool versions and run analysis. WRK-1140 automates the detection half: a nightly cron step compares installed CLI versions against `config/ai-tools/release-scan-state.yaml`, and when a new version is found, creates a WRK item prompting the human to run the analysis skill next session.

**Design decision:** The script detects version changes deterministically (Option D). It does NOT fetch or parse release notes — that judgment call stays with the human + skill. Scripts handle mechanics; skills handle judgment.

## Architecture

**Two files, clear split:**

| File | Language | Responsibility |
|---|---|---|
| `scripts/automation/nightly-release-scan.sh` | Bash (~100 lines) | Version detection via `--version`, CLI PATH resolution, dry-run flag, orchestration |
| `scripts/automation/release_scan_wrk.py` | Python (~80 lines) | YAML state I/O, WRK file generation via `next-id.sh`, INDEX.md rebuild |

**Arguments:** `--dry-run` (print without writing), `--provider claude|codex|gemini|all` (default: all)
**Exit codes:** 0 = success (including "no changes"), 1 = internal error

## Version Detection

Reuses `ai-agent-readiness.sh` pattern:
```bash
claude --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?'
```
Compare with `sort -V`. Skip if current <= last_seen (downgrades not actionable).

## WRK Creation

One WRK per scan run (batches all provider changes). Template:
- `category: harness`, `subcategory: tooling`, `priority: medium`, `complexity: simple`
- Body: detected changes table + "Run `/release-notes-adoption` next session"
- Uses `next-id.sh` for atomic ID, then `generate-index.py` for INDEX rebuild

## Cron Integration

Insert into `comprehensive-learning-nightly.sh` after Step 3b (ai-agent-readiness):

```bash
# Step 3c: release-notes scan (best-effort — WRK-1140)
echo "--- Release notes scan $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/automation/nightly-release-scan.sh || \
  echo "WARNING: release notes scan failed — see above"

# Auto-commit any WRK items created by the release scan
if ! git diff --quiet .claude/work-queue/ config/ai-tools/release-scan-state.yaml 2>/dev/null; then
  git add .claude/work-queue/pending/WRK-*.md .claude/work-queue/INDEX.md config/ai-tools/release-scan-state.yaml
  git commit -m "chore(release-scan): nightly scan — $(date +%Y-%m-%d)"
  git push
fi
```

Renumber existing 3c→3d, 3d→3e (comments only).

## Files

**Create:**
- `scripts/automation/nightly-release-scan.sh` — Bash driver
- `scripts/automation/release_scan_wrk.py` — Python WRK generator
- `tests/automation/test_release_scan_wrk.py` — 11 Python unit tests
- `tests/automation/test_nightly_release_scan.sh` — Bash integration test

**Modify:**
- `scripts/cron/comprehensive-learning-nightly.sh` — insert Step 3c (~10 lines)

**Referenced (not modified):**
- `scripts/work-queue/next-id.sh`, `scripts/lib/python-resolver.sh`, `.claude/work-queue/scripts/generate-index.py`

## Test Strategy (TDD)

11 Python tests covering:
- State YAML parsing (all providers, empty versions)
- Version change detection (new, same, first-scan, downgrade-ignored)
- WRK content generation (single provider, multi-provider)
- State update (version + timestamp persisted)
- Idempotency (re-run with same version → no WRK)
- Dry-run (no file writes)

Bash integration test: mock CLIs via PATH override, verify dry-run output.

## Implementation Sequence

1. Write failing tests (`tests/automation/test_release_scan_wrk.py`)
2. Implement `release_scan_wrk.py` — make tests green
3. Write Bash integration test
4. Implement `nightly-release-scan.sh` — make integration test pass
5. Modify `comprehensive-learning-nightly.sh` — insert Step 3c
6. Smoke test: `--dry-run` then live run
7. Commit + push

## Verification

```bash
# Unit tests
uv run --no-project python -m pytest tests/automation/test_release_scan_wrk.py -v

# Dry-run smoke test
bash scripts/automation/nightly-release-scan.sh --dry-run

# Live test (creates WRK if version differs from state)
bash scripts/automation/nightly-release-scan.sh

# Verify WRK created + state updated
cat config/ai-tools/release-scan-state.yaml
ls -la .claude/work-queue/pending/WRK-*.md | tail -1
```
