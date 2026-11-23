# Claude agent-team prompt: session-log portability commit-only implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Scope Verifier
3. Git Integrator
4. Adversarial Reviewer

Do not ask the user any questions.

Objective:
Take the already-prepared session-log portability changes, verify they are correctly scoped, and commit/push ONLY the intended files.

Current intended implementation artifacts:
- `docs/reports/2026-04-11-session-log-portability-transfer.md`
- `logs/orchestrator/README.md`
- `.claude/memory/KNOWLEDGE.md`
- `.claude/memory/topics/session-log-portability.md`

Additional prompt artifact for this run:
- `docs/plans/2026-04-11-file-based-claude-bash-agent-teams-prompt-session-log-portability-commit.md`

Critical constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT modify, stage, commit, or push unrelated files.
- Do NOT touch `.claude/state/**`.
- Do NOT touch `.claude/skills/**`.
- Do NOT touch `docs/handoffs/**`.
- Do NOT touch any other `docs/plans/**` file except this prompt if absolutely needed (normally read-only).
- Never use `git add .` or broad globs.

Allowed write/stage paths for this run only:
- `docs/reports/2026-04-11-session-log-portability-transfer.md`
- `logs/orchestrator/README.md`
- `.claude/memory/KNOWLEDGE.md`
- `.claude/memory/topics/session-log-portability.md`

Read-only context:
- `docs/plans/2026-04-11-file-based-claude-bash-agent-teams-prompt-session-log-portability.md`
- `docs/reports/2026-04-11-session-log-portability-transfer.md`
- `logs/orchestrator/README.md`
- `.claude/memory/KNOWLEDGE.md`
- `.claude/memory/topics/session-log-portability.md`
- `git status --short`
- `git diff -- <intended paths>`

Success condition:
Create one clean commit containing ONLY the four intended portability-transfer files, push it to `origin main`, and leave unrelated working-tree changes untouched.

Required execution steps:

STEP 1 — Verify scope
- Run `git status --short`.
- Confirm the four intended paths exist and contain the expected portability-transfer work.
- Confirm no out-of-scope file is staged.
- If any intended file is missing or obviously malformed, stop and report clearly instead of guessing.

STEP 2 — Review the exact diff
- Inspect `git diff --` for ONLY the four intended files.
- Verify the changes match the portability-transfer objective:
  - README documents Hermes artifacts and export-before-audit ordering.
  - KNOWLEDGE has a concise session-log rule section.
  - Topic file contains detailed operational guidance.
  - Report explains sources, promoted learnings, and residual local-only observations.

STEP 3 — Commit only intended files
- Stage only these four paths explicitly by exact path.
- Commit message:
  - `docs(memory): transfer durable session-log learnings into repo ecosystem`

STEP 4 — Push
- Push to `origin main`.

STEP 5 — Final verification
- Confirm the commit contains only the four intended files.
- Confirm unrelated dirty/untracked files remain uncommitted.

Final response format in the Claude run:
1. Files verified
2. Exact files committed
3. Verification performed
4. Commit SHA
5. Push status
6. Any untouched unrelated files left in working tree
