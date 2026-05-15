# ace-linux-2 direct-work SSH/VNC handoff runbook

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2646
Machine registry key: `dev-secondary`
Hostname: `ace-linux-2`
Primary workspace path: `/mnt/local-analysis/workspace-hub`  # abs-path-allowed
Role: secondary Linux workstation for open-source FEA/CFD/simulation-stack work.

This runbook is for handing work from ace-linux-1/Hermes to an operator or agent running directly on ace-linux-2. It documents existing connection scripts only; it does not create a new dispatch system.

## 1. When to use ace-linux-2

Use ace-linux-2 when work benefits from the secondary Linux workstation or its open-source engineering stack:

- OpenFOAM, FreeCAD, Gmsh, ParaView, CalculiX, Blender, meshio, Capytaine, or GPU-local inspection.
- Read-only or bounded remote checks that should not block ace-linux-1.
- Direct GUI inspection where VNC is useful.
- Work explicitly routed to `dev-secondary` by a plan or issue.

Do not use ace-linux-2 for licensed Windows-only tools. Do not assume OrcaFlex, OrcaWave, AQWA, ANSYS, or other licensed Windows solvers are available on ace-linux-2.

## 2. Source-of-truth paths and scripts

From the workspace-hub repository root on ace-linux-1:

- SSH helper: `scripts/operations/connection/ssh-dev-secondary.sh`
- VNC helper: `scripts/operations/connection/vnc-ace-linux-2.sh`
- Planning-state bundle helper: `scripts/operations/workstation-handoff.sh`
- Workstation registry: `config/workstations/registry.yaml`

Remote workspace path on ace-linux-2:

```bash
cd /mnt/local-analysis/workspace-hub  # abs-path-allowed
```

A legacy path `/mnt/workspace-hub` may exist on some setups, but new handoffs should use `/mnt/local-analysis/workspace-hub` unless a live preflight proves otherwise and the issue comment records the exception.  # abs-path-allowed

## 3. Preflight checklist

Run read-only checks before assigning or continuing work. Do not mutate ace-linux-2 state until the issue plan explicitly allows it.

### 3.1 Check for local Git operations before touching the repo

On the controlling machine:

```bash
pgrep -af "git (rebase|stash|commit|merge|reset|checkout)" || true
git status --short
git branch --show-current
git rev-parse --show-toplevel
```

If another cleanup or Git operation is active, stop and wait or surface `BLOCKED` in the GitHub issue. Never use `--no-verify`.

### 3.2 SSH health and workspace path

From ace-linux-1/workspace-hub:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 'hostname; test -d /mnt/local-analysis/workspace-hub/.git; git -C /mnt/local-analysis/workspace-hub status --short'  # abs-path-allowed
```

Expected:

- Hostname prints `ace-linux-2`.
- The workspace path exists and is a Git checkout.
- Dirty state is either empty or explicitly owned by the current handoff.

If the hostname alias fails, use the helper script for interactive access, or fall back to the registry Tailscale IP if needed:

```bash
scripts/operations/connection/ssh-dev-secondary.sh
ssh vamsee@10.1.0.2 'hostname'
```

### 3.3 Required tool presence

Use read-only `command -v` checks:

```bash
ssh ace-linux-2 'for t in git uv tmux claude openfoam2312 blender gmsh paraview; do printf "%s: " "$t"; command -v "$t" || true; done'
```

Only require the tools needed for the assigned issue. Missing optional engineering tools should be recorded as a blocker only if the task requires them.

### 3.4 VNC readiness, only when GUI is needed

Use SSH-only mode unless a GUI is required. For VNC preflight:

```bash
ssh ace-linux-2 'pgrep -af "Xtigervnc|x11vnc|vnc" || true; ss -tlnp 2>/dev/null | grep -E ":5900|:5901" || true'
```

This check is read-only. The VNC helper can start `x11vnc` if absent; treat that as a remote-state mutation and only run it when GUI work is intended.

## 4. Handoff mode A: SSH-only

Use SSH-only for terminal work, Git inspection, scripted checks, docs edits, tests, and non-GUI agent sessions.

Interactive shell:

```bash
scripts/operations/connection/ssh-dev-secondary.sh
```

Direct one-liner without the helper:

```bash
ssh ace-linux-2 'cd /mnt/local-analysis/workspace-hub && git status --short && git branch --show-current'  # abs-path-allowed
```

Start a long-running session with tmux:

```bash
ssh ace-linux-2 'cd /mnt/local-analysis/workspace-hub && tmux new -As issue-ISSUE_NUMBER'  # abs-path-allowed
```

Recommended SSH-only workflow:

1. Confirm the GitHub issue is `status:plan-approved` before implementation.
2. Confirm the remote checkout is clean or identify every dirty file owner.
3. Pull/rebase only if the handoff explicitly allows updating the remote checkout.
4. Run the worker prompt from Section 6 inside the remote shell or tmux session.
5. Return results via the protocol in Section 7.

## 5. Handoff mode B: VNC-needed

Use VNC only when GUI inspection or GUI tools are required. Prefer SSH-only for all terminal work.

From ace-linux-1/workspace-hub:

```bash
scripts/operations/connection/vnc-ace-linux-2.sh
```

What the helper does:

- Verifies `xtigervncviewer` exists locally.
- Checks whether `x11vnc` is listening on ace-linux-2 port 5900.
- If missing, attempts to discover the active X display and start `x11vnc` on localhost-only port 5900.
- Opens an SSH tunnel from local port 5900 to ace-linux-2 localhost:5900.
- Launches `xtigervncviewer localhost:5900`.
- Closes the tunnel when the viewer exits.

Reconnect procedure:

```bash
pgrep -af "ssh -L 5900:localhost:5900" || true
pkill -f "ssh -L 5900:localhost:5900" 2>/dev/null || true
scripts/operations/connection/vnc-ace-linux-2.sh
```

If the helper cannot find a display, stop and comment `BLOCKED`; do not improvise sudo/systemd changes unless the issue plan explicitly permits remote machine mutation.

## 6. Copy/paste worker prompt template

Paste this into the agent or operator session running on ace-linux-2. Fill placeholders first.

```text
You are working directly on ace-linux-2 for workspace-hub issue ISSUE_NUMBER.

Repository:
- WORKSPACE=/mnt/local-analysis/workspace-hub  # abs-path-allowed
- Branch/worktree ownership: DESCRIBE_BRANCH_OR_WORKTREE
- GitHub issue: https://github.com/vamseeachanta/workspace-hub/issues/ISSUE_NUMBER
- Approved plan: docs/plans/PLAN_FILE.md

Hard rules:
- Never use --no-verify.
- Never self-approve or bypass plan/adversarial-review gates.
- On 3+ retries on the same error, stop and report BLOCKED.
- Before Git mutation, run: pgrep -af "git (rebase|stash|commit|merge|reset|checkout)" || true
- Do not store secrets, tokens, private keys, or credentials in files, logs, or GitHub comments.
- Do not assume OrcaFlex, OrcaWave, AQWA, ANSYS, or Windows-only licensed tools are available on ace-linux-2.

Allowed paths:
- LIST_ALLOWED_FILES_OR_DIRS

Forbidden paths:
- LIST_FORBIDDEN_FILES_OR_DIRS

Task:
- RESTATE_APPROVED_PLAN_SCOPE

Required validation:
- LIST_EXACT_TEST_OR_VERIFICATION_COMMANDS

Return format:
1. Current state: completed | blocked | partial
2. Files changed: list paths
3. Commands run: list commands and exit status
4. Evidence: paste concise relevant output or path to committed report
5. Blockers: exact blocker, retry count, and next required human/action if any
6. Git state: branch, commit SHA if committed, `git status --short`
```

## 7. Return protocol

Every ace-linux-2 direct-work handoff must return enough evidence for Hermes on ace-linux-1 to verify without guessing.

### 7.1 Completion comment format

Post or hand back this comment body for the GitHub issue:

```markdown
## ace-linux-2 handoff result

State: COMPLETED | PARTIAL | BLOCKED
Machine: ace-linux-2
Workspace: /mnt/local-analysis/workspace-hub  # abs-path-allowed
Branch/worktree: BRANCH_OR_WORKTREE
Commit: SHA_OR_NONE

Files changed:
- path/to/file

Validation:
- `COMMAND` → exit N
- `COMMAND` → exit N

Evidence:
- Concise output, report path, or artifact path

Blockers / follow-up:
- None, or exact blocker and next action
```

### 7.2 Log and artifact locations

Use the smallest durable evidence surface that satisfies the issue:

- GitHub issue comment for short terminal evidence and blocker reports.
- `docs/reports/` for durable reports that should remain in the repo.
- `docs/session-handoffs/` for session-exit handoffs.
- `/tmp/` only for scratch files that do not need to survive.

Do not put secrets, tokens, private keys, full environment dumps, or license details in any log, report, or comment.

### 7.3 Blocked stop condition

Stop and return `BLOCKED` if any of these occur:

- Same error has been retried three times.
- Git state is unsafe and ownership is unclear.
- Remote state mutation is required but not allowed by the issue plan.
- Required tool is missing and installing it would mutate ace-linux-2.
- VNC/display setup requires sudo/systemd changes not explicitly approved.

## 8. Planning-state bundles

`scripts/operations/workstation-handoff.sh` packages GSD planning state into a tarball. Use it when a worker needs a portable planning context bundle, not as a replacement for this runbook.

Examples:

```bash
scripts/operations/workstation-handoff.sh --phase 3 --dry-run
scripts/operations/workstation-handoff.sh --wrk WRK-123 --output /tmp/handoff-WRK-123.tar.gz
```

Keep generated tarballs out of the repository unless a plan explicitly says to commit them.

## 9. Security and licensed-tool boundaries

- Never store API keys, SSH private keys, GitHub tokens, license files, or passwords in repo files, terminal logs, or GitHub comments.
- Do not paste full `env` output into comments or reports.
- Do not assume OrcaFlex, OrcaWave, AQWA, ANSYS, or other licensed Windows tools are present on ace-linux-2.
- Treat ace-linux-2 as an open-source Linux engineering workstation unless live evidence and the issue plan say otherwise.
- For wrapper-style checks involving SSH or VNC, run read-only checks first and surface before mutating remote machine state.

## 10. Quick operator checklist

Before work:

- [ ] Issue is open and `status:plan-approved`.
- [ ] Approved plan path is known.
- [ ] `pgrep -af "git (rebase|stash|commit|merge|reset|checkout)" || true` checked on controlling checkout.
- [ ] SSH preflight confirms `ace-linux-2` and `/mnt/local-analysis/workspace-hub`.  # abs-path-allowed
- [ ] Dirty Git state is clean or explicitly owned.
- [ ] Needed tools are present.
- [ ] VNC used only if GUI is required.

After work:

- [ ] Tests/verification commands were run and recorded with exit codes.
- [ ] Changes are committed and pushed when the issue plan requires it.
- [ ] GitHub issue has a progress/completion/blocker comment.
- [ ] Any remote dirty state left behind is explicitly documented.
