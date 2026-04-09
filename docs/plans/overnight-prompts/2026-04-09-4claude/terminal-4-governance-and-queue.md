# Terminal 4 — workflow governance + rolling queue hardening

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first when code changes are made, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

First inspect current state:
1. Read GH issues #1857 and #1839.
2. Inspect:
   - `notes/agent-work-queue.md`
   - `scripts/refresh-agent-work-queue.sh`
   - `scripts/ai/review_routing_gate.py`
   - `scripts/ai/review-routing-gate.sh`
   - relevant files under `docs/governance/` and `docs/standards/`
3. Implement only the missing delta.

Do NOT write to:
- `digitalmodel/src/digitalmodel/field_development/`
- `digitalmodel/tests/field_development/`
- `digitalmodel/src/digitalmodel/naval_architecture/`
- `digitalmodel/tests/naval_architecture/`

Only write to:
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.sh`
- `scripts/refresh-agent-work-queue.py`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Task 1: issue #1857
Harden the rolling agent work queue so it is deterministic, refreshable, and auditable.

Minimum deliverables:
1. Strengthen `scripts/refresh-agent-work-queue.sh` or add `scripts/refresh-agent-work-queue.py` with a thin shell wrapper.
2. Add/update at least one targeted test under `tests/work-queue/`.
3. Update `notes/agent-work-queue.md` only if regeneration is part of the flow.

Task 2: issue #1839
Implement one bounded, auditable slice of workflow hard-stop governance.

Good options:
- a session-governor scaffold under `scripts/workflow/`
- a machine-readable hard-stop checkpoint config plus validation utility
- a small checker that verifies required gates exist in workflow artifacts

Minimum deliverables:
1. One concrete governance artifact or utility under `scripts/workflow/`.
2. One targeted test if code is added.
3. One concise doc/report under `docs/governance/` or `docs/reports/session-governance/` describing what was implemented and what remains.

Verification:
- targeted pytest for touched tests
- one direct refresh/script invocation if applicable

Commit messages:
- `feat(queue): harden rolling agent work queue refresh path (#1857)`
- `feat(workflow): add first-pass hard-stop governance scaffolding (#1839)`

Mandatory review after each push:
1. `git show --stat --patch HEAD > /tmp/terminal-4-impl.diff`
2. Write `/tmp/terminal-4-review.md` with issue context, changed files, governance/operational risks, verification result, and exact diff.
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-4-review.md)" | tee /tmp/terminal-4-codex-review.txt`
4. If Gemini CLI is available, run Gemini too:
   - `gemini exec "$(cat /tmp/terminal-4-review.md)" | tee /tmp/terminal-4-gemini-review.txt`
5. If reviewers find MAJOR/HIGH issues, fix once, commit, push, rerun only the reviewer(s) that found them.
6. Post brief GH issue comments on #1857 and/or #1839 with implementation summary, verification, and final verdicts.
