# Overnight 5-Terminal Claude Batch — 2026-04-09

Generated: 2026-04-09 06:52 CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub
Operator note: sized for ~50% Claude quota remaining. Each terminal is a bounded 60-90 minute stream, not an all-night open-ended run.

## Terminal Allocation

| Terminal | Primary CLI | Workstream | Issues | Est. Time |
|----------|-------------|------------|--------|-----------|
| 1 | Claude | SubseaIQ → field-development benchmark bridge | #1861 | 60-90 min |
| 2 | Claude | Field-development economics facade wiring | #1858 | 60-90 min |
| 3 | Claude | Naval-architecture vessel/hull integration | #1859 | 60-90 min |
| 4 | Claude | Hermes routing + AI credit utilization tooling | #1855, #1856 | 75-90 min |
| 5 | Claude | Workflow hard-stops + rolling agent queue hardening | #1839, #1857 | 75-90 min |

## Mandatory Review Policy Included In Every Prompt

Every prompt now includes implementation cross-review:
- Claude implements with TDD
- Commit to main and push
- Run Codex adversarial review on the committed diff
- For architecture-heavy prompts, also run Gemini review if available
- Fix MAJOR/HIGH findings once, recommit, and rerun review
- Post a brief issue comment with implementation status + review verdict

## Git Contention Avoidance Map

Terminal 1 writes:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/tests/field_development/test_benchmarks.py
- worldenergydata/subseaiq/analytics/ (new analytics files only)

Terminal 2 writes:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_economics.py

Terminal 3 writes:
- digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
- digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py
- digitalmodel/src/digitalmodel/naval_architecture/integration.py
- digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py
- digitalmodel/tests/naval_architecture/

Terminal 4 writes:
- scripts/ai/credit-utilization-tracker.py
- scripts/ai/task-dispatcher.py
- scripts/ai/generate-agent-radar.py
- scripts/cron/setup-cron.sh
- config/agents/routing-config.yaml
- config/agents/provider-capabilities.yaml
- config/ai-tools/weekly-utilization.json
- notes/ai-credit-utilization-weekly.md

Terminal 5 writes:
- notes/agent-work-queue.md
- scripts/refresh-agent-work-queue.sh
- scripts/refresh-agent-work-queue.py
- scripts/workflow/
- tests/work-queue/
- docs/governance/
- docs/reports/session-governance/

Review artifacts:
- Use /tmp/terminal-N-review.* only. Do NOT write shared review files into the repo.

Zero same-file overlap is required.
If a prompt discovers the target file already satisfies the issue, it should narrow to the missing delta rather than rewrite.
Every terminal must run `git pull origin main` before every push.

## Prompt Files

- docs/plans/overnight-prompts/2026-04-09/terminal-1-subseaiq-benchmarks.md
- docs/plans/overnight-prompts/2026-04-09/terminal-2-field-dev-economics.md
- docs/plans/overnight-prompts/2026-04-09/terminal-3-naval-arch-vessel-integration.md
- docs/plans/overnight-prompts/2026-04-09/terminal-4-hermes-routing-and-usage.md
- docs/plans/overnight-prompts/2026-04-09/terminal-5-workflow-governance-and-queue.md

## Manual Launch Pattern

Example:
`claude -p "Read docs/plans/overnight-prompts/2026-04-09/terminal-1-subseaiq-benchmarks.md and execute it exactly."
`

Launch all 5 in separate terminals.

## Issue-to-Terminal Map

| Issue | Title | Terminal |
|------:|-------|----------|
| #1861 | SubseaIQ-to-field-development bridge | T1 |
| #1858 | worldenergydata FDAS + economics integration | T2 |
| #1859 | vessel fleet + hull models integration | T3 |
| #1855 | weekly AI credit utilization tracker | T4 |
| #1856 | Hermes quick model switching + dispatch | T4 |
| #1839 | workflow hard-stops + session governance | T5 |
| #1857 | rolling 1-week agent work queue | T5 |

## What You Should Have By Morning

From Terminal 1:
- benchmark bridge scaffold with tests
- initial SubseaIQ analytics output path wired
- Codex review verdict on the bridge

From Terminal 2:
- field-development economics facade with tests
- explicit worldenergydata integration points documented in code
- Codex review verdict on the facade

From Terminal 3:
- vessel/hull adapter wiring in naval_architecture with tests
- initial curves-of-form / principal-dimensions integration points
- Codex + optional Gemini review verdicts

From Terminal 4:
- tighter Hermes routing config
- utilization tracker extended or completed
- dispatcher/review artifacts and review verdicts

From Terminal 5:
- queue refresh hardening
- session-governance artifacts for hard-stops
- Codex + optional Gemini review verdicts
