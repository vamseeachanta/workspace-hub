# WRK-1265 Plan: Optimize Audit Shell Scripts

## Approach
1. TDD — write tests for each check type (readme, word count, description length, XML tags, coverage)
2. Implement `scripts/skills/audit-skills.py` with `audit_skill_lib.py`
3. Wire `ecosystem-eval-report.sh` to use new script
4. Deprecate old shell scripts

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-16T12:00:00Z
decision: passed
