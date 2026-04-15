# Skills Audit Execution Prep — 2026-04-15

> Operator-ready packet for #2280, #2281, #2282
> Constraint: read-only preparation; no code changes until `status:plan-approved`

---

## 1. Current Status Snapshot

| Issue | Title | Plan Status | Label `status:plan-approved`? | Adversarial Review | Blocker |
|---|---|---|---|---|---|
| #2280 | weekly skill ecosystem audit + consolidation maintenance loop | `draft` | **NO** | Claude: MAJOR, Codex: MAJOR, Gemini: UNAVAIL | umbrella — children depend on this |
| #2281 | implement v1 weekly audit for skills-curation workflow | `draft` | **NO** | Claude: MAJOR, Codex: MAJOR, Gemini: UNAVAIL | classification policy deferred to #2282 |
| #2282 | lock classification and ranking policy for weekly skills audit | `draft` | **NO** | pending (not yet run) | must complete review before #2281 can finalize buckets |

**Key observation:** All three plans are `draft`. None have `status:plan-approved`. #2282 has not even completed adversarial review yet.

### Existing weekly run state
- Scheduler: `skills-curation` task exists in `config/scheduled-tasks/schedule-tasks.yaml` (line 175), Monday 04:00, `is_claude_task: true`.
- Wrapper: `scripts/cron/skills-curation.sh` — thin Claude prompt launcher (no deterministic logic).
- Latest log: `logs/maintenance/skills-curation-20260413.log` (56 lines, prose output from Claude).
- Test suite: `tests/cron/test_skills_curation.py` — **2/2 FAILING** (wrapper drift: tests expect `--print` flag, wrapper uses `exec`).

---

## 2. Implementation-Ready File Ownership Map — #2281

| Action | Path | Owner | Notes |
|---|---|---|---|
| **Create** | `scripts/skills/weekly_skills_audit.py` | #2281 | New deterministic audit entrypoint; consumes `detect_duplicate_skills.py` logic |
| **Modify** | `scripts/cron/skills-curation.sh` | #2281 | Convert from Claude-prompt launcher to deterministic-script wrapper |
| **Modify** | `config/scheduled-tasks/schedule-tasks.yaml` | #2281 | Update `is_claude_task`, `requires`, `command`, `description` for the `skills-curation` entry |
| **Modify** | `docs/ops/scheduled-tasks.md` | #2281 | Document deterministic workflow + output paths |
| **Modify** | `tests/cron/test_skills_curation.py` | #2281 | Fix or deliberately evolve wrapper contract (currently 2/2 red) |
| **Create** | `tests/skills/test_weekly_skills_audit.py` | #2281 | 15 TDD tests covering classification, scope, schema, delta, waivers |
| **Update** | `docs/plans/README.md` | #2281 | Add plan index row |

### Read-only inputs (do not modify)
| Path | Role |
|---|---|
| `scripts/skills/detect_duplicate_skills.py` | Compose as library — duplicate + leaf-collision detection |
| `scripts/skills/skill-usage-report.py` | Compose for staleness/usage signals |
| `tests/skills/test_skill_name_canonicalization.py` | Existing canonical-name test contract — preserve |

### New paths to create (do not exist yet)
| Path | Purpose |
|---|---|
| `config/skills/weekly-audit-waivers.yaml` | Suppression/waiver registry for accepted patterns |
| `logs/maintenance/skills-curation/YYYY-MM-DD.json` | JSON artifact output directory |
| `logs/maintenance/skills-curation/YYYY-MM-DD.md` | Markdown summary output directory |

---

## 3. Policy-File Ownership Map — #2282

| Action | Path | Owner | Notes |
|---|---|---|---|
| **Create** | `docs/standards/weekly-skills-audit-policy.md` or `config/skills/weekly-audit-policy.yaml` | #2282 | Checked-in policy contract (format TBD in plan review) |
| **Create** | `tests/skills/test_weekly_skills_audit_policy.py` | #2282 | 8 fixture-backed policy tests |
| **Update** | `docs/plans/README.md` | #2282 | Add plan index row |

### Policy defines (consumed by #2281 implementation)
- Classification buckets: `exact-duplicate`, `canonical-wrapper-pair`, `near-duplicate-same-intent`, `adjacent-specialization`, `generic-leaf-collision`, `stale-superseded`, `needs-human-review`
- Severity rubric: criteria for high/medium/low
- Confidence rubric: criteria for high/medium/low
- Carry-forward rules: how unchanged findings stay compact
- Escalation thresholds: when findings become follow-up issues
- Boundary-case decision table: wrapper vs near-duplicate vs adjacent-specialization

---

## 4. Ordered Execution Sequence (Post-Approval)

```
Step 0: Prerequisites
  [x] Confirm #2280 plan-approved (umbrella governance)
  [ ] Complete #2282 adversarial review
  [ ] Confirm #2282 plan-approved (policy layer)
  [ ] Confirm #2281 plan-approved (implementation)

Step 1: Implement #2282 — Policy Layer
  - Create policy document/schema
  - Create policy test fixtures
  - Validate: uv run pytest tests/skills/test_weekly_skills_audit_policy.py -v
  - Commit + PR

Step 2: Implement #2281 — Deterministic Audit
  - Create scripts/skills/weekly_skills_audit.py (consuming #2282 policy)
  - Update scripts/cron/skills-curation.sh wrapper
  - Update config/scheduled-tasks/schedule-tasks.yaml
  - Create config/skills/weekly-audit-waivers.yaml (empty initial)
  - Create tests/skills/test_weekly_skills_audit.py (15 TDD tests)
  - Fix tests/cron/test_skills_curation.py (currently 2/2 red)
  - Update docs/ops/scheduled-tasks.md
  - Validate all (see section 6)
  - Commit + PR

Step 3: Operational Validation
  - Manual dry run of full weekly audit
  - Verify JSON + Markdown artifacts generated correctly
  - Wait for next Monday 04:00 cron execution
  - Review first automated output
```

---

## 5. Explicit Do-Not-Touch List

These files/paths must NOT be modified during #2281/#2282 implementation:

| Path | Reason |
|---|---|
| `scripts/skills/detect_duplicate_skills.py` | Read-only input; compose, do not fork |
| `scripts/skills/skill-usage-report.py` | Read-only input; compose, do not fork |
| `tests/skills/test_skill_name_canonicalization.py` | Existing contract; preserve, do not break |
| `.claude/skills/**` | Audit target; read-only in v1 |
| `_archive/`, `_diverged/` directories | Excluded from v1 scope by design |
| Any SKILL.md files | v1 is read-only — no auto-rename/archive/merge |
| Other `config/scheduled-tasks/` entries | Only touch the `skills-curation` entry |
| `scripts/cron/setup-cron.sh` | Installer; should not need changes |
| `scripts/cron/validate-schedule.py` | Validator; should not need changes |

---

## 6. Validation Commands During Implementation

```bash
# --- Schedule integrity ---
uv run --no-project python scripts/cron/validate-schedule.py
bash scripts/cron/setup-cron.sh --dry-run

# --- Wrapper tests (currently 2/2 red — must turn green) ---
uv run pytest tests/cron/test_skills_curation.py -v

# --- Canonical-name contract (must stay green) ---
uv run pytest tests/skills/test_skill_name_canonicalization.py -v

# --- New policy tests (#2282) ---
uv run pytest tests/skills/test_weekly_skills_audit_policy.py -v

# --- New audit tests (#2281) ---
uv run pytest tests/skills/test_weekly_skills_audit.py -v

# --- Manual dry run of deterministic audit ---
uv run --no-project python scripts/skills/weekly_skills_audit.py --output-root /tmp/skills-audit-test
ls /tmp/skills-audit-test/  # expect: YYYY-MM-DD.json, YYYY-MM-DD.md

# --- Duplicate detector still works standalone ---
uv run --no-project python scripts/skills/detect_duplicate_skills.py

# --- Full cron wrapper dry-run ---
bash scripts/cron/skills-curation.sh --dry-run
```

---

## 7. Risks / Blockers Checklist

| # | Risk / Blocker | Severity | Mitigation |
|---|---|---|---|
| 1 | **#2282 adversarial review not yet completed** | HIGH | Must finish review + approval before #2281 can finalize classification buckets |
| 2 | **All three plans still `draft`** — none plan-approved | HIGH | Follow planning workflow: review -> `status:plan-review` -> user approves -> `status:plan-approved` |
| 3 | Existing cron tests 2/2 red | MEDIUM | #2281 must fix wrapper contract; TDD should address this in first implementation step |
| 4 | Audit universe mismatch between `detect_duplicate_skills.py` and `skill-usage-report.py` | MEDIUM | #2281 must normalize exclusion policy; plan already flags this |
| 5 | No waiver/suppression file exists yet (`config/skills/weekly-audit-waivers.yaml`) | LOW | Create empty YAML as part of #2281; not blocking |
| 6 | Output directory `logs/maintenance/skills-curation/` (subdirectory for JSON/MD) does not exist | LOW | Script should create on first run |
| 7 | Gemini adversarial review returned 429 for #2280/#2281 | LOW | Re-run Gemini review when capacity allows; Claude+Codex reviews are sufficient for approval gating |
| 8 | `is_claude_task: true` in schedule YAML must flip to `false` | LOW | Handled in #2281 scheduler YAML update |

---

## 8. Post-Approval Launch Template

### tmux session for #2282 (policy — execute first)

```bash
tmux new-session -s skills-audit-policy -d
tmux send-keys -t skills-audit-policy \
  'cd /mnt/local-analysis/workspace-hub && claude -p "Implement issue #2282 — lock classification and ranking policy for weekly skills audit. Plan: docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md. Follow the plan TDD test list. Create policy doc and tests. Do not touch implementation files for #2281." --dangerously-skip-permissions' Enter
```

### tmux session for #2281 (implementation — execute after #2282 merges)

```bash
tmux new-session -s skills-audit-impl -d
tmux send-keys -t skills-audit-impl \
  'cd /mnt/local-analysis/workspace-hub && claude -p "Implement issue #2281 — v1 weekly audit for skills-curation workflow. Plan: docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md. Policy: docs/standards/weekly-skills-audit-policy.md (from #2282). Follow the plan TDD test list. Existing cron tests are 2/2 red — fix the wrapper contract. Do-not-touch: detect_duplicate_skills.py, skill-usage-report.py, test_skill_name_canonicalization.py." --dangerously-skip-permissions' Enter
```

### Interactive Claude Code session (alternative)

```bash
cd /mnt/local-analysis/workspace-hub
claude
# Then paste:
# /gsd:execute-phase  (with issue number)
```

---

*Generated: 2026-04-15 | Constraints: approval-safe, read-only prep only*
