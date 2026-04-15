# Skills Audit — Post-Approval Prompt Pack

> Generated: 2026-04-15
> Execution order: #2282 (policy) then #2281 (implementation)
> Constraint: do NOT execute until all preconditions are met

---

## 0. GATE: Plan-Approval Required

| Issue | Title | Current Status | Required Before Execution |
|---|---|---|---|
| #2280 | weekly skill ecosystem audit + consolidation maintenance loop | OPEN, draft, **NOT plan-approved** | `status:plan-approved` label |
| #2282 | lock classification and ranking policy for weekly skills audit | OPEN, draft, **NOT plan-approved** | `status:plan-approved` label |
| #2281 | implement v1 weekly audit for existing skills-curation workflow | OPEN, draft, **NOT plan-approved** | `status:plan-approved` label |

**DO NOT launch any tmux session below until all three issues carry `status:plan-approved`.**

---

## 1. Preconditions Checklist

Run these checks interactively before launching either session:

```bash
# 1a. Confirm plan-approved labels exist on all three issues
gh issue view 2280 --json labels --jq '[.labels[].name] | if any(. == "status:plan-approved") then "OK: #2280 approved" else "BLOCKED: #2280 not approved" end'
gh issue view 2282 --json labels --jq '[.labels[].name] | if any(. == "status:plan-approved") then "OK: #2282 approved" else "BLOCKED: #2282 not approved" end'
gh issue view 2281 --json labels --jq '[.labels[].name] | if any(. == "status:plan-approved") then "OK: #2281 approved" else "BLOCKED: #2281 not approved" end'

# 1b. Confirm plan files are present and not stale
ls -la docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md
ls -la docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md

# 1c. Confirm existing infrastructure is intact
test -f scripts/skills/detect_duplicate_skills.py && echo "OK: duplicate detector" || echo "MISSING"
test -f scripts/cron/skills-curation.sh && echo "OK: cron wrapper" || echo "MISSING"
test -f config/scheduled-tasks/schedule-tasks.yaml && echo "OK: schedule config" || echo "MISSING"
test -f tests/skills/test_skill_name_canonicalization.py && echo "OK: canonical-name tests" || echo "MISSING"

# 1d. Confirm no conflicting branches
git branch --list '*2282*' '*2281*' '*skills-audit*'

# 1e. Clean working tree (no uncommitted changes in target paths)
git status --short -- scripts/skills/ scripts/cron/skills-curation.sh config/skills/ config/scheduled-tasks/ tests/skills/ tests/cron/test_skills_curation.py docs/standards/
```

All checks must pass before proceeding.

---

## 2. Execute #2282 — Policy Layer (First)

### 2a. tmux launch command

```bash
tmux new-session -s skills-2282-policy \
  "cd /mnt/local-analysis/workspace-hub && claude --dangerously-skip-permissions"
```

### 2b. First prompt to paste

Copy and paste this entire block into the interactive Claude session:

```
Implement issue #2282: lock classification and ranking policy for weekly skills audit.

Plan file: docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md
Status: plan-approved (confirmed).

Deliverable: a checked-in policy contract consumed by #2281.

Files to create:
1. config/skills/weekly-audit-policy.yaml — canonical machine-readable policy (authoritative)
2. docs/standards/weekly-skills-audit-policy.md — explanatory companion (subordinate to YAML)
3. tests/skills/test_weekly_skills_audit_policy.py — fixture-backed tests for all 14 TDD cases in the plan

Policy must define:
- Classification buckets: exact-duplicate, canonical-wrapper-pair, adjacent-specialization, generic-leaf-collision, needs-human-review
- Precedence rules when multiple buckets match (exactly one winner)
- Severity rubric (high/medium/low) with explicit criteria
- Confidence rubric (high/medium/low) with explicit criteria
- Carry-forward rules for unchanged, changed, suppressed, resolved findings
- Escalation thresholds for follow-up issue creation (idempotent)
- Minimum finding schema: finding_key, classification, severity, confidence, canonical_names, paths, summary, recommended_action, escalation_state, is_new, is_changed
- Minimum weekly summary sections: new, changed, unresolved high-confidence, suppressed/carry-forward, operational errors
- Fixture examples for each bucket

Constraints:
- Ambiguous cases must route to needs-human-review, never ad hoc guessing
- Optimize for low-noise repeatable weekly output
- Do NOT create implementation code for the weekly audit script (#2281)
- Do NOT modify scripts/skills/detect_duplicate_skills.py or scripts/skills/skill-usage-report.py
- Use TDD: write tests first, then implement policy files to make them pass
- Run: uv run pytest tests/skills/test_weekly_skills_audit_policy.py -v
- Update docs/plans/README.md with the plan index row
- Commit on a branch: feat/2282-weekly-audit-policy
- Post a comment on GitHub issue #2282 summarizing what was delivered
```

### 2c. Validation checklist for #2282 completion

Run these after the session completes:

```bash
# Policy file exists and is non-empty
test -s config/skills/weekly-audit-policy.yaml && echo "PASS: policy YAML" || echo "FAIL"

# Explanatory doc exists
test -s docs/standards/weekly-skills-audit-policy.md && echo "PASS: policy doc" || echo "FAIL"

# Policy tests exist and pass
uv run pytest tests/skills/test_weekly_skills_audit_policy.py -v

# Verify all 5 classification buckets are defined in policy
for bucket in exact-duplicate canonical-wrapper-pair adjacent-specialization generic-leaf-collision needs-human-review; do
  grep -q "$bucket" config/skills/weekly-audit-policy.yaml && echo "PASS: $bucket" || echo "FAIL: $bucket missing"
done

# Verify finding schema fields present
for field in finding_key classification severity confidence canonical_names paths summary recommended_action escalation_state is_new is_changed; do
  grep -q "$field" config/skills/weekly-audit-policy.yaml && echo "PASS: $field" || echo "FAIL: $field missing"
done

# Verify precedence is defined
grep -q "precedence" config/skills/weekly-audit-policy.yaml && echo "PASS: precedence" || echo "FAIL: precedence missing"

# Canonical-name tests still pass (regression check)
uv run pytest tests/skills/test_skill_name_canonicalization.py -v

# Plan index updated
grep -q "2282" docs/plans/README.md && echo "PASS: plan index" || echo "FAIL: plan index"

# Branch exists with commits
git log --oneline feat/2282-weekly-audit-policy..HEAD 2>/dev/null || git log --oneline -3
```

---

## 3. Execute #2281 — Implementation (After #2282 Merges)

### 3a. Prerequisites before starting #2281

```bash
# Confirm #2282 branch is merged
git log --oneline main | head -5  # should contain #2282 commits

# Confirm policy file is on main
test -s config/skills/weekly-audit-policy.yaml && echo "PASS: policy available" || echo "BLOCKED: merge #2282 first"

# Pull latest main
git checkout main && git pull
```

### 3b. tmux launch command

```bash
tmux new-session -s skills-2281-impl \
  "cd /mnt/local-analysis/workspace-hub && claude --dangerously-skip-permissions"
```

### 3c. First prompt to paste

Copy and paste this entire block into the interactive Claude session:

```
Implement issue #2281: v1 weekly audit for existing skills-curation workflow.

Plan file: docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md
Policy contract: config/skills/weekly-audit-policy.yaml (from #2282, already merged)
Status: plan-approved (confirmed).

Deliverable: deterministic, read-only weekly skills-curation audit with stable JSON + Markdown + cron-log output.

Files to create:
1. scripts/skills/weekly_skills_audit.py — deterministic audit entrypoint
2. tests/skills/test_weekly_skills_audit.py — 15 TDD tests per plan test list
3. config/skills/weekly-audit-waivers.yaml — empty initial suppression registry

Files to modify:
4. scripts/cron/skills-curation.sh — convert from Claude-prompt launcher to deterministic-script wrapper
5. config/scheduled-tasks/schedule-tasks.yaml — update skills-curation entry: set is_claude_task to false, update requires/command/description
6. tests/cron/test_skills_curation.py — fix wrapper contract (currently 2/2 red, must turn green)
7. docs/ops/scheduled-tasks.md — document deterministic workflow and output paths
8. docs/plans/README.md — add plan index row

Implementation rules:
- Consume policy from config/skills/weekly-audit-policy.yaml (do not redefine buckets)
- Use frontmatter name as canonical skill identifier
- Exclude _archive and _diverged from audit scope
- Bucket _core and _internal findings separately (informational-only, not in main ranked findings)
- V1 is strictly read-only: no auto-rename, no auto-archive, no auto-issue creation
- Support --output-root CLI flag for TDD/manual runs to redirect output to temp dirs
- JSON output: logs/maintenance/skills-curation/YYYY-MM-DD.json
- Markdown output: logs/maintenance/skills-curation/YYYY-MM-DD.md
- Exit 0 on successful audit even when findings exist

Do NOT modify:
- scripts/skills/detect_duplicate_skills.py (compose as library, do not fork)
- scripts/skills/skill-usage-report.py (compose for usage signals, do not fork)
- tests/skills/test_skill_name_canonicalization.py (preserve existing contract)
- .claude/skills/** (audit target, read-only)
- scripts/cron/setup-cron.sh, scripts/cron/validate-schedule.py (should not need changes)

Use TDD: write tests first, then implement to make them pass.
Run all validation after implementation:
  uv run pytest tests/skills/test_weekly_skills_audit.py -v
  uv run pytest tests/cron/test_skills_curation.py -v
  uv run pytest tests/skills/test_skill_name_canonicalization.py -v
  uv run --no-project python scripts/cron/validate-schedule.py
  bash scripts/cron/setup-cron.sh --dry-run
  uv run --no-project python scripts/skills/weekly_skills_audit.py --output-root /tmp/skills-audit-test

Commit on a branch: feat/2281-weekly-skills-audit-v1
Post a comment on GitHub issue #2281 summarizing what was delivered.
```

### 3d. Validation checklist for #2281 completion

Run these after the session completes:

```bash
# --- Core deliverables exist ---
test -s scripts/skills/weekly_skills_audit.py && echo "PASS: audit script" || echo "FAIL"
test -s tests/skills/test_weekly_skills_audit.py && echo "PASS: audit tests" || echo "FAIL"
test -f config/skills/weekly-audit-waivers.yaml && echo "PASS: waiver registry" || echo "FAIL"

# --- All test suites pass ---
uv run pytest tests/skills/test_weekly_skills_audit.py -v
uv run pytest tests/cron/test_skills_curation.py -v
uv run pytest tests/skills/test_skill_name_canonicalization.py -v
uv run pytest tests/skills/test_weekly_skills_audit_policy.py -v

# --- Schedule integrity ---
uv run --no-project python scripts/cron/validate-schedule.py
bash scripts/cron/setup-cron.sh --dry-run

# --- Manual dry run produces artifacts ---
rm -rf /tmp/skills-audit-test
uv run --no-project python scripts/skills/weekly_skills_audit.py --output-root /tmp/skills-audit-test
test -s /tmp/skills-audit-test/*.json && echo "PASS: JSON artifact" || echo "FAIL"
test -s /tmp/skills-audit-test/*.md && echo "PASS: Markdown artifact" || echo "FAIL"

# --- Wrapper dry-run works ---
bash scripts/cron/skills-curation.sh --dry-run

# --- Scheduler metadata updated ---
grep -A5 "skills-curation" config/scheduled-tasks/schedule-tasks.yaml | grep -q "is_claude_task: false" && echo "PASS: is_claude_task flipped" || echo "FAIL"

# --- V1 is read-only (no mutations outside artifact paths) ---
git diff --name-only | grep -v "^logs/" | grep -v "^docs/" | grep -v "^scripts/" | grep -v "^config/" | grep -v "^tests/" && echo "WARN: unexpected changes" || echo "PASS: clean scope"

# --- Plan index updated ---
grep -q "2281" docs/plans/README.md && echo "PASS: plan index" || echo "FAIL"

# --- Branch exists ---
git log --oneline -5
```

---

## 4. Reminder: Approval Gate is Mandatory

**None of these issues are plan-approved as of 2026-04-15.**

The planning workflow requires:
1. Plans pass adversarial review (both #2282 and #2281 currently FAIL)
2. Plans receive `status:plan-review` label
3. User reviews and applies `status:plan-approved` label
4. Only then may implementation begin

Do not self-approve. Do not skip adversarial review. Do not implement draft plans.

---

*Source plans: `docs/plans/2026-04-14-issue-2282-*.md`, `docs/plans/2026-04-14-issue-2281-*.md`*
*Execution prep: `docs/reports/2026-04-15-skills-audit-execution-prep.md`*
