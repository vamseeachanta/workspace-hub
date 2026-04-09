# Terminal 5 — Workflow Governance + Rolling Queue Hardening (Claude)

We are in /mnt/local-analysis/workspace-hub.
Use `uv run` for all Python.
Commit to `main` and push after each completed implementation/fix cycle.
Do not branch.
TDD first where code changes are made. Do NOT ask the user any questions.
Run `git pull origin main` before every push.

IMPORTANT: first inspect current state before coding.
1. Read issue bodies for #1839 and #1857.
2. Inspect current artifacts before changing them:
   - notes/agent-work-queue.md
   - scripts/refresh-agent-work-queue.sh
   - scripts/ai/review_routing_gate.py
   - scripts/ai/review-routing-gate.sh
   - docs/governance/ and docs/standards/ relevant workflow files
3. Narrow to the missing delta only.

Do NOT write to paths owned by other terminals:
- digitalmodel/src/digitalmodel/field_development/
- digitalmodel/tests/field_development/
- digitalmodel/src/digitalmodel/naval_architecture/
- digitalmodel/tests/naval_architecture/
- scripts/ai/credit-utilization-tracker.py
- scripts/ai/task-dispatcher.py
- scripts/ai/generate-agent-radar.py
- config/agents/
- config/ai-tools/
- scripts/cron/setup-cron.sh

Only write to:
- notes/agent-work-queue.md
- scripts/refresh-agent-work-queue.sh
- scripts/refresh-agent-work-queue.py
- scripts/workflow/
- tests/work-queue/
- docs/governance/
- docs/reports/session-governance/

## TASK 1: Issue #1857

Harden the rolling agent work queue so it is refreshable, reviewable, and less ad-hoc.

Minimum deliverables:
1. Improve the queue refresh path:
   - either strengthen `scripts/refresh-agent-work-queue.sh`
   - or add `scripts/refresh-agent-work-queue.py` and keep the shell wrapper thin
2. Ensure the generated queue remains deterministic and easy to audit.
3. Add/update at least one targeted test in `tests/work-queue/` covering queue generation behavior or formatting assumptions.
4. Update `notes/agent-work-queue.md` only if the refresh logic intentionally regenerates it.

Required verification:
- targeted pytest for touched test(s)
- one safe queue-refresh run if practical

Commit message:
`feat(queue): harden rolling agent work queue refresh path (#1857)`

## TASK 2: Issue #1839

Implement one bounded, auditable slice of workflow hard-stop governance.

Keep this scoped. Good first-pass options include:
- a session-governor scaffold under `scripts/workflow/` that models hard-stop checkpoints
- a governance doc and machine-readable config for hard-stop checkpoints
- a small verification utility that checks whether required gates are present in current workflow artifacts

Do NOT attempt a full orchestrator rewrite in this terminal.

Minimum deliverables:
1. One concrete governance artifact or utility under `scripts/workflow/`.
2. One targeted test if code is added.
3. One concise governance doc/report under `docs/governance/` or `docs/reports/session-governance/` explaining what was implemented and what remains.

Required verification:
- targeted pytest for touched test(s), if code was added
- one direct script invocation if applicable

Commit message:
`feat(workflow): add first-pass hard-stop governance scaffolding (#1839)`

## IMPLEMENTATION CROSS-REVIEW (mandatory)

This stream is architecture/policy-heavy. Run both Codex and Gemini review if Gemini CLI is available.

After each task commit is pushed:
1. Capture the committed diff:
   - `git show --stat --patch HEAD > /tmp/terminal-5-impl.diff`
2. Write `/tmp/terminal-5-review.md` with:
   - issue context (#1857 or #1839)
   - changed files
   - governance/operational risks
   - verification command/result
   - the exact diff
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-5-review.md)" | tee /tmp/terminal-5-codex-review.txt`
4. If available, run Gemini review:
   - `gemini exec "$(cat /tmp/terminal-5-review.md)" | tee /tmp/terminal-5-gemini-review.txt`
5. Fix MAJOR/HIGH findings once, commit, push, and rerun the reviewer(s) that found them.
6. Post brief issue comments on #1857 and/or #1839 with implementation summary, verification, and final review verdicts.

If Gemini CLI is unavailable, note that in the issue comment and proceed with Codex review only.
