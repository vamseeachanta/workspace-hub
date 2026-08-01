# Exit handoff — ace-win-2 machine-equivalence reconciliation

Date: 2026-07-13
Machine: `ace-win-2`
Repo: `workspace-hub`
Branch: `main`

## Active task

Bring this Windows workstation toward repo-ecosystem and machine-equality parity,
refresh the machine-equivalence matrix, preserve unrelated work, and leave a verified
restart point for the remaining Windows-specific blockers.

## Completed

- Ran the canonical `ecosystem-equivalence-reconcile` workflow report-first and
  preserved all active issue worktrees.
- Preserved the pre-existing 11-path canonical dirt in stash
  `a15a6d7b1ad5d6d0303cdf6034d544b26001400c`, named
  `reconcile-ace-win-2-preserve-2026-07-13T0503-CDT`.
- Fast-forwarded canonical `C:\ws\workspace-hub` without reset, force, or rebase.
- Refreshed and published canonical ace-win-2 equality evidence plus the dated/stable
  HTML matrix in
  [`0d281835f`](https://github.com/vamseeachanta/workspace-hub/commit/0d281835f).
- Rebuilt the Codex runtime skill index, verified the generated artifact, installed
  content-equivalent runtime state, and published
  [`7b0789cb4`](https://github.com/vamseeachanta/workspace-hub/commit/7b0789cb4).
- Refreshed Windows session curation with `PYTHONUTF8=1`: 47 sessions in 24 hours
  across Claude, Codex, and Gemini; skill drift clean; published the exact 10-file
  evidence transaction in
  [`1dec1e1a2`](https://github.com/vamseeachanta/workspace-hub/commit/1dec1e1a2).
- Passed JSON/YAML validation, SOUL-runtime drift/build tests, `git diff --check`,
  task-scoped legal scans, and adversarial artifact reviews.
- Verified the [live matrix](https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html)
  returns HTTP 200, reports 10 ace-win-2 gaps, and grades session curation
  `CURATED-FRESH`.
- Posted transactional evidence to
  [#3506](https://github.com/vamseeachanta/workspace-hub/issues/3506#issuecomment-4956855861).

## Verified repo and parallel-work state

- Before this handoff edit, canonical `main` was clean and synchronized at
  `f4531ed4c`; the three task commits above are ancestors of `origin/main`.
- Workspace-hub worktrees for
  [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424) and
  [#3443](https://github.com/vamseeachanta/workspace-hub/issues/3443) remain active
  and untouched.
- The temporary equality clone was removed. No `.cleanup-lock`, `.cleanup-trash`,
  Git index lock, in-repo `*.partial`, or `*.tmp` residue remained.
- During rollback, the disconnected `equivalence-state` ref was restored and verified
  at `3b54f621bf0fbc2cee9736433d38c39ff1389101`; no corrupt fingerprint remained from
  this session. Normal fleet publishing subsequently advanced the live ref to
  `120a6a3f1eee05134ee599cd0aa71b2f34f8c802`, verified immediately before handoff.
- No email or external message was sent. No issue was closed.

## Current machine-equality result

Green/current evidence includes compute, required data access, kanban, Claude/Codex
provider capabilities, Gemini memory/workflow capabilities, skill-link health, and
session curation.

Ten gaps remain:

1. `solvers: BELOW-BASELINE` — the probe proves presence, not interactive licence
   availability; operator follow-up is still required.
2. `harness`, `memory`, and `behavior: DIVERGES` — the local snapshot is fresh; these
   require peer refresh and/or policy reconciliation rather than another local collect.
3. `scheduler: DIVERGES` — seven native `\Claude\` tasks are Ready, but the Windows
   collector reports zero scheduler jobs.
4. Three Hermes capability rows diverge because this Windows role has no Hermes
   home/memory/runtime surfaces.
5. `memory_freshness: MISSING-EVIDENCE` because bridge/Hermes memory evidence is absent.
6. `publish_health: MISSING-EVIDENCE` because ace-win-2 cannot safely publish its
   equivalence fingerprint yet.

## Open blockers

- [#3506](https://github.com/vamseeachanta/workspace-hub/issues/3506) remains open;
  its done condition requires a valid ace-win-2 fingerprint and green publish health.
- [#3511](https://github.com/vamseeachanta/workspace-hub/issues/3511) is
  `status:needs-plan`: Windows sentinel uses the Store `python3` stub, fails open with
  zero-byte JSON, defaults the host role to `unknown`, and can corrupt `mktree`
  filenames through CRLF text I/O.
- [#3513](https://github.com/vamseeachanta/workspace-hub/issues/3513) is
  `status:needs-plan`: the Windows SOUL installer reports `LINK` while producing an
  ordinary file and accumulating backups.
- Whether Hermes is required on licensed Windows hosts remains a policy decision. If
  not required, those cells should be graded as expected divergence instead of defects.

## Expected residue

- Preserved stash `a15a6d7b1ad5d6d0303cdf6034d544b26001400c` contains 11 paths
  (374 insertions, 28 deletions), including an untracked draft plan and session-report
  outputs. Keep it until deliberately reconciled. Never apply this 117-commit-old stash
  directly onto canonical `main`. Create an isolated clean recovery branch/worktree at
  an intentional base, apply immutable hash
  `a15a6d7b1ad5d6d0303cdf6034d544b26001400c` there (not `pop`), and verify all 11 paths,
  including the upstream-overlapping `.claude/memory/topics/INDEX.md`, before dropping
  the stash.
- Active issue worktrees named above and the llm-wiki-acma issue worktrees remain
  intentionally preserved.
- `~/.codex/AGENTS.md.pre-install-backup.20260713T050444Z` is retained for rollback;
  current runtime content hash matched the repo source at install time.
- Report-only reconciliation logs under `logs/quality/` are expected local evidence.

## Exact next checkpoint

Start with [#3511](https://github.com/vamseeachanta/workspace-hub/issues/3511): run
resource intelligence, draft the issue plan, dispatch adversarial plan review, and stop
for explicit user approval. Do not self-apply `status:plan-approved`. After an approved
TDD implementation lands, run the Windows sentinel from canonical `main`, prove a
non-empty alias-correct fingerprint lands without CRLF corruption, re-run the Windows
equality publisher, verify `publish_health` is green in the live matrix, comment on and
close [#3506](https://github.com/vamseeachanta/workspace-hub/issues/3506) only when its
done condition is met. Reconcile the preserved stash separately after that checkpoint.

## Cleanup verdict

`EXPECTED` — only the named stash, active worktrees, runtime backup, and local quality
logs remain. No unexpected task residue is known.
