# Baseline inventory first for multi-machine work

Use this reference when a user wants to deploy work from a secondary machine or prepare multi-machine automation. Start from the physical/logical inventory before designing queues, solver automation, or provider dispatch.

## Session learning

The user corrected an over-solver-focused plan: the plan must begin with the most basic operational facts:

- what machines exist and their roles;
- what repos should be cloned on each machine;
- what files, raw data, knowledge stores, llm-wikis, and mounted drives each machine can access;
- which AI programs are available and authenticated on each machine;
- which engineering/simulation programs are available, and which are explicitly not;
- what drift exists between registry/config and observed live state.

## Recommended baseline matrix

Produce this matrix before implementation planning:

| Machine | Role | Required repos | Local storage | Remote mounts | AI tools | Engineering tools | Gaps/blockers |
|---|---|---|---|---|---|---|---|
| primary control plane | approvals, GitHub mutation, dispatch ledger, repo source of truth | workspace-hub + tier-1 repos | canonical workspace + knowledge/rawdata disk | secondary machine storage if available | hermes/claude/codex/gemini/gh/git/uv/tmux | as observed | dirty repos, stale auth, low disk |
| secondary worker | isolated implementation, preprocessing, open-source simulation | workspace-hub + repos needed for worker tasks | local scratch/bulk disk | read-only or controlled access to primary knowledge/rawdata | provider CLIs via login shell | open-source solvers/tools | stale workspace root, missing repos, invalid gh |
| licensed host | proprietary solver execution only | workspace-hub queue processor + solver project inputs | local solver work area | optional sync share or Git queue | optional | OrcaWave/OrcaFlex/AQWA/ANSYS as applicable | no SSH, Task Scheduler bootstrap needed |

## Probe commands

Use direct shell probes rather than relying on stale registry values:

```bash
hostname
findmnt -R /mnt || true
df -hT / /mnt/local-analysis /mnt/ace /mnt/dde 2>/dev/null || true
find /mnt/local-analysis /mnt/ace /mnt/dde -maxdepth 2 -name .git -type d 2>/dev/null | sed 's#/.git$##' | sort
for c in hermes claude codex gemini gh git uv tmux python3; do command -v "$c" || echo "$c:not-found"; done
```

Remote worker pattern:

```bash
ssh ace-linux-2 'bash -lc '\''hostname; findmnt -R /mnt || true; df -hT / /mnt/local-analysis /mnt/dde /mnt/remote/ace-linux-1/ace 2>/dev/null || true; for c in hermes claude codex gemini gh git uv tmux python3; do command -v "$c" || echo "$c:not-found"; done'\'''
```

## Workspace-hub example facts discovered in the session

Treat these as a starting hypothesis and rerun probes before acting:

- `ace-linux-1` is the control plane with canonical workspace `/mnt/local-analysis/workspace-hub` and canonical knowledge/rawdata store `/mnt/ace`.
- `ace-linux-2` was reachable by SSH and had actual workspace `/mnt/local-analysis/workspace-hub`; registry/config still referenced stale `/mnt/workspace-hub` in some places.
- `ace-linux-2` had access to primary knowledge data through `/mnt/remote/ace-linux-1/ace` and primary workspace through `/mnt/remote/ace-linux-1/local-analysis`.
- `ace-linux-2` had AI CLIs visible (`claude`, `codex`, `gemini`, `hermes`) but registry under-reported agent CLIs.
- `ace-linux-2` did not have proprietary solver stack: no OrcaWave, OrcaFlex, AQWA/ANSYS, MATLAB, or Python `OrcFxAPI`.
- Licensed Windows hosts were represented in the registry but had `ssh: null`, so Linux-origin verification/bootstrap was blocked and requires GUI/Task Scheduler or another remote-access method.
- `/mnt/ace` was storage-constrained, so large rawdata/result workflows need capacity policy before automation.

## Pitfall

Do not let a concrete implementation target (for example solver queue/inbox automation) skip the foundational inventory. If the user asks for multi-machine readiness, first answer the machine/repo/mount/tool/rawdata matrix, then derive automation phases from the gaps.
