# Terminal 4 — workflow governance + rolling queue hardening

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first when code changes are made, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

Status note:
- A prior run encountered permissions that limited the session to analysis instead of implementation.
- Preserve that read-only outcome in the audit trail.
- If write access is still unavailable, switch immediately to analysis-only mode instead of repeatedly attempting implementation.

First inspect current state:
1. Read GH issues #1857 and #1839.
2. Inspect:
   - `notes/agent-work-queue.md`
   - `scripts/refresh-agent-work-queue.sh`
   - `scripts/refresh-agent-work-queue.py`
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

Execution mode decision:
1. First, verify whether the allowed write paths are actually writable.
2. If writes succeed, proceed with the bounded implementation tasks below.
3. If writes are denied or the workspace is effectively read-only:
   - do not claim implementation completion
   - do not keep retrying failed writes
   - produce analysis-only patch guidance under `/tmp/terminal-4-analysis.md`
   - include exact files, exact proposed edits, and verification commands to run once write access is restored

Task 1: issue #1857 (implementation if writable, otherwise analysis-only patch plan)

Minimum deliverables:
1. Strengthen `scripts/refresh-agent-work-queue.sh` or `scripts/refresh-agent-work-queue.py` only for still-missing deterministic refresh/parity work.
2. Add/update at least one targeted test under `tests/work-queue/` if code changes are made.
3. Update `notes/agent-work-queue.md` only if regeneration is part of the flow.

Task 2: issue #1839 (implementation if writable, otherwise analysis-only patch plan)

Minimum deliverables:
1. Implement one concrete runtime-enforcement or hard-stop-governance delta, not just another broad scaffold.
2. Add one targeted test if code is added.
3. Add one concise doc/report under `docs/governance/` or `docs/reports/session-governance/` describing what was implemented or what exact patch is proposed.

Verification:
- if writable: targeted pytest for touched tests and one direct refresh/script invocation if applicable
- if read-only: verify by inspection only and record the exact commands that should be run later once write access is restored

Mandatory closeout:
1. If implementation succeeds, capture `/tmp/terminal-4-impl.diff`, `/tmp/terminal-4-review.md`, and reviewer outputs.
2. If the session is analysis-only, write `/tmp/terminal-4-analysis.md` with:
   - blocked write paths or permission symptoms
   - exact proposed changes by file
   - test/verification commands to run later
   - whether issue #1857, #1839, or both were analyzed
3. Keep the audit trail explicit about analysis-only versus implemented work.
