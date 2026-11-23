You are working in /mnt/local-analysis/workspace-hub.

Read and follow first:
- AGENTS.md
- CLAUDE.md

Task:
Implement Work Package 5 only for Windows Claude Code parity.

Goal:
Close the remaining Windows write-back parity gap using the existing bridge/scheduler infrastructure, and reconcile the related operator docs only after the implementation is real.

Target files
- scripts/memory/bridge-hermes-claude.sh
- scripts/windows/setup-scheduler-tasks.ps1
- .claude/docs/new-machine-setup.md
- docs/sessions/skills-unification-stream-exit-report.md

Strict scope
- Only edit the 4 target files above
- Do not edit hooks
- Do not edit Claude settings
- Do not edit readiness scripts/config
- Do not create new files
- Do not commit

Implementation intent
- Use the existing scripts/memory/bridge-hermes-claude.sh as the implementation anchor for Windows-side write-back parity.
- Make the smallest repo-grounded change that gives Windows an explicit documented/scheduled path to refresh repo-tracked memory outputs.
- Then reconcile the docs so they no longer overstate or understate Windows parity.
- Do not invent a broad new architecture.

Constraints
- Keep Linux behavior intact.
- Keep Windows behavior conservative and explicit.
- If Windows cannot support full automatic equivalence, document the exact supported path honestly.
- Update docs only to match the implemented repo behavior.

Required outcomes
1. bridge-hermes-claude.sh should no longer read as Linux/Hermes-only in a way that makes Windows parity impossible.
2. setup-scheduler-tasks.ps1 should clearly reflect the Windows path to shared memory/write-back parity if that path belongs there.
3. .claude/docs/new-machine-setup.md should stop saying Windows has only two tasks if that is no longer true.
4. docs/sessions/skills-unification-stream-exit-report.md should accurately reflect the current state of the Windows write-back gap after your changes.

Required verification
Run all of these and report results:
- bash -n scripts/memory/bridge-hermes-claude.sh
- grep -nE 'Windows|licensed-win-1|bridge-hermes-claude|Task Scheduler|two tasks|#1918|Windows auto-memory sync' scripts/memory/bridge-hermes-claude.sh scripts/windows/setup-scheduler-tasks.ps1 .claude/docs/new-machine-setup.md docs/sessions/skills-unification-stream-exit-report.md || true
- git diff -- scripts/memory/bridge-hermes-claude.sh scripts/windows/setup-scheduler-tasks.ps1 .claude/docs/new-machine-setup.md docs/sessions/skills-unification-stream-exit-report.md
- git status --short -- scripts/memory/bridge-hermes-claude.sh scripts/windows/setup-scheduler-tasks.ps1 .claude/docs/new-machine-setup.md docs/sessions/skills-unification-stream-exit-report.md

Output format
1. What you changed
2. How Windows write-back parity is now implemented or clarified
3. What doc drift was corrected
4. Verification results
5. Explicit confirmation that no files outside the allowed scope were modified
6. Stop without committing
