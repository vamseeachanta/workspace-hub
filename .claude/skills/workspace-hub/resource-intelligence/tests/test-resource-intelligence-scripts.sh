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
  return 0
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
- AGENTS
- EXTRA
- WORKSPACE
EOF

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: true
sources: []
EOF

assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
sources:
  - AGENTS.md
EOF

assert_fail bash "$VALIDATE" WRK-900

mkdir -p data/document-index
cat > data/document-index/mounted-source-registry.yaml <<'EOF'
generated: "2026-03-01T00:00:00Z"
source_roots:
  - source_id: AGENTS
    document_intelligence_bucket: workspace_spec
    mount_root: AGENTS.md
  - source_id: WORKSPACE
    document_intelligence_bucket: workspace_spec
    mount_root: /mnt/local-analysis/workspace-hub
EOF

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
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

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: true
sources:
  - id: AGENTS
    source_type: additive
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: additive
    status: available
EOF
assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
EOF
bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: 'WRK-900'
no_external_sources: false
sources:
  - id: 'AGENTS'
    source_type: 'registry'
    origin: 'AGENTS.md'
    license_access: 'repo-native'
    retrieval_date: '2026-03-01'
    canonical_storage_path: 'AGENTS.md'
    duplicate_status: 'canonical'
    status: 'available'
EOF
bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - source_type: registry
    id: AGENTS
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
EOF
bash "$VALIDATE" WRK-900

rm data/document-index/mounted-source-registry.yaml
assert_fail bash "$VALIDATE" WRK-900
cat > data/document-index/mounted-source-registry.yaml <<'EOF'
generated: "2026-03-01T00:00:00Z"
source_roots:
  - source_id: AGENTS
    document_intelligence_bucket: workspace_spec
    mount_root: AGENTS.md
  - source_id: WORKSPACE
    document_intelligence_bucket: workspace_spec
    mount_root: /mnt/local-analysis/workspace-hub
EOF
bash "$VALIDATE" WRK-900

perl -0pi -e 's/id: AGENTS/id: BAD_ID/' "${asset_dir}/resources.yaml"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/id: BAD_ID/id: AGENTS/' "${asset_dir}/resources.yaml"

perl -0pi -e 's/source_type: registry/source_type: additive/' "${asset_dir}/resources.yaml"
bash "$VALIDATE" WRK-900
perl -0pi -e 's/source_type: additive/source_type: registry/' "${asset_dir}/resources.yaml"

perl -0pi -e 's/- `top_p1_gaps`:\n  - none/- `top_p1_gaps`:\n  - missing legal review/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `top_p1_gaps`:\n  - missing legal review/- `top_p1_gaps`:\n  - none/' "${asset_dir}/resource-intelligence-summary.md"

perl -0pi -e 's/- `reviewer`: codex//' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `summary`: ok/- `summary`: ok\n- `reviewer`: codex/' "${asset_dir}/resource-intelligence-summary.md"
perl -0pi -e 's/- `top_p1_gaps`:\n  - none//' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `summary`: ok\n- `reviewer`: codex/- `summary`: ok\n- `top_p1_gaps`:\n  - none\n- `reviewer`: codex/' "${asset_dir}/resource-intelligence-summary.md"
perl -0pi -e 's/- `top_p1_gaps`:\n  - none/- `top_p1_gaps`: blocker still here/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `top_p1_gaps`: blocker still here/- `top_p1_gaps`:\n  - none/' "${asset_dir}/resource-intelligence-summary.md"
perl -0pi -e 's/- `top_p3_gaps`:\n/- `top_p3_gaps`:\n- `top_p3_gaps`:\n/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `top_p3_gaps`:\n- `top_p3_gaps`:\n/- `top_p3_gaps`:\n/' "${asset_dir}/resource-intelligence-summary.md"
perl -0pi -e 's/- `top_p2_gaps`:\n  - validator threshold not chosen yet/- `top_p2_gaps`: validator threshold not chosen yet/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `top_p2_gaps`: validator threshold not chosen yet/- `top_p2_gaps`:\n  - validator threshold not chosen yet/' "${asset_dir}/resource-intelligence-summary.md"
perl -0pi -e 's/- `top_p3_gaps`:\n  - none/- `top_p3_gaps`: none/' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's/- `top_p3_gaps`: none/- `top_p3_gaps`:\n  - none/' "${asset_dir}/resource-intelligence-summary.md"

cat > "${asset_dir}/legal-scan.md" <<'EOF'
# Legal Scan

ok
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
- `legal_scan_ref`: ../../outside.md
- `indexing_ref`: not_applicable
EOF
touch "${tmpdir}/outside.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's#../../outside.md#.claude/work-queue/assets/WRK-900/legal-scan.md#' "${asset_dir}/resource-intelligence-summary.md"
bash "$VALIDATE" WRK-900

perl -0pi -e 's#`indexing_ref`: not_applicable#`indexing_ref`: ../../outside.md#' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's#`indexing_ref`: ../../outside.md#`indexing_ref`: not_applicable#' "${asset_dir}/resource-intelligence-summary.md"
bash "$VALIDATE" WRK-900
perl -0pi -e 's#`indexing_ref`: not_applicable#`indexing_ref`: data/document-index/registry.yaml#' "${asset_dir}/resource-intelligence-summary.md"
assert_fail bash "$VALIDATE" WRK-900
perl -0pi -e 's#`indexing_ref`: data/document-index/registry.yaml#`indexing_ref`: not_applicable#' "${asset_dir}/resource-intelligence-summary.md"
bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: /tmp/not-registry
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: /tmp/not-registry
    duplicate_status: canonical
    status: available
EOF
assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: WORKSPACE
    source_type: registry
    origin: /mnt/local-analysis/workspace-hub-backup
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: /mnt/local-analysis/workspace-hub-backup
    duplicate_status: canonical
    status: available
EOF
assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: offline
EOF
assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
EOF
bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
  - id: EXTRA
    source_type: additive
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: EXTRA.md
    duplicate_status: additive
    status: available
EOF
assert_fail bash "$VALIDATE" WRK-900

cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
  - id: EXTRA
    source_type: additive
    origin: EXTRA.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: EXTRA.md
    duplicate_status: additive
    status: available
EOF
bash "$VALIDATE" WRK-900

# Regression: non-empty routing_overrides must not be parsed as source entries
cat > "${asset_dir}/resources.yaml" <<'EOF'
wrk_id: WRK-900
no_external_sources: false
sources:
  - id: AGENTS
    source_type: registry
    origin: AGENTS.md
    license_access: repo-native
    retrieval_date: 2026-03-01
    canonical_storage_path: AGENTS.md
    duplicate_status: canonical
    status: available
routing_overrides:
  - decision: use_claude
    reason: advisor conflict resolved by orchestrator
    recorded_at: 2026-03-01T00:00:00Z
    recorded_by: orchestrator
EOF
bash "$VALIDATE" WRK-900

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
schema_version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
  measurement_owner: orchestrator
  measurement_process: update from reviewed resource packs and linked follow-up WRKs
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
grep -Fq 'Canonical state: [data/document-index/resource-intelligence-maturity.yaml](data/document-index/resource-intelligence-maturity.yaml)' data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check
assert_fail python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/wrong.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
schema_version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
  measurement_owner: orchestrator
  measurement_process: update from reviewed resource packs and linked follow-up WRKs
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 2
  documents_marked_read_percent: 40
  key_calculations_implemented: ["calc-a", "calc-b"]
  followup_wrks: ["WRK-901", "WRK-902"]
notes:
  - "YAML is the source of truth."
EOF
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md
grep -Fq 'Key calculations implemented: calc-a, calc-b' data/document-index/resource-intelligence-maturity.md
grep -Fq 'Follow-up WRKs: WRK-901, WRK-902' data/document-index/resource-intelligence-maturity.md
grep -Fq 'Measurement owner: orchestrator' data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: '2026-02-28T00:00:00Z'
version: '1.0.0'
schema_version: '1.0.0'
target_window: '3 months'
target_start: '2026-03-01'
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
  measurement_owner: 'orchestrator'
  measurement_process: 'update from reviewed resource packs and linked follow-up WRKs'
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 2
  documents_marked_read_percent: 40
  key_calculations_implemented: ['calc-a', 'calc-b']
  followup_wrks: ['WRK-901', 'WRK-902']
notes:
  - 'YAML is the source of truth.'
EOF
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md
grep -Fq 'Key calculations implemented: calc-a, calc-b' data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
schema_version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
    documents_read_threshold_percent: 80
    key_calculations_implemented_required: true
    measurement_owner: orchestrator
    measurement_process: update from reviewed resource packs and linked follow-up WRKs
tracking:
    canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
    documents_in_scope: 5
    documents_marked_read: 2
    documents_marked_read_percent: 40
    key_calculations_implemented:
        - calc-a
        - calc-b
    followup_wrks:
        - WRK-901
        - WRK-902
notes:
    - "YAML is the source of truth."
EOF
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md
grep -Fq 'Key calculations implemented: calc-a, calc-b' data/document-index/resource-intelligence-maturity.md
grep -Fq 'Follow-up WRKs: WRK-901, WRK-902' data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 2
  documents_marked_read_percent: 40
  key_calculations_implemented: ["calc-a", "calc-b"]
  followup_wrks: ["WRK-901", "WRK-902"]
notes:
  - "YAML is the source of truth."
EOF
assert_fail python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
schema_version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 2
  documents_marked_read_percent: 40
  key_calculations_implemented: ["calc-a", "calc-b"]
  followup_wrks: ["WRK-901", "WRK-902"]
notes:
  - "YAML is the source of truth."
EOF
assert_fail python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

cat > data/document-index/resource-intelligence-maturity.yaml <<'EOF'
generated: "2026-02-28T00:00:00Z"
version: "1.0.0"
schema_version: "1.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
  measurement_owner: orchestrator
  measurement_process: update from reviewed resource packs and linked follow-up WRKs
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
status:
  documents_in_scope: 5
  documents_marked_read: 2
  documents_marked_read_percent: 40
  key_calculations_implemented: ["calc-a", "calc-b"]
  followup_wrks: ["WRK-901", "WRK-902"]
notes:
  - "YAML is the source of truth."
EOF
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md
python3 "$SYNC" --yaml data/document-index/resource-intelligence-maturity.yaml --markdown data/document-index/resource-intelligence-maturity.md --check

mkdir -p nested/work
pushd nested/work >/dev/null
python3 "$SYNC" --yaml ../../data/document-index/resource-intelligence-maturity.yaml --markdown ../../data/document-index/resource-intelligence-maturity.md --check
popd >/dev/null

popd >/dev/null
echo "Resource Intelligence script tests passed"
