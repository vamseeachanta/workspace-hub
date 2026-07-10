# Exit handoff — ace-win-2 ecosystem reconciliation

Date: 2026-07-10
Machine: `ace-win-2`
Repo: `workspace-hub`
Branch: `main`

## Active task

Reconcile ace-win-2 with the repo ecosystem and machine-equality matrix, preserve
parallel work, publish verified evidence, and prepare an executable ace-win-1 handover.

## Completed

- Used the canonical `ecosystem-equivalence-reconcile` workflow report-first.
- Applied the auto-safe subset. It deleted one proven squash-merged local branch in
  `digitalmodel`; no dirty work was discarded.
- Fast-forwarded `workspace-hub` while preserving generated curation artifacts through
  remote races.
- Rebuilt the SOUL runtime artifacts and verified `check-soul-runtime-drift.sh` passed.
- Ran `install-soul-runtime.sh`:
  - backed up the prior Codex runtime file to
    `~/.codex/AGENTS.md.pre-install-backup.20260710T025008Z`;
  - Git Bash reported a link install, but the final Windows object is an ordinary file
    (`LinkType` empty), not an NTFS symlink.
- Registered and verified the seven canonical `\Claude\` scheduled tasks as `Ready`:
  `ContextManagementDaily`, `EqualityReport`, `HarnessUpdate`, `MemoryBridgeSync`,
  `NightlyReadiness`, `RepoSync`, and `WorkstationVersionCheck`.
- Ran Windows session curation successfully with `PYTHONUTF8=1`:
  - `last_curated_at: 2026-07-10T07:56:23+00:00`;
  - 58 sessions/24h across Claude and Codex;
  - skill drift clean; skill-link health collected.
- Refreshed ace-win-2 equality evidence and the matrix.
- Created the ace-win-1 entry prompt at
  `docs/session-handoffs/2026-07-09-ace-win-1-ecosystem-reconcile-entry-prompt.md`.
- Validated changed JSON/YAML, ran `git diff --check`, and passed
  `scripts/legal/legal-sanity-scan.sh --diff-only`.
- Committed and pushed
  [`ed4e181f8`](https://github.com/vamseeachanta/workspace-hub/commit/ed4e181f8bdf376142fb7df020018e1a5710f26e)
  (`chore(equality): reconcile ace-win-2 and hand off ace-win-1`).

## Verified repo and parallel-work state

- Before staging this exit handoff, `workspace-hub` was clean and synchronized with
  `origin/main` at `ed4e181f8`. The final handoff commit/push SHA must be reported in
  the session's final status rather than embedded self-referentially here.
- `workspace-hub` linked worktrees: issues
  [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424) and
  [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443), preserved as
  active parallel work.
- `deckhand`: clean `main`; the earlier issue-529 stash is no longer present. A
  transient edit to `scripts/deckhand/licensed-run-agent/run-agent.cmd` appeared during
  adversarial review and was resolved by its external owner before the final audit.
- `llm-wiki-acma`: clean `chore/issue-215-it-tooling-plan`; linked worktrees for
  issues 214 and 216 are preserved as active parallel work. The issue-214 worktree is
  clean; four plan-review result files observed during adversarial review were
  dispositioned by its external owner before the final audit.
- No in-repo `*.partial` or `*.tmp` files were found.
- No `C:\ws\.cleanup-lock`, `C:\ws\.cleanup-trash`, or abandoned equality-publish
  worktree was found.
- No external email/message was sent and no GitHub issue was closed in this session.
- At `04:30:01-05:00`, the newly registered `MemoryBridgeSync` schedule modified
  `.claude/memory/agents.md` and `.claude/memory/topics/INDEX.md`. The exact timestamp
  matches its configured 04:30 run. Those generated changes are not part of this exit
  handoff commit and are preserved for the memory-bridge owner to validate/disposition.

## Residual equality findings

The final report-only run at `2026-07-10T03:52:40-05:00` returned one auto-safe
suggestion, nine approval-gated findings, and one operator-only finding. Repeated
collection will not clear all of these because several are measurement or policy gaps:

1. `memory_freshness` remains `MISSING-EVIDENCE` because the bridge heartbeat and
   Hermes memory store are absent. `check-memory-drift.sh` confirmed this host has no
   Hermes memory to bridge.
2. The three Hermes provider-capability cells remain divergent because `~/.hermes`
   memory, skill registry, and active runtime surfaces are absent, although a Hermes
   executable exists under `%LOCALAPPDATA%`.
3. The scheduler cell still reports zero jobs because `collect-equality.sh` deliberately
   skips scheduler enumeration for `OS=windows`. Native Task Scheduler is the verified
   machine truth: seven tasks were `Ready`.
4. Harness/behavior group verdicts remain divergent/no-majority. The actual ace-win-2
   behavior enums and permission hash matched both Linux peers; the group verdict is
   affected by other peer/provider differences.
5. Solver status remains operator-only: the probe reports `present` rather than
   `licensed`; follow the note in
   [PR #2850](https://github.com/vamseeachanta/workspace-hub/pull/2850).
6. The broad full-repo legal scan still finds pre-existing legacy/public engineering
   content. The task-scoped `--diff-only` publication gate passed.
7. The ace-win-2 evidence uses `acma-ws014`, which is a tracked public alias under
   `config/workstations/registry.yaml`. Unlike ace-win-1, no private-hostname collision
   is documented for this machine. If that policy changes, contain the published
   evidence and route redaction through the legal/issue workflow immediately.

## Remaining action items — recommended order

1. **Run ace-win-1 reconciliation.** Use
   `docs/session-handoffs/2026-07-09-ace-win-1-ecosystem-reconcile-entry-prompt.md`.
   Preserve its PII boundary: never publish the raw OS hostname. Stop if the collector
   or scheduler cannot honor the PII-safe `ace-win-1` label.
2. **Plan a PII-safe Windows equality fix.** Create/use a GitHub issue for:
   - native Task Scheduler enumeration in Windows evidence;
   - a real machine-label/host-redaction override across collector, curation, scheduler,
     and equality publication;
   - the confirmed parameter defect: `refresh-equality-matrix.ps1 -Machine` passes a
     `Machine` argument to `equality-report.ps1`, whose top-level parameter block does
     not accept it;
   - a Windows-safe publisher lock instead of the missing Git Bash `flock` command.
   This is implementation work: issue → plan → adversarial review → explicit user
   approval → TDD → code review. Never self-approve the plan.
3. **Plan the curation UTF-8 fix.** `curate-session-memory.ps1` should set
   `PYTHONUTF8=1` before invoking its Python engine, as `equality-report.ps1` already
   does. Until then, keep the environment workaround in operator prompts.
4. **Plan Windows runtime-install semantics.** Decide whether the installer should use
   an NTFS symlink, hard link, or verified copy when `core.symlinks=false`; it must not
   report `LINK` for an ordinary file without stating the actual object type.
5. **Decide whether Hermes is required on licensed Windows hosts.** If yes, define and
   install the supported Windows home/config/memory path. If no, grade the absent Hermes
   surfaces as expected divergence rather than perpetual failure.
6. **Run the solver licence follow-up** when the licensed application can be opened and
   checked interactively.
7. **Prune worktrees only after their issues finish.** Recheck ownership/activity for
   workspace-hub issues 3424/3443 and llm-wiki-acma issues 214/216 before any guarded
   removal.

## Expected residue

- Active issue worktrees named above.
- Two generated memory files from the 04:30 `MemoryBridgeSync` run:
  `.claude/memory/agents.md` and `.claude/memory/topics/INDEX.md`. They remain
  uncommitted and must be validated through the memory-bridge workflow before landing.
- `~/.codex/AGENTS.md.pre-install-backup.20260710T025008Z`, retained for rollback and
  forensics.
- Ambient Windows/Outlook/Adobe temp logs under `%TEMP%`; none were created as requested
  deliverables and none were deleted.

## Cleanup verdict

`EXPECTED` — only the named active worktrees, scheduled-memory outputs, runtime backup,
and ambient operating-system temp files remain. No unexpected task residue remained at
the final audit.

## Exact next checkpoint

Open a new session on ace-win-1 with the committed entry prompt, run its startup and
report-only reconciliation, and stop at the first PII/identity or approval-gated
blocker. Return evidence to the Windows equality follow-up issue before changing code.
