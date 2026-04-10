#!/usr/bin/env bash
# skill-health-dashboard.sh — Unified skill health dashboard (#1562)
#
# Runs all audit scripts and computes a weighted health score (0-100).
# Safe for nightly cron: each audit is non-blocking (failures use fallback values).
#
# Output:
#   - Formatted dashboard to stdout
#   - JSON to .claude/state/skill-health/YYYY-MM-DD.json
#
# Usage:
#   bash scripts/skills/skill-health-dashboard.sh
#   bash scripts/skills/skill-health-dashboard.sh --quiet   # JSON only, no stdout dashboard
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$WS_HUB"

TODAY=$(date -u +%Y-%m-%d)
STATE_DIR=".claude/state/skill-health"
OUTPUT_JSON="${STATE_DIR}/${TODAY}.json"
QUIET=false

[[ "${1:-}" == "--quiet" ]] && QUIET=true

mkdir -p "$STATE_DIR"

# ---------------------------------------------------------------------------
# Helper: count SKILL.md files (excluding _archive, _diverged)
# ---------------------------------------------------------------------------
total_skills=$(find .claude/skills -name SKILL.md \
  -not -path '*/_archive/*' \
  -not -path '*/_diverged/*' 2>/dev/null | wc -l | tr -d ' ')
total_skills=${total_skills:-0}

# ---------------------------------------------------------------------------
# 1. Eval Coverage: skills with evals / total skills
# ---------------------------------------------------------------------------
eval_count=$(ls .planning/skills/evals/*.yaml 2>/dev/null | wc -l | tr -d ' ')
eval_count=${eval_count:-0}

if (( total_skills > 0 )); then
  eval_coverage_score=$(( eval_count * 100 / total_skills ))
else
  eval_coverage_score=0
fi
eval_coverage_detail="${eval_count}/${total_skills} skills have evals"

# ---------------------------------------------------------------------------
# 2. Eval Pass Rate: from latest eval results JSONL
# ---------------------------------------------------------------------------
EVAL_DIR=".claude/state/skill-eval-results"
latest_eval=$(ls "${EVAL_DIR}/"*.jsonl 2>/dev/null | sort | tail -1)

if [[ -n "$latest_eval" ]]; then
  eval_pass=$(grep -c '"result"[: ]*"pass"' "$latest_eval" 2>/dev/null || true)
  eval_pass=${eval_pass:-0}; eval_pass=$(echo "$eval_pass" | tr -d '[:space:]'); eval_pass=${eval_pass:-0}
  eval_fail=$(grep -c '"result"[: ]*"fail"' "$latest_eval" 2>/dev/null || true)
  eval_fail=${eval_fail:-0}; eval_fail=$(echo "$eval_fail" | tr -d '[:space:]'); eval_fail=${eval_fail:-0}
  eval_skip=$(grep -c '"result"[: ]*"skip"' "$latest_eval" 2>/dev/null || true)
  eval_skip=${eval_skip:-0}; eval_skip=$(echo "$eval_skip" | tr -d '[:space:]'); eval_skip=${eval_skip:-0}
  eval_total=$(( eval_pass + eval_fail ))
  if (( eval_total > 0 )); then
    eval_pass_score=$(( eval_pass * 100 / eval_total ))
  else
    eval_pass_score=100
  fi
  eval_pass_detail="${eval_pass}/${eval_total} checks pass"
else
  eval_pass=0
  eval_fail=0
  eval_total=0
  eval_pass_score=100
  eval_pass_detail="no eval results yet"
fi

# ---------------------------------------------------------------------------
# 3. Reference Health: from latest rot report
# ---------------------------------------------------------------------------
ROT_DIR=".claude/state/skill-rot-report"
latest_rot=$(ls "${ROT_DIR}/"*.json 2>/dev/null | sort | tail -1)

if [[ -n "$latest_rot" ]]; then
  broken_file_paths_count=$(uv run --no-project python -c "
import json, sys
try:
    d = json.load(open('$latest_rot'))
    s = d.get('summary', {})
    # Total broken references = broken_refs + broken_scripts + broken_file_paths
    total = s.get('broken_refs_count', 0) + s.get('broken_scripts_count', 0) + s.get('broken_file_paths_count', 0)
    print(total)
except Exception:
    print(0)
" 2>/dev/null || echo 0)
  rot_skills_indexed=$(uv run --no-project python -c "
import json
try:
    d = json.load(open('$latest_rot'))
    print(d.get('skills_indexed', $total_skills))
except Exception:
    print($total_skills)
" 2>/dev/null || echo "$total_skills")

  if (( rot_skills_indexed > 0 )); then
    # Each broken ref reduces health proportionally
    if (( broken_file_paths_count >= rot_skills_indexed )); then
      ref_health_score=0
    else
      ref_health_score=$(( (rot_skills_indexed - broken_file_paths_count) * 100 / rot_skills_indexed ))
    fi
  else
    ref_health_score=100
  fi
  ref_health_detail="${broken_file_paths_count} broken refs"
else
  broken_file_paths_count=0
  ref_health_score=100
  ref_health_detail="no rot report yet"
fi

# ---------------------------------------------------------------------------
# 4. Usage Health: from latest usage report
# ---------------------------------------------------------------------------
USAGE_DIR=".claude/state/skill-usage-report"
latest_usage=$(ls "${USAGE_DIR}/"*.json 2>/dev/null | sort | tail -1)

if [[ -n "$latest_usage" ]]; then
  usage_data=$(uv run --no-project python -c "
import json, sys
try:
    d = json.load(open('$latest_usage'))
    s = d.get('summary', {})
    total = d.get('total_skills', $total_skills)
    dead = s.get('dead', 0)
    print(f'{dead} {total}')
except Exception:
    print('0 $total_skills')
" 2>/dev/null || echo "0 $total_skills")
  dead_skills=$(echo "$usage_data" | awk '{print $1}')
  usage_total=$(echo "$usage_data" | awk '{print $2}')

  if (( usage_total > 0 )); then
    usage_health_score=$(( (usage_total - dead_skills) * 100 / usage_total ))
  else
    usage_health_score=100
  fi
  usage_health_detail="${dead_skills} dead skills"
else
  dead_skills=0
  usage_total=$total_skills
  usage_health_score=100
  usage_health_detail="no usage report yet"
fi

# ---------------------------------------------------------------------------
# 5. Description Compliance: run audit-descriptions.py, count violations
# ---------------------------------------------------------------------------
desc_violations=0
desc_total=$total_skills
desc_output=$(uv run --no-project python "${WS_HUB}/scripts/skills/audit-descriptions.py" 2>/dev/null || true)
if [[ -n "$desc_output" ]]; then
  # Parse "Total violations:" line from output
  desc_violations=$(echo "$desc_output" | grep -i "Total violations:" | grep -oP '\d+' | tail -1 || echo 0)
  desc_violations=${desc_violations:-0}
fi

if (( desc_total > 0 && desc_violations >= 0 )); then
  if (( desc_violations >= desc_total )); then
    desc_score=0
  else
    desc_score=$(( (desc_total - desc_violations) * 100 / desc_total ))
  fi
else
  desc_score=100
fi
desc_detail="${desc_violations} violations"

# ---------------------------------------------------------------------------
# 6. Size Compliance: run find-oversized-skills.py, count oversized
# ---------------------------------------------------------------------------
oversized_output=$(uv run --no-project python "${WS_HUB}/scripts/skills/find-oversized-skills.py" 2>&1 || true)
# The stderr line: "N skills over 200 lines"
oversized_count=$(echo "$oversized_output" | grep -oP '^\d+(?= skills over)' || echo 0)
oversized_count=${oversized_count:-0}

if (( total_skills > 0 )); then
  if (( oversized_count >= total_skills )); then
    size_score=0
  else
    size_score=$(( (total_skills - oversized_count) * 100 / total_skills ))
  fi
else
  size_score=100
fi
size_detail="${oversized_count} oversized"

# ---------------------------------------------------------------------------
# Compute weighted overall score
# ---------------------------------------------------------------------------
# Weights: eval_coverage=25, eval_pass=25, ref_health=20, usage=15, desc=10, size=5
overall_score=$(( \
  (eval_coverage_score * 25 + \
   eval_pass_score * 25 + \
   ref_health_score * 20 + \
   usage_health_score * 15 + \
   desc_score * 10 + \
   size_score * 5) / 100 ))

# Clamp to 0-100
(( overall_score > 100 )) && overall_score=100
(( overall_score < 0 )) && overall_score=0

# ---------------------------------------------------------------------------
# Generate actionable items (sorted by impact)
# ---------------------------------------------------------------------------
declare -a actions=()
uncovered=$(( total_skills - eval_count ))
(( uncovered > 0 )) && actions+=("Generate evals for ${uncovered} uncovered skills")
(( dead_skills > 0 )) && actions+=("Investigate ${dead_skills} dead skills for retirement")
(( broken_file_paths_count > 0 )) && actions+=("Fix ${broken_file_paths_count} broken file path references")
(( eval_fail > 0 )) && actions+=("Fix ${eval_fail} failing eval checks")
(( desc_violations > 0 )) && actions+=("Fix ${desc_violations} description violations")
(( oversized_count > 0 )) && actions+=("Split ${oversized_count} oversized skills")

# ---------------------------------------------------------------------------
# Write JSON report
# ---------------------------------------------------------------------------
uv run --no-project python -c "
import json, sys
data = {
    'date': '$TODAY',
    'overall_score': $overall_score,
    'total_skills': $total_skills,
    'components': {
        'eval_coverage': {
            'score': $eval_coverage_score,
            'weight': 25,
            'detail': '$eval_coverage_detail',
            'evals_count': $eval_count,
            'total_skills': $total_skills
        },
        'eval_pass_rate': {
            'score': $eval_pass_score,
            'weight': 25,
            'detail': '$eval_pass_detail',
            'pass': $eval_pass,
            'fail': $eval_fail,
            'total_checks': $eval_total
        },
        'reference_health': {
            'score': $ref_health_score,
            'weight': 20,
            'detail': '$ref_health_detail',
            'broken_refs': $broken_file_paths_count
        },
        'usage_health': {
            'score': $usage_health_score,
            'weight': 15,
            'detail': '$usage_health_detail',
            'dead_skills': $dead_skills,
            'total_skills': $usage_total
        },
        'description_qa': {
            'score': $desc_score,
            'weight': 10,
            'detail': '$desc_detail',
            'violations': $desc_violations
        },
        'size_compliance': {
            'score': $size_score,
            'weight': 5,
            'detail': '$size_detail',
            'oversized': $oversized_count
        }
    },
    'actions': $(printf '%s\n' "${actions[@]}" | uv run --no-project python -c "import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '[]')
}
with open('$OUTPUT_JSON', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
print('JSON written to $OUTPUT_JSON', file=sys.stderr)
" 2>&1 || echo "WARNING: failed to write JSON report"

# ---------------------------------------------------------------------------
# Print formatted dashboard
# ---------------------------------------------------------------------------
if [[ "$QUIET" == "false" ]]; then
  printf '\n'
  printf '══════════════════════════════════════════════\n'
  printf 'SKILL HEALTH DASHBOARD — %s\n' "$TODAY"
  printf '══════════════════════════════════════════════\n'
  printf 'Overall Score: %d/100\n' "$overall_score"
  printf '\n'
  printf 'Component Scores:\n'
  printf '  Eval Coverage:    %3d/100 (wt 25)  — %s\n' "$eval_coverage_score" "$eval_coverage_detail"
  printf '  Eval Pass Rate:   %3d/100 (wt 25)  — %s\n' "$eval_pass_score" "$eval_pass_detail"
  printf '  Reference Health: %3d/100 (wt 20)  — %s\n' "$ref_health_score" "$ref_health_detail"
  printf '  Usage Health:     %3d/100 (wt 15)  — %s\n' "$usage_health_score" "$usage_health_detail"
  printf '  Description QA:   %3d/100 (wt 10)  — %s\n' "$desc_score" "$desc_detail"
  printf '  Size Compliance:  %3d/100 (wt  5)  — %s\n' "$size_score" "$size_detail"
  printf '\n'

  if (( ${#actions[@]} > 0 )); then
    printf 'Top-%d Actionable Items:\n' "${#actions[@]}"
    for i in "${!actions[@]}"; do
      printf '  %d. %s\n' "$(( i + 1 ))" "${actions[$i]}"
    done
  else
    printf 'No actionable items — all clear!\n'
  fi

  printf '══════════════════════════════════════════════\n'
  printf '\n'
fi
