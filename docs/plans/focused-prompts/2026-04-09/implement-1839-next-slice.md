# Claude worker — implement #1839 next slice

Repo: /mnt/local-analysis/workspace-hub
Mode: implementation with write access enabled.

Goal:
Implement the highest-value next slice for issue #1839 identified in `.planning/iterative-finding-cocoa.md`:
1. plan-approval hard-stop hook
2. strict review gate by default
3. align/remove old 500-call ceiling hook so only one active ceiling model remains

Rules:
- use `uv run` for Python where needed
- commit to `main`
- `git pull origin main` before push
- do not branch
- do not ask the user questions
- print a startup checklist immediately:
  - issue read: yes/no
  - files inspected: list
  - first implementation step: one sentence

Inspect first:
1. GH issue #1839 and latest comments
2. `.planning/iterative-finding-cocoa.md`
3. `.claude/settings.json`
4. `.claude/hooks/`
5. `scripts/workflow/governance-checkpoints.yaml`
6. `scripts/workflow/session_governor.py`
7. any tests under `tests/work-queue/` and hook-related tests

Write boundaries:
Only write to:
- `.claude/settings.json`
- `.claude/hooks/`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Concrete target delta:
1. Add a real plan-approval enforcement hook for implementation tools or bash write/push paths.
2. Make review gate strict by default in the currently active enforcement path.
3. Remove or align the old 500-ceiling enforcement so it does not conflict with the 200-call session governor path.
4. Add/extend targeted tests proving the new behavior.
5. Update docs/reporting with exactly what is now enforced.

Implementation guidance:
- Prefer minimal, auditable hook changes over a broad rewrite.
- If an approval marker path is needed, use a simple explicit convention and document it clearly.
- Avoid introducing a second competing mechanism for the same gate.
- If a tiny part must stay advisory, document the exact remaining gap.

Verification:
- targeted pytest for touched tests
- one direct hook/script invocation per new gate if practical
- one configuration/readout check showing strict review gate default

Mandatory closeout:
1. Capture `/tmp/issue-1839-next-slice-impl.diff` and `/tmp/issue-1839-next-slice-review.md`
2. Run Codex adversarial review on the committed diff
3. If blocked, write `/tmp/issue-1839-next-slice-blocker.md` with exact blocker and partial progress
4. Post a brief GH issue comment on #1839 with what was implemented, verification, and updated remaining items

Commit message:
`feat(governance): enforce plan approval and strict review defaults (#1839)`
