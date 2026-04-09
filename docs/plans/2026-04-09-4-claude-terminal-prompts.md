# 4 Claude terminals — work plan (2026-04-09)

Repo root: /mnt/local-analysis/workspace-hub
Goal: 4 parallel Claude streams with zero same-file overlap and easy launch commands.
Note: no open GH issues currently carry the `status:plan-approved` label, so treat this as a prepared execution pack based on already-identified workstreams. If you want strict hard-stop compliance before implementation, update issue labels/plan status first.

## Terminal map

| Terminal | Workstream | Issue(s) | Prompt file |
|---|---|---:|---|
| T1 | SubseaIQ -> field-development benchmark bridge | #1861 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md` |
| T2 | Field-development economics facade | #1858 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md` |
| T3 | Naval-architecture vessel/hull integration | #1859 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md` |
| T4 | Workflow governance + rolling queue hardening | #1839, #1857 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md` |

## Git contention map

T1 writes only:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`
- `worldenergydata/subseaiq/analytics/` (new files only)

T2 writes only:
- `digitalmodel/src/digitalmodel/field_development/economics.py`
- `digitalmodel/src/digitalmodel/field_development/__init__.py`
- `digitalmodel/tests/field_development/test_economics.py`

T3 writes only:
- `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`
- `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py`
- `digitalmodel/src/digitalmodel/naval_architecture/integration.py`
- `digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py`
- `digitalmodel/tests/naval_architecture/`

T4 writes only:
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.sh`
- `scripts/refresh-agent-work-queue.py`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Review artifacts:
- `/tmp/terminal-1-*`
- `/tmp/terminal-2-*`
- `/tmp/terminal-3-*`
- `/tmp/terminal-4-*`

## Launch commands

Terminal 1:
`claude -p "Read docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md and execute it exactly."`

Terminal 2:
`claude -p "Read docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md and execute it exactly."`

Terminal 3:
`claude -p "Read docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md and execute it exactly."`

Terminal 4:
`claude -p "Read docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md and execute it exactly."`

## What you should have after the run

From T1:
- bounded benchmark bridge scaffold
- targeted tests for aggregation + missing fields
- Codex review verdict

From T2:
- bounded economics facade over worldenergydata adapters
- targeted tests for adapter delegation + bad inputs
- Codex review verdict

From T3:
- vessel-record -> principal-dimensions adapter wiring
- targeted naval architecture tests
- Codex review verdict, plus Gemini if available

From T4:
- hardened queue refresh path
- one bounded hard-stop governance utility/doc slice
- targeted tests/review verdicts
