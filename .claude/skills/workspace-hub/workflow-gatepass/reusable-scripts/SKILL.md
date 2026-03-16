---
name: workflow-gatepass-reusable-scripts
description: 'Sub-skill of workflow-gatepass: Reusable Scripts.'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# Reusable Scripts

## Reusable Scripts


| Script | Purpose |
|--------|---------|
| `scripts/work-queue/start_stage.py WRK-NNN N` | Build stage-N-prompt.md; route task_agent/human_interactive/chained_agent |
| `scripts/work-queue/exit_stage.py WRK-NNN N` | Validate stage exit artifacts + human gate; SystemExit(1) on failure |
| `scripts/work-queue/gate_check.py` | PreToolUse Write hook; blocks evidence writes if upstream gate not met |
| `scripts/work-queue/verify-gate-evidence.py WRK-NNN` | Check all gates pass before close (canonical authority) |
| `scripts/work-queue/parse-session-logs.sh WRK-NNN ...` | Read Claude/Codex/Gemini logs; emit session-log-review.md |
| `scripts/review/orchestrator-variation-check.sh --wrk WRK-NNN --orchestrator <provider> --scripts "..."` | Run scripts and emit variation-test-results.md |
| `scripts/work-queue/claim-item.sh WRK-NNN` | Atomic claim + stage-8 auto-progress |
| `scripts/work-queue/close-item.sh WRK-NNN --html-verification <path>` | Atomic close + stage-19 auto-progress + auto final HTML generation; `--html-verification` is required (WRK≥624) |
| `scripts/work-queue/archive-item.sh WRK-NNN` | Atomic archive + stage-20 auto-progress; exits non-zero if other queue items fail post-validation — archive still completes, confirm via `find .claude/work-queue/archive -name "WRK-NNN.md"` |

`parse-session-logs.sh` handles JSONL (Claude) and plain-text (Codex/Gemini) formats;
also checks native stores (`~/.codex/sessions/`, `~/.gemini/tmp/`).

`orchestrator-variation-check.sh` is provider-agnostic — set `--orchestrator` to
`claude`, `codex`, or `gemini`; the runner field in `variation-test-results.md`
reflects this value for cross-provider comparisons.
