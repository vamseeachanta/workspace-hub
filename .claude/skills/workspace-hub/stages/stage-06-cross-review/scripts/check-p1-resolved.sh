#!/usr/bin/env bash
# scripts/work-queue/check-p1-resolved.sh — verify all P1 cross-review findings are resolved
# Usage: check-p1-resolved.sh WRK-NNN [--assets-root <path>]
# Exit 0 = all P1s resolved; Exit 1 = unresolved P1s or missing evidence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: check-p1-resolved.sh WRK-NNN [--assets-root <path>]" >&2
  exit 1
fi

WRK_ID="$1"
shift

ASSETS_ROOT="${REPO_ROOT}/.claude/work-queue/assets"
while [ $# -gt 0 ]; do
  case "$1" in
    --assets-root) ASSETS_ROOT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

CROSS_REVIEW="${ASSETS_ROOT}/${WRK_ID}/evidence/cross-review.yaml"

if [ ! -f "$CROSS_REVIEW" ]; then
  echo "FAIL: ${CROSS_REVIEW} not found" >&2
  exit 1
fi

# Parse with Python for reliable YAML handling
uv run --no-project python3 -c "
import yaml, sys

with open('${CROSS_REVIEW}') as f:
    data = yaml.safe_load(f)

if not data:
    print('FAIL: cross-review.yaml is empty', file=sys.stderr)
    sys.exit(1)

# Collect total P1 count from reviewers (array or dict format)
total_p1 = 0
reviewers = data.get('reviewers', {})
if isinstance(reviewers, list):
    for r in reviewers:
        total_p1 += r.get('p1_count', 0)
elif isinstance(reviewers, dict):
    for name, r in reviewers.items():
        if isinstance(r, dict):
            total_p1 += r.get('p1_count', 0)

# If no P1s reported at all, pass
if total_p1 == 0:
    print('PASS: no P1 findings reported')
    sys.exit(0)

# P1s were reported — check p1_findings for resolutions
findings = data.get('p1_findings', [])
if not findings:
    print(f'FAIL: {total_p1} P1(s) reported but no p1_findings section', file=sys.stderr)
    sys.exit(1)

unresolved = []
for f in findings:
    fid = f.get('id', 'unknown')
    if not f.get('resolution'):
        unresolved.append(f)

if unresolved:
    print(f'FAIL: {len(unresolved)} unresolved P1 finding(s):', file=sys.stderr)
    for u in unresolved:
        desc = u.get('description', '').strip()[:80]
        print(f'  - {u.get(\"id\", \"unknown\")}: {desc}', file=sys.stderr)
    sys.exit(1)

print(f'PASS: all {len(findings)} P1 finding(s) have resolutions')
sys.exit(0)
"
