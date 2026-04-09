# Focused run — issue #1839 runtime hook integration

Repo: /mnt/local-analysis/workspace-hub
Run mode: unattended Claude with write access enabled.
Rules:
- use `uv run` for Python
- commit to `main`
- `git pull origin main` before push
- do not branch
- do not ask the user questions
- print a startup checklist immediately:
  - issue read: yes/no
  - files inspected: list
  - first implementation step: one sentence

Scope:
This is NOT a broad governance rewrite. It is a focused completion pass for the still-missing delta in #1839 after commit `fdb7c5cf0`.

Primary objective:
Wire the existing runtime enforcement logic into actual hook/invocation points so the session governor is no longer only a standalone utility.

Inspect first:
1. GH issue #1839 and latest comments
2. `.claude/settings.json`
3. `.claude/hooks/`
4. `scripts/workflow/session_governor.py`
5. `scripts/workflow/governance-checkpoints.yaml`
6. `tests/work-queue/test_session_governor.py`
7. any existing hook tests or related workflow tests

Write boundaries:
Only write to these areas unless a tiny adjacent test fixture change is unavoidable:
- `.claude/settings.json`
- `.claude/hooks/`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Do NOT write to:
- `digitalmodel/`
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.*`
- `docs/plans/overnight-prompts/2026-04-09-4claude/`

Concrete target delta:
1. Integrate `check_session_limits()` into a real hook path or wrapper path that Claude sessions can invoke automatically.
2. Keep the implementation narrow and auditable.
3. Add/extend targeted tests for the hook integration behavior.
4. Update governance docs/report for what is now enforced vs still advisory.

Suggested implementation shape:
- Prefer a small dedicated hook script under `.claude/hooks/` that calls `uv run scripts/workflow/session_governor.py --check-limits ...`
- If session metrics need to come from env or simple state files, keep that mechanism minimal and explicit
- If full automatic metrics are not available, implement the cleanest currently-available integration point and document the remaining gap precisely

Verification:
- targeted pytest for touched tests
- one direct invocation of the new hook/wrapper path
- one direct invocation of `session_governor.py --check-limits`

Mandatory closeout:
1. Capture `/tmp/issue-1839-impl.diff` and `/tmp/issue-1839-review.md`
2. Run Codex adversarial review on the committed diff
3. If blocked, write `/tmp/issue-1839-blocker.md` with exact blocker and partial progress
4. Post a brief GH issue comment on #1839 with what was implemented, verification, and what remains

Commit message:
`feat(governance): wire runtime enforcement into hooks (#1839)`
