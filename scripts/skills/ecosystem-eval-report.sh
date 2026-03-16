#!/usr/bin/env bash
# ecosystem-eval-report.sh — Orchestrate all 3 skill evaluation tools and collate into single YAML.
#
# Tools run:
#   1. eval-skills.py (18 structural checks)
#   2. audit-skill-violations.sh (4 hard constraints)
#   3. skill-coverage-audit.sh (script-wiring gaps)
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
COLLATED_YAML="${AUDIT_DIR}/skill-eval-${DATE}.yaml"

echo "=== Skill Ecosystem Evaluation Report ===" >&2
echo "Date: ${DATE}" >&2
echo "" >&2

# --- Tool 1: eval-skills.py ---
echo "[1/3] Running eval-skills.py ..." >&2
EVAL_EXIT=0
uv run --no-project python \
  .claude/skills/development/skill-eval/scripts/eval-skills.py \
  --format json --output "$EVAL_JSON" 2>&1 || EVAL_EXIT=$?
echo "  eval-skills.py exit: ${EVAL_EXIT}" >&2

# --- Tool 2: audit-skill-violations.sh ---
echo "[2/3] Running audit-skill-violations.sh ..." >&2
VIOLATIONS_EXIT=0
bash scripts/skills/audit-skill-violations.sh > "$VIOLATIONS_YAML" 2>/dev/null || VIOLATIONS_EXIT=$?
echo "  audit-skill-violations.sh exit: ${VIOLATIONS_EXIT}" >&2

# --- Tool 3: skill-coverage-audit.sh ---
echo "[3/3] Running skill-coverage-audit.sh ..." >&2
COVERAGE_EXIT=0
bash scripts/skills/skill-coverage-audit.sh > "$COVERAGE_YAML" 2>/dev/null || COVERAGE_EXIT=$?
echo "  skill-coverage-audit.sh exit: ${COVERAGE_EXIT}" >&2

# --- Collate ---
echo "" >&2
echo "Collating results into ${COLLATED_YAML} ..." >&2

uv run --no-project python -c "
import json, yaml, sys
from datetime import datetime, timezone

eval_json = '${EVAL_JSON}'
violations_yaml = '${VIOLATIONS_YAML}'
coverage_yaml = '${COVERAGE_YAML}'

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
}

with open('${COLLATED_YAML}', 'w') as f:
    yaml.dump(report, f, default_flow_style=False, sort_keys=False, width=120)

print(f'Total skills: {total_skills}')
print(f'Eval passed: {eval_data[\"summary\"][\"passed\"]}')
print(f'Violations: {len(violations_list)}')
print(f'Coverage gaps: {gaps_total}')
print(f'Coverage: {report[\"coverage_summary\"][\"coverage_pct\"]}%')
"

echo "" >&2
echo "Report written to: ${COLLATED_YAML}" >&2
echo "Detail files: ${EVAL_JSON}, ${VIOLATIONS_YAML}, ${COVERAGE_YAML}" >&2

# Exit 1 if any tool found issues
if [[ "$EVAL_EXIT" -ne 0 ]] || [[ "$VIOLATIONS_EXIT" -ne 0 ]] || [[ "$COVERAGE_EXIT" -ne 0 ]]; then
  exit 1
fi
exit 0
