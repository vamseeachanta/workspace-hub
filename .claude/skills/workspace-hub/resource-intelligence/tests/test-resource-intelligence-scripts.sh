#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
INIT="${ROOT}/.claude/skills/workspace-hub/resource-intelligence/scripts/init-resource-pack.sh"
VALIDATE="${ROOT}/.claude/skills/workspace-hub/resource-intelligence/scripts/validate-resource-pack.sh"
SYNC="${ROOT}/.claude/skills/workspace-hub/resource-intelligence/scripts/sync-maturity-summary.py"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

assert_fail() {
  if "$@"; then
    echo "Expected failure: $*" >&2
    exit 1
  fi
}

assert_file() {
  [[ -f "$1" ]] || { echo "Missing file: $1" >&2; exit 1; }
}

pushd "$tmpdir" >/dev/null
git init -q

mkdir -p .claude/skills/workspace-hub/resource-intelligence/templates
mkdir -p .claude/work-queue/assets
cp "${ROOT}/.claude/skills/workspace-hub/resource-intelligence/templates/resource-intelligence-summary.md" \
  .claude/skills/workspace-hub/resource-intelligence/templates/resource-intelligence-summary.md

assert_fail bash "$INIT" BAD-1
bash "$INIT" WRK-900

asset_dir="${tmpdir}/.claude/work-queue/assets/WRK-900"
assert_file "${asset_dir}/resource-pack.md"
assert_file "${asset_dir}/sources.md"
assert_file "${asset_dir}/resources.yaml"
assert_file "${asset_dir}/resource-intelligence-summary.md"

cat > "${asset_dir}/sources.md" <<'EOF'
# Sources
- AGENTS.md
EOF

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
sources:
  - AGENTS.md
EOF

cat > "${asset_dir}/resource-intelligence-summary.md" <<'EOF'
# Resource Intelligence Summary

- `wrk_id`: WRK-900
- `summary`: ok
- `top_p1_gaps`:
  - none
- `top_p2_gaps`:
  - validator threshold not chosen yet
- `top_p3_gaps`:
  - none
- `user_decision`: continue_to_planning
- `reviewed_at`: 2026-03-01T00:00:00Z
- `reviewer`: codex
- `legal_scan_ref`: not_applicable
- `indexing_ref`: not_applicable
EOF

bash "$VALIDATE" WRK-900

perl -0pi -e 's/- `top_p1_gaps`:\n  - none/- `top_p1_gaps`:\n  - missing legal review/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900

mkdir -p data/document-index
cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
target_window: "3 months"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 0
  documents_marked_read_percent: 0
  key_calculations_implemented: []
  followup_wrks: []
notes:
  - "YAML is the source of truth."
EOF

python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check
assert_fail python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/wrong.md --check

popd >/dev/null
echo "Resource Intelligence script tests passed"
