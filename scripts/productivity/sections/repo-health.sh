#!/usr/bin/env bash
# ABOUTME: Daily log section — repo health dashboard (branch, dirty, tests) per repo
# Usage: bash repo-health.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"

echo "### Repo Health"
echo ""
echo "<details><summary>Show repo health table</summary>"
echo ""
echo '```'
bash "$WORKSPACE_ROOT/scripts/repo-health.sh" 2>/dev/null || echo "(repo-health.sh failed)"
echo '```'
echo ""
echo "</details>"
echo ""
