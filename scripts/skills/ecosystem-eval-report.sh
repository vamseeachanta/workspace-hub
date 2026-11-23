#!/usr/bin/env bash
# ecosystem-eval-report.sh — Orchestrate all 4 skill evaluation tools and collate into single YAML.
#
# Tools run:
#   1. eval-skills.py (18 structural checks)
#   2. audit-skills.py --mode violations (4 hard constraints)
#   3. audit-skills.py --mode coverage (script-wiring gaps)
#   4. skill-tier-report.py (quality tier classification A/B/C/D)
#
# Output: specs/audit/skill-eval-<date>.yaml (collated report)
# Exit: 0 = success, 1 = tools found issues, 2 = script error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$REPO_ROOT"

DATE="$(date +%Y-%m-%d)"
AUDIT_DIR="specs/audit"
mkdir -p "$AUDIT_DIR"

EVAL_JSON="${AUDIT_DIR}/skill-eval-${DATE}.json"
VIOLATIONS_YAML="${AUDIT_DIR}/skill-violations-${DATE}.yaml"
COVERAGE_YAML="${AUDIT_DIR}/skill-coverage-gaps-${DATE}.yaml"
TIER_YAML="${AUDIT_DIR}/skill-tiers-${DATE}.yaml"
COLLATED_YAML="${AUDIT_DIR}/skill-eval-${DATE}.yaml"

echo "=== Skill Ecosystem Evaluation Report ===" >&2
echo "Date: ${DATE}" >&2
echo "" >&2

# --- Tool 1: eval-skills.py ---
echo "[1/4] Running eval-skills.py ..." >&2
EVAL_EXIT=0
uv run --no-project python \
  .claude/skills/development/skill-eval/scripts/eval-skills.py \
  --format json --output "$EVAL_JSON" 2>&1 || EVAL_EXIT=$?
echo "  eval-skills.py exit: ${EVAL_EXIT}" >&2

# --- Tool 2: audit-skills.py --mode violations (replaces audit-skill-violations.sh) ---
echo "[2/4] Running audit-skills.py --mode violations ..." >&2
VIOLATIONS_EXIT=0
uv run --no-project python scripts/skills/audit-skills.py --mode violations > "$VIOLATIONS_YAML" 2>/dev/null || VIOLATIONS_EXIT=$?
echo "  audit-skills.py violations exit: ${VIOLATIONS_EXIT}" >&2

# --- Tool 3: audit-skills.py --mode coverage (replaces skill-coverage-audit.sh) ---
echo "[3/4] Running audit-skills.py --mode coverage ..." >&2
COVERAGE_EXIT=0
uv run --no-project python scripts/skills/audit-skills.py --mode coverage > "$COVERAGE_YAML" 2>/dev/null || COVERAGE_EXIT=$?
echo "  audit-skills.py coverage exit: ${COVERAGE_EXIT}" >&2

# --- Tool 4: skill-tier-report.py (quality tier classification) ---
echo "[4/4] Running skill-tier-report.py ..." >&2
TIER_EXIT=0
uv run --no-project python scripts/skills/skill-tier-report.py --format yaml --output "$TIER_YAML" 2>&1 || TIER_EXIT=$?
echo "  skill-tier-report.py exit: ${TIER_EXIT}" >&2

# --- Collate ---
echo "" >&2
echo "Collating results into ${COLLATED_YAML} ..." >&2

uv run --no-project python -c "
import json, yaml, sys
from datetime import datetime, timezone

eval_json = '${EVAL_JSON}'
violations_yaml = '${VIOLATIONS_YAML}'
coverage_yaml = '${COVERAGE_YAML}'
tier_yaml = '${TIER_YAML}'

with open(eval_json) as f:
    eval_data = json.load(f)

try:
    with open(violations_yaml) as f:
        violations_data = yaml.safe_load(f) or {}
except FileNotFoundError:
    violations_data = {}

try:
    with open(coverage_yaml) as f:
        coverage_data = yaml.safe_load(f) or {}
except FileNotFoundError:
    coverage_data = {}

try:
    with open(tier_yaml) as f:
        tier_data = yaml.safe_load(f) or {}
except FileNotFoundError:
    tier_data = {}

total_skills = eval_data['summary']['total_skills']
gaps_total = coverage_data.get('gaps_total', 0)
violations_list = violations_data.get('violations', [])

violation_counts = {}
for v in violations_list:
    check = v.get('check', 'unknown')
    violation_counts[check] = violation_counts.get(check, 0) + 1

report = {
    'report_date': '${DATE}',
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'tools_run': [
        'eval-skills.py (18 structural checks)',
        'audit-skill-violations.sh (4 hard constraints)',
        'skill-coverage-audit.sh (script-wiring gaps)',
        'skill-tier-report.py (quality tier A/B/C/D)',
    ],
    'eval_summary': eval_data['summary'],
    'eval_top_issues': eval_data['top_issues'],
    'eval_by_category': eval_data['by_category'],
    'violations_summary': {
        'total_violations': len(violations_list),
        'by_check': violation_counts,
    },
    'coverage_summary': {
        'gaps_total': gaps_total,
        'total_skills': total_skills,
        'coverage_pct': round(100 * (1 - gaps_total / total_skills), 1) if total_skills else 0,
    },
    'tier_summary': tier_data.get('tier_distribution', {}),
}

with open('${COLLATED_YAML}', 'w') as f:
    yaml.dump(report, f, default_flow_style=False, sort_keys=False, width=120)

print(f'Total skills: {total_skills}')
print(f'Eval passed: {eval_data[\"summary\"][\"passed\"]}')
print(f'Violations: {len(violations_list)}')
print(f'Coverage gaps: {gaps_total}')
print(f'Coverage: {report[\"coverage_summary\"][\"coverage_pct\"]}%')
tier_dist = tier_data.get('tier_distribution', {})
print(f'Tiers: A={tier_dist.get(\"A\",0)} B={tier_dist.get(\"B\",0)} C={tier_dist.get(\"C\",0)} D={tier_dist.get(\"D\",0)}')
"

echo "" >&2
echo "Report written to: ${COLLATED_YAML}" >&2
echo "Detail files: ${EVAL_JSON}, ${VIOLATIONS_YAML}, ${COVERAGE_YAML}" >&2

# Exit 1 if any tool found issues
if [[ "$EVAL_EXIT" -ne 0 ]] || [[ "$VIOLATIONS_EXIT" -ne 0 ]] || [[ "$COVERAGE_EXIT" -ne 0 ]] || [[ "$TIER_EXIT" -ne 0 ]]; then
  exit 1
fi
exit 0
