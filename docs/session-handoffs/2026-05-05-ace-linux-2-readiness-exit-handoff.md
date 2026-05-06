# 2026-05-05 Exit Handoff — ace-linux-2 readiness setup / branch cleanup

Timestamp: 2026-05-05 22:20 CDT  
Repo: `workspace-hub`  
Canonical checkout: `/mnt/local-analysis/workspace-hub`  
Exit commit base when this handoff was prepared: `71ebcc57350df7fcff50db86d4a9cc881d856e0c`

## User objective

User wants ace-linux-2 made ready to perform work directly from this computer, including repo files, `/mnt` drives, and a concrete multi-machine plan for dispatching work from ace-linux-1/control plane to ace-linux-2/overflow.

## What happened this session

1. Loaded relevant multi-machine / workstation orchestration skills at the start:
   - `coordination/workstation-aware-provider-orchestration`
   - `software-development/multi-machine-ai-readiness-and-issue-triage`
   - `coordination/ace-linux-1-control-surface`
   - `workspace-hub/external-drive-ingest-planning`
2. Session was interrupted by cleanup requests for branch `chore/strip-raw-pdfs-to-mnt-ace`.
3. Verified and pushed the branch earlier with commits:
   - `7d05256a2 chore(license): strip vendor-derivative PDFs to /mnt/ace, gitignore future`
   - `f4e724e0b chore(state): record session signals`
   - `1ecbe0d39 docs(sessions): add B1528 moored-current handoff`
4. Merged `chore/strip-raw-pdfs-to-mnt-ace` into `main` using a clean temporary integration worktree because root checkout had live-generated state churn.
5. Resolved merge conflicts only in generated/live session-state files by taking `--ours`; durable artifact `docs/session-handoffs/2026-05-05-b1528-moored-current-exit-handoff.md` was already identical on `origin/main`.
6. Pushed merge commit to `origin/main`:
   - `c031fc0715f2ebe2d6860848ec9a07526b9a465a Merge branch 'chore/strip-raw-pdfs-to-mnt-ace'`
7. Deleted stale branch:
   - remote `origin/chore/strip-raw-pdfs-to-mnt-ace`: deleted
   - local `chore/strip-raw-pdfs-to-mnt-ace`: deleted
   - temporary merge worktree/branch: removed
8. A later cleanup-stream handoff advanced `origin/main` to:
   - `71ebcc57350df7fcff50db86d4a9cc881d856e0c docs(sessions): fix recovery-tag count in cleanup-stream handoff (19 → 13)`

## Verified state before exit handoff

Remote/local main sync:

```text
HEAD        = 71ebcc57350df7fcff50db86d4a9cc881d856e0c
origin/main = 71ebcc57350df7fcff50db86d4a9cc881d856e0c
local_ahead = 0
local_behind = 0
```

Stale branch cleanup proof:

```text
branch commit 1ecbe0d39 contained in origin/main = yes
remote feature heads for chore/strip-raw-pdfs-to-mnt-ace = 0
local branches matching *strip-raw-pdfs* = 0
registered temp worktrees matching strip/merge = none
```

Important caveat:

- Broad `git diff --name-only` and `git ls-files --others --exclude-standard` from the live root timed out under `timeout 10` during exit checks.
- Treat the live root as potentially affected by concurrent/generated churn; use clean temporary worktrees for final documentation commits or future transactional closeout.

## Current unstarted work: ace-linux-2 readiness

No concrete ace-linux-2 readiness implementation was completed yet. The next session should start from this objective rather than assuming setup is done.

Recommended first-pass plan:

1. Inventory ace-linux-1 current repo/mount/control-plane state.
2. Inventory ace-linux-2 via SSH or direct shell:
   - OS/user/home paths
   - disk layout and mounted `/mnt/*` drives
   - repo locations and remotes
   - GitHub auth and write permissions
   - Hermes/Claude/Codex/Gemini availability and auth state
   - Python/uv/node/devtools availability
3. Build a machine-readiness matrix for both machines:
   - repo presence
   - branch sync status
   - mount availability
   - tool/auth readiness
   - safe work categories per host
   - blockers and exact remediation commands
4. Decide canonical storage layout for ace-linux-2:
   - mirror `/mnt/local-analysis/...` if possible
   - confirm `/mnt/ace/...` availability or mount plan
   - avoid duplicating vendor/raw/client files unless provenance and gitignore rules are clear
5. Create an execution packet/runbook under `docs/` with:
   - setup commands
   - sync commands
   - validation commands
   - dispatch rules from ace-linux-1 to ace-linux-2
   - rollback/cleanup rules
6. Only after readiness proof, start dispatching work to ace-linux-2.

## Skills to load next session

Load these before continuing the multi-machine work:

- `coordination/workstation-aware-provider-orchestration`
- `software-development/multi-machine-ai-readiness-and-issue-triage`
- `coordination/ace-linux-1-control-surface`
- `workspace-hub/external-drive-ingest-planning`
- `coordination/artifact-verification`
- `workspace-hub/worktree-branch-sync-hygiene`

## Suggested next operator prompt

```text
Resume from docs/session-handoffs/2026-05-05-ace-linux-2-readiness-exit-handoff.md. Build the concrete ace-linux-1 ↔ ace-linux-2 readiness plan. First inventory both machines' repo roots, /mnt mounts, GitHub auth, Hermes/provider auth, and toolchains. Produce a computable readiness matrix and a concrete remediation/runbook before dispatching work to ace-linux-2. Do not assume ace-linux-2 is ready until verified.
```

## Exit rules

- Do not reopen `chore/strip-raw-pdfs-to-mnt-ace`; it is merged and deleted.
- Do not mutate live-root generated dirt without first proving ownership.
- Prefer clean temporary worktrees for docs-only commits if root git operations hang.
- Keep ace-linux-1 as the control surface; ace-linux-2 is overflow only after repo/tool/auth/mount checks pass.
