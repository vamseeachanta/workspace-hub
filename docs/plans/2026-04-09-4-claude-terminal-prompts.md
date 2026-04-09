# 4 Claude terminals — execution pack and run learnings (2026-04-09)

Repo root: /mnt/local-analysis/workspace-hub
Goal: preserve the 2026-04-09 four-terminal execution pack, record actual outcomes, and define safe relaunch commands for remaining work without same-file overlap.

Important workflow note:
- No open GH issues currently carry the `status:plan-approved` label.
- Treat this as an execution/audit pack derived from already-identified workstreams.
- For strict AGENTS.md compliance before new implementation, update issue plan-status labels first.

## Terminal map

| Terminal | Workstream | Issue(s) | Prompt file |
|---|---|---:|---|
| T1 | SubseaIQ -> field-development benchmark bridge | #1861 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md` |
| T2 | Field-development economics facade | #1858 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md` |
| T3 | Naval-architecture vessel/hull integration | #1859 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md` |
| T4 | Workflow governance + rolling queue hardening | #1839, #1857 | `docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md` |

## Observed run status (actual)

| Terminal | Actual outcome | Relaunch policy |
|---|---|---|
| T1 | First-pass benchmark scaffold already existed; rerun correctly detected missing delta = 0 | Do not relaunch for fresh implementation. Use only for audit or bounded follow-up delta. |
| T2 | Current economics facade exists in `digitalmodel` with passing tests, but the launched run produced no useful artifact | Main relaunch target. Use hardened command + explicit startup/blocker artifact requirements. |
| T3 | First-pass vessel/hull integration already existed; rerun verified tests and posted issue summary | Do not relaunch for fresh implementation. Use only for audit or bounded follow-up delta. |
| T4 | Analysis succeeded, but implementation was blocked by Claude write-permission behavior | Relaunch only with explicit unattended write mode enabled, or use analysis-only mode. |

## Concrete unfinished work by issue

1. #1857
   - Core queue system exists and tests pass.
   - Remaining delta is parity hardening: richer generated sections (focus/dependencies/overnight prompts) and related refresh polish.
2. #1839
   - Governance scaffolding exists and tests pass.
   - Remaining delta is runtime enforcement/hook integration, not just verifier scaffolding.
3. #1858
   - Economics facade exists and tests pass in `digitalmodel`.
   - Remaining delta is missing integration into broader field-development workflow and any follow-up regression hardening.
4. #1861
   - Benchmark bridge scaffold exists and tests pass.
   - Remaining delta is beyond scaffold scope; do not re-run unless auditing or addressing a concrete follow-up.
5. #1859
   - Vessel/hull adapter slice exists and tests largely pass.
   - Remaining delta is follow-up scope plus at least one order-dependent registry/test-sensitivity issue.

## Git contention map

T1 writes only:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`
- `worldenergydata/subseaiq/analytics/` (new files only)

T2 writes only:
- `digitalmodel/src/digitalmodel/field_development/economics.py`
- `digitalmodel/src/digitalmodel/field_development/__init__.py`
- `digitalmodel/tests/field_development/test_economics.py`
- optionally `digitalmodel/src/digitalmodel/field_development/workflow.py` if that file is created and no other stream is active there

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

## Hardened unattended launch pattern

Observed facts from live testing:
1. `claude -p` in non-interactive mode may emit a 3-second stdin warning if stdin is not closed.
2. Default/auto permission handling was not reliable for unattended write tasks here.
3. `--permission-mode acceptEdits` was the tested unattended mode that actually allowed writes.
4. If you close stdin with `</dev/null`, the prompt must be passed as an argument, not piped on stdin.

Recommended pattern for trusted workspace automation:

```bash
PROMPT_FILE="docs/plans/overnight-prompts/2026-04-09-4claude/terminal-N-...md"
LOG="logs/claude-terminal-N-$(date +%Y%m%d-%H%M%S).log"
PROMPT=$(< "$PROMPT_FILE")
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee "$LOG"
```

Use `--permission-mode plan` instead of `acceptEdits` for read-only smoke tests.
Do not use `--dangerously-skip-permissions` unless explicitly approved.

## Relaunch commands

Preferred relaunch target 1 — T2:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/claude-terminal-2-rerun.log
```

Preferred relaunch target 2 — T4:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/claude-terminal-4-rerun.log
```

Optional audit-only relaunch — T1:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md)
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee logs/claude-terminal-1-audit.log
```

Optional audit-only relaunch — T3:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md)
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee logs/claude-terminal-3-audit.log
```

## What actually happened in the 2026-04-09 run

From T1:
- implementation slice was already present
- rerun detected no missing delta and exited cleanly

From T2:
- no reliable execution artifact from the launched run
- economics facade work appears already partially implemented in `digitalmodel`
- treat as incomplete stream requiring hardened relaunch and blocker capture

From T3:
- implementation slice was already present
- rerun verified the existing work and posted issue summary

From T4:
- analysis and issue commenting succeeded
- implementation was blocked by unattended permission handling
- preserve this as analysis-only outcome, not completed implementation

## Next relaunch priority

1. T2 implementation relaunch
2. T4 implementation relaunch after confirming unattended write mode
3. T3 audit only if addressing order-dependent registry/test sensitivity
4. T1 only if a new benchmark follow-up defect is identified
