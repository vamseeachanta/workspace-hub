# WRK-1053 Plan (Claude)

## Route B — Medium Complexity

### Phase 1: Create New Scripts

**`scripts/skills/audit-skill-violations.sh`**
- Scan `.claude/skills/**/*.md` for violations
- Checks (revised per cross-review):
  - README.md PRESENCE = violation (v2 anti-pattern — FLIP from original)
  - SKILL.md word count >5000 = violation
  - description field >1024 chars = violation (use `uv run --no-project python -c` or `yq` — not bare bash string ops)
  - XML/HTML tags in SKILL.md body = violation
- Output: YAML to stdout with schema `{violations: [{file, check, severity}]}`
- Exit: 0 = clean, 1 = violations found, 2 = usage/script error
- Tests: clean dir (exit 0), README.md present (exit 1 violation), oversized SKILL.md (exit 1)

**`scripts/skills/skill-coverage-audit.sh`**
- Map WRK category values → skill subdirs
- Score each skill: check frontmatter `scripts:` field AND exec patterns (`bash scripts/`, `uv run`, `bash .claude/skills/`)
- Output: YAML `{skills: [{path, has_script_ref, gaps: []}]}`; cron-safe (silent when clean)
- Exit: 0 = all wired, 1 = gaps found, 2 = usage error
- Tests: full coverage (exit 0), partial (gap found), empty dir (exit 2)

### Phase 2: Wire Existing Scripts

1. **resource-intelligence** — remove hub-root `scripts/validate-resource-pack.sh` alias (broken path); keep skill-local path only
2. **skill-eval** — add calls to `audit-skill-violations.sh` + `validate-skills.sh`
3. **comprehensive-learning Phase 9** — update BOTH:
   - `SKILL.md`: define Phase 9 referencing `identify-script-candidates.sh` + `skill-coverage-audit.sh`
   - `scripts/learning/comprehensive-learning.sh`: add Phase 9 invocation
   - `scripts/analysis/comprehensive_learning_pipeline.py`: replace placeholder Phase 9 with real call
4. ~~detect-drift.sh~~ — DROPPED (already runs in CL Phase 1b; duplication risk)
5. ~~queue-status.sh~~ — DROPPED (already documented in work-queue SKILL.md; low-value churn)

### Phase 3: TDD/Eval

- 3 bash tests per new script (happy path, violation, usage error)
- Grep-verify each updated SKILL.md + runtime script contains expected invocation
- Run `verify-gate-evidence.py WRK-1053`

### Acceptance Criteria Mapping (revised)

| AC | Phase |
|----|-------|
| audit-skill-violations.sh created — README presence, word count, description length, XML tags | 1 |
| skill-coverage-audit.sh created — frontmatter + exec pattern heuristic | 1 |
| skill-eval wired to audit-skill-violations.sh + validate-skills.sh | 2 |
| comprehensive-learning Phase 9 in SKILL.md + .sh + .py | 2 |
| resource-intelligence path fix | 2 |
| workflow-gatepass verify-gate-evidence.py explicit | already done — verify only |
| set -euo pipefail + exit 0/1/2 convention in new scripts | 1 |
| YAML output schema defined and stable | 1 |
| ≥3 tests per new script | 3 |
| No prose loop where script already covers it | 1+2 |
