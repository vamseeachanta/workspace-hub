#!/usr/bin/env bash
# Strategic brief: track balance bars + top scored items table.
# Usage: bash scripts/strategic/strategic-brief.sh [--top N]

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="${REPO_ROOT}/scripts/strategic"
TOP_N="${1:---top}"
TOP_VAL="${2:-5}"

# Parse --top N
if [[ "${TOP_N}" == "--top" ]]; then
    TOP="${TOP_VAL}"
else
    TOP=5
fi

# Generate YAML output to temp file (avoids quote escaping issues)
TMPFILE=$(mktemp /tmp/strategic-brief-XXXXXX.yaml)
trap 'rm -f "${TMPFILE}"' EXIT

uv run --no-project python "${SCRIPT_DIR}/strategic_score.py" --top "${TOP}" > "${TMPFILE}" 2>&1

if [[ $? -ne 0 ]]; then
    echo "ERROR: Scoring engine failed"
    cat "${TMPFILE}"
    exit 1
fi

# ── Render ───────────────────────────────────────────────────────────────

uv run --no-project python -c "
import sys, yaml
from pathlib import Path

data = yaml.safe_load(Path('${TMPFILE}').read_text())

# Header
print()
print('\033[1m━━━ Strategic Brief ━━━\033[0m')
print()

# Track Balance
print('\033[1mTrack Balance\033[0m')
print()
balance = data.get('track_balance', {})
for track in ['engineering', 'market', 'harness', 'other']:
    info = balance.get(track, {})
    target = info.get('target_pct', 0)
    actual = info.get('actual_pct', 0)
    status = info.get('status', 'unknown')
    delta = info.get('delta', 0)

    bar_len = int(actual / 2)
    bar = chr(9608) * bar_len + chr(9617) * (50 - bar_len)

    if status == 'under_served':
        color = '\033[31m'
    elif status == 'over_served':
        color = '\033[33m'
    else:
        color = '\033[32m'

    sign = '+' if delta > 0 else ''
    print(f'  {track:<13s} {color}{bar}\033[0m {actual:5.1f}% (target {target}%, {sign}{delta}pp)')

# Top Items Table
print()
items = data.get('ranked_items', [])
top_n = len(items)
print(f'\033[1mTop {top_n} Items\033[0m')
print()
print('  ┌─────────────────┬──────────────┬───────┬────────┐')
print('  │ ID              │ Track        │ Score │ Method │')
print('  ├─────────────────┼──────────────┼───────┼────────┤')
for item in items:
    wid = item['id'][:15]
    t = item['track'][:12]
    score = item['strategic_score']
    method = item['scoring_method'][:6]
    print(f'  │ {wid:<15s} │ {t:<12s} │ {score:5.1f} │ {method:<6s} │')
print('  └─────────────────┴──────────────┴───────┴────────┘')

# Recommendation
print()
rec = data.get('recommendation', {})
if rec:
    print(f\"\033[1mRecommendation:\033[0m {rec.get('next_item', 'N/A')} — {rec.get('rationale', '')}\")
print()
"
