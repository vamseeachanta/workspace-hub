# Exact staged commit sequence — 2026-04-11

This is the exact current-tree staging plan based on live `git status`.

## Current modified / untracked files in scope

Provider audit / session logging thread:
- `.claude/hooks/session-logger.sh`
- `tests/hooks/test_session_logger.py`
- `scripts/analysis/provider_session_ecosystem_audit.py`
- `scripts/permissions/audit-bash-commands.py`
- `scripts/bash_command_prefixes.py`
- `tests/test_bash_command_prefixes.py`
- `tests/analysis/test_provider_session_ecosystem_audit.py`
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Separate planning / docs thread:
- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- `scripts/planning/ensemble-plan.sh`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/ops/legacy-claude-reference-map.md`
- `docs/plans/README.md`
- `docs/plans/2026-04-10-top3-issue-assessment-dossiers.md`
- `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md`
- `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md`
- `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md`

Runtime/state files to skip:
- `.claude/state/corrections/.edit_sequence_counter`
- `.claude/state/corrections/.recent_edits`
- `.claude/state/session-signals/2026-04-11.jsonl`

## Recommended commit order

### Commit 1 — Claude logging parity

Purpose:
- Persist `session_id` into future raw Claude orchestrator log records
- Add direct hook-level regression coverage

Stage:
```bash
git add .claude/hooks/session-logger.sh \
  tests/hooks/test_session_logger.py
```

Commit:
```bash
git commit -m "fix(claude): persist session_id in raw session logger output"
```

### Commit 2 — Shared command-prefix helper + analysis reuse

Purpose:
- Remove duplicated Bash command-prefix logic
- Centralize cleanup/prefix extraction for audit tooling

Stage:
```bash
git add scripts/bash_command_prefixes.py \
  scripts/analysis/provider_session_ecosystem_audit.py \
  scripts/permissions/audit-bash-commands.py \
  tests/test_bash_command_prefixes.py
```

Commit:
```bash
git commit -m "refactor(analysis): share bash command-prefix normalization helpers"
```

### Commit 3 — Provider audit coverage + refreshed artifacts

Purpose:
- Expand provider-audit regression coverage
- Refresh machine-readable and markdown provider audit artifacts

Stage:
```bash
git add tests/analysis/test_provider_session_ecosystem_audit.py \
  analysis/provider-session-ecosystem-audit.json \
  docs/reports/provider-session-ecosystem-audit.md
```

Commit:
```bash
git commit -m "test(analysis): refresh provider audit artifacts and coverage"
```

## Optional separate planning/docs commits

These should not be mixed into the provider-audit thread unless you explicitly want a broader PR.

### Commit 4 — planning workflow / ensemble migration

Stage:
```bash
git add .claude/skills/coordination/issue-planning-mode/SKILL.md \
  scripts/planning/ensemble-plan.sh \
  docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md \
  docs/ops/legacy-claude-reference-map.md
```

Commit:
```bash
git commit -m "fix(planning): align ensemble planning workflow and architecture docs"
```

### Commit 5 — plan dossiers / governance notes

Stage:
```bash
git add docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md \
  docs/plans/README.md \
  docs/plans/2026-04-10-top3-issue-assessment-dossiers.md \
  docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md \
  docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md \
  docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md
```

Commit:
```bash
git commit -m "docs(plans): add April 11 planning dossiers and index updates"
```

## Skip / unstage safety commands

To ensure runtime artifacts never enter commits:
```bash
git restore --staged .claude/state/corrections/.edit_sequence_counter \
  .claude/state/corrections/.recent_edits \
  .claude/state/session-signals/2026-04-11.jsonl 2>/dev/null || true
```

If they become tracked accidentally in the index during interactive staging:
```bash
git reset HEAD .claude/state/corrections/.edit_sequence_counter \
  .claude/state/corrections/.recent_edits \
  .claude/state/session-signals/2026-04-11.jsonl
```

## Recommended minimal path

If you want the cleanest provider-audit-only branch/PR, stop after Commit 3.
That gives you:
- Claude future session-id parity
- shared command-prefix helper
- refreshed provider audit outputs and coverage

## Verification command before each commit

```bash
git diff --cached --stat
```

And before pushing the provider-audit thread:
```bash
uv run pytest tests/hooks/test_session_logger.py \
  tests/test_bash_command_prefixes.py \
  tests/analysis/test_provider_session_ecosystem_audit.py \
  tests/permissions/test_audit_bash_commands.py \
  tests/cron/test_hermes_session_export.py \
  tests/cron/test_codex_session_export.py \
  tests/cron/test_gemini_session_export.py
```
