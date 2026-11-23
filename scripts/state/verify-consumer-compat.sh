#!/usr/bin/env bash
# verify-consumer-compat.sh — Pre-implementation gate for #2070 rotation.
#
# All 3 adversarial reviewers (Claude/Codex/Gemini) flagged a P1 risk: rotating
# cost-tracking.jsonl into gzipped archives could break consumers that expect
# a single contiguous file. This script synthesizes a fixture (live JSONL + a
# rotated `.jsonl.gz` archive) and runs each known consumer against it,
# verifying that records from BOTH the live file and the archive are seen.
#
# Exit codes:
#   0  — all consumers verified, rotation safe to run
#   1  — at least one consumer failed; rotation must NOT run
#
# Known consumers (extend this list as more are discovered):
#   - scripts/ai/wrk_cost_report.py   (read; aggregates by WRK item)
#
# (Writers like provider-cost-tracker.sh are NOT consumers — they only append.)
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

LIVE_DIR="$TMPDIR/.claude/state/session-signals"
ARCHIVE_DIR="$LIVE_DIR/archive"
mkdir -p "$ARCHIVE_DIR"

LIVE="$LIVE_DIR/cost-tracking.jsonl"
ARC_PLAIN="$ARCHIVE_DIR/cost-tracking-2026-04-01.jsonl"

# Fixture: 1 live record + 2 archived records
cat > "$LIVE" <<'EOF'
{"wrk":"WRK-LIVE","input_tokens":100,"output_tokens":50,"cost_usd":0.01,"provider":"claude"}
EOF

cat > "$ARC_PLAIN" <<'EOF'
{"wrk":"WRK-ARCH-A","input_tokens":200,"output_tokens":100,"cost_usd":0.02,"provider":"claude"}
{"wrk":"WRK-ARCH-B","input_tokens":300,"output_tokens":150,"cost_usd":0.03,"provider":"codex"}
EOF
gzip "$ARC_PLAIN"

FAIL=0

# ── Consumer 1: wrk_cost_report.py ─────────────────────────────────────
echo "[verify] running scripts/ai/wrk_cost_report.py against rotated fixture..."
OUT="$(uv run --no-project python "$REPO_ROOT/scripts/ai/wrk_cost_report.py" \
        --data-file "$LIVE" 2>&1 || true)"

if echo "$OUT" | grep -q "WRK-LIVE" \
   && echo "$OUT" | grep -q "WRK-ARCH-A" \
   && echo "$OUT" | grep -q "WRK-ARCH-B"; then
    echo "  PASS"
else
    echo "  FAIL — wrk_cost_report.py did not see all expected records:"
    echo "$OUT" | sed 's/^/    | /'
    FAIL=1
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo
if (( FAIL == 0 )); then
    echo "[verify] OK — all consumers handle rotated archives. Rotation is SAFE."
    exit 0
else
    echo "[verify] FAIL — at least one consumer cannot handle rotation."
    echo "  Update the failing consumer(s) before running rotate-cost-tracking.sh."
    exit 1
fi
