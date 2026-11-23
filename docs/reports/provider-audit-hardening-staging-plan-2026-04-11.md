# Provider audit hardening staging plan — 2026-04-11

Scope: current working tree in `workspace-hub` after provider-audit/export hardening and related planning-doc churn.

## Do not commit

Runtime/state artifacts that should stay out of commits:
- `.claude/state/corrections/.edit_sequence_counter`
- `.claude/state/corrections/.recent_edits`
- `.claude/state/session-signals/2026-04-11.jsonl`

## Recommended commit groups

### Commit 1
Title:
- fix(claude): persist session_id in raw session logger output

Files:
- `.claude/hooks/session-logger.sh`
- `tests/hooks/test_session_logger.py`

Why:
- Smallest functional change
- Directly improves future provider-audit fidelity
- Clean code+test pair

### Commit 2
Title:
- test(analysis): refresh provider audit artifacts and cover Claude runtime session counting

Files:
- `tests/analysis/test_provider_session_ecosystem_audit.py`
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Why:
- Keeps audit regression coverage and regenerated artifacts together
- Depends conceptually on session_id-bearing Claude logs existing going forward

## Separate unrelated workstreams currently in tree

These are not part of the provider-audit hardening thread and should be staged separately.

### Planning/ensemble migration work
Suggested title:
- fix(planning): remove stale ensemble-plan dependencies and refresh AI architecture docs

Files:
- `scripts/planning/ensemble-plan.sh`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`
- `docs/ops/legacy-claude-reference-map.md`

### Plan/backlog documentation updates
Suggested title:
- docs(plans): add new issue planning dossiers and update plan index

Files already tracked/index-like:
- `docs/plans/README.md`

New plan artifacts:
- `docs/plans/2026-04-10-top3-issue-assessment-dossiers.md`
- `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md`
- `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md`
- `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Note:
- `docs/plans/README.md` should ideally index all newly added plan docs before commit if you want that commit to be internally consistent.

## Minimal provider-audit-only staging commands

```bash
git add .claude/hooks/session-logger.sh tests/hooks/test_session_logger.py
git commit -m "fix(claude): persist session_id in raw session logger output"

git add tests/analysis/test_provider_session_ecosystem_audit.py \
  analysis/provider-session-ecosystem-audit.json \
  docs/reports/provider-session-ecosystem-audit.md
git commit -m "test(analysis): refresh provider audit artifacts and cover Claude runtime session counting"
```

## Current rationale

If your goal is to ship only the provider-audit ecosystem hardening work, stop after Commit 2.
The remaining modified/untracked files belong to a separate planning/docs stream and should not be mixed into the audit thread.
