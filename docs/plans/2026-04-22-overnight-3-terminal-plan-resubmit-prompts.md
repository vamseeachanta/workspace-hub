# Overnight 3-terminal plan-resubmit batch — #2443, #2444, #2289

Context
- Repo: `/mnt/local-analysis/workspace-hub`
- Mode: planning-only / plan-hardening only
- Reason: all three issues are still blocked at adversarial plan review; no implementation work is authorized
- Current status: Hermes is actively executing #2443 plan revision in the current terminal

Live issue map
| Issue | Title | Terminal | Mode |
|---|---|---|---|
| #2443 | achantas-data markdown-lint + link-check CI | T1 / current terminal | plan revision + README row sync |
| #2444 | aceengineer-admin minimal CI | T2 | plan revision only |
| #2289 | bypass rollback / recovery policy contract | T3 | plan revision only |

Git contention avoidance map
- Terminal 1 writes:
  - `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`
  - `docs/plans/README.md` (only the #2443 row)
- Terminal 2 writes:
  - `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
  - optional issue-specific scratch under `.planning/quick/2444-*`
- Terminal 3 writes:
  - `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
  - optional issue-specific scratch under `.planning/quick/2289-*`
- Zero intentional overlap except `docs/plans/README.md`, which is owned ONLY by Terminal 1 in this wave.

Negative write boundaries
- T1 must not edit `2444` or `2289` plan files.
- T2 must not edit `docs/plans/README.md`, `2443`, or `2289` plan files.
- T3 must not edit `docs/plans/README.md`, `2443`, or `2444` plan files.
- No terminal may modify source code, tests, workflow files in external repos, labels, approval markers, or plan-approved state.

Operator launch notes
- Use Claude-only if preserving Codex credits.
- Prompts are self-contained and planning-safe.
- Because the workspace already has unrelated dirty files, each terminal should verify and touch ONLY its owned paths.
- Do not commit unrelated existing dirt.

Suggested launch pattern
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-2-issue-2444.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/claude-terminal-2-2444.log
```

What you should have by morning
- From Terminal 1:
  - revised #2443 plan artifact
  - synced #2443 README row
  - ready-to-rerun checklist for Wave 3 review
- From Terminal 2:
  - revised #2444 plan artifact with resolved `uv.lock` / trigger / TDD contradictions
  - issue-ready summary of remaining review commands to dispatch
- From Terminal 3:
  - revised #2289 canonical plan with missing-section / mechanism-selection / README-row blocker closed in plan text
  - issue-ready summary of remaining review commands to dispatch

Success definition
- Each terminal produces a cleaner canonical plan with blocker-specific revisions only
- No terminal changes live approval state
- No terminal performs implementation in target child repos
- Each plan should be closer to a fresh adversarial re-review, not merely cosmetically edited
