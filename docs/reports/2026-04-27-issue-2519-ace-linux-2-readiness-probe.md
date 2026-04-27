# Issue #2519 ace-linux-2 readiness probe

> Date: 2026-04-27
> Scope: pre-delegation check for tier-1 repos and engineering program availability on `ace-linux-2`.

## Summary

`ace-linux-2` is reachable over the network/VPN and has the tier-1 repositories present under `/mnt/local-analysis/workspace-hub`, but it is **not currently ready as an autonomous Hermes/Codex/Claude execution node** because the key AI CLIs are not on `PATH` and GitHub CLI auth is invalid on that host.

Use `ace-linux-2` only after a pre-delegation gate verifies both:

1. repo/worktree readiness for the specific assigned repo; and
2. tool/auth readiness for the provider and engineering software required by the work packet.

## Connectivity / host

Probe command from `ace-linux-1`:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 'hostname; pwd; uname -a'
```

Result:

```text
ace-linux-2
/home/vamsee
Linux ace-linux-2 6.17.0-22-generic #22~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 26 15:25:54 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
```

Name resolution / ping:

```text
192.168.1.103   ace-linux-2
1 packet transmitted, 1 received, 0% packet loss
```

Disk availability:

```text
/mnt/local-analysis: 932G total, 52G used, 880G available, 6% used
```

GPU note:

```text
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.
```

Interpretation: usable for CPU/dev tasks; do not route GPU-dependent work unless the GPU driver state is repaired and re-probed.

## Tier-1 repositories on ace-linux-2

Tier-1 list from existing workspace docs: `digitalmodel`, `worldenergydata`, `assetutilities`, `teamresumes`.

Canonical location found on `ace-linux-2`: `/mnt/local-analysis/workspace-hub`.

| Repo | Path | Branch | HEAD | Remote | Dirty? | Ahead/behind | pyproject | uv.lock | .venv |
|---|---|---:|---:|---|---|---|---|---|---|
| digitalmodel | `/mnt/local-analysis/workspace-hub/digitalmodel` | main | e1274b78 | `https://github.com/vamseeachanta/digitalmodel` | no | 0 / 0 | yes | yes | yes |
| worldenergydata | `/mnt/local-analysis/workspace-hub/worldenergydata` | main | 74976b6d | `https://github.com/vamseeachanta/worldenergydata` | no | 0 / 0 | yes | yes | yes |
| assetutilities | `/mnt/local-analysis/workspace-hub/assetutilities` | main | a4c4af7 | `https://github.com/vamseeachanta/assetutilities` | no | 0 / 0 | yes | yes | yes |
| teamresumes | `/mnt/local-analysis/workspace-hub/teamresumes` | main | f904b88 | `https://github.com/vamseeachanta/teamresumes` | no | 0 / 0 | yes | yes | no |

Also found `/home/vamsee/workspace-hub`, but the tier-1 child repos are not present there. Treat `/mnt/local-analysis/workspace-hub` as the only current canonical repo root for delegation.

Workspace-hub root on `ace-linux-2` is not clean:

```text
 M .claude/state/session-signals/network-mounts.jsonl
 M config/ai_agents/ai-tools-status.yaml
?? .claude/state/session-signals/2026-04-14.jsonl
?? .claude/state/session-signals/2026-04-15.jsonl
```

Interpretation: issue #2519 should require a root cleanliness / stash / allowed-dirty-files decision before using `ace-linux-2` as a worker for workspace-hub-root changes.

## AI/dev CLI readiness on ace-linux-2

Available:

| Tool | Version / status |
|---|---|
| python3 | Python 3.12.3 |
| uv | 0.11.1 via `/snap/bin/uv` |
| git | 2.43.0 |
| gh | 2.90.0 |

Blocked / missing:

| Tool/auth | Status | Delegation impact |
|---|---|---|
| `gh auth status` | token invalid for `vamseeachanta` | Cannot safely post comments, create branches/PRs/issues, or push via `gh` until re-authenticated. |
| `hermes` | not in `PATH` | Cannot run Hermes worker/orchestration prompts directly. |
| `claude` | not in `PATH` | Cannot run Claude Code worker prompts directly. |
| `codex` | not in `PATH` | Cannot burn expiring Codex credit from this machine yet. |
| `gemini` | not in `PATH` | Cannot run Gemini CLI directly. |

Interpretation: `ace-linux-2` is currently repo-ready but not AI-agent-runtime-ready. It can become an execution worker after installing/wiring the relevant CLIs and refreshing GitHub auth.

## Engineering programs detected on ace-linux-2

Command/package evidence found:

| Program/tool | Evidence | Notes |
|---|---|---|
| OpenFOAM ESI | `openfoam-selector --list` -> `openfoam2312`; apt packages `openfoam2312*` | Good candidate for OpenFOAM/CFD tasks after case-specific smoke test. |
| Gmsh | `/usr/bin/gmsh`, version `4.12.1` | Good for mesh generation tasks. |
| FreeCAD | `/usr/bin/freecad`; apt package `freecad 0.21.2...` | CLI version probe timed out under 5s; needs headless smoke before assignment. |
| Blender | `/snap/bin/blender`; snap `blender 5.1.1`; apt `blender-data 4.0.2...` | Needs headless `blender --background` smoke before assigning render/geometry work. |
| ParaView | `/usr/bin/paraview`, `/usr/bin/pvpython`, `/usr/bin/pvbatch`; apt `paraview 5.11.2...` | GUI probe failed without display; use `pvbatch`/headless smoke for delegation. |
| CalculiX | `/usr/bin/ccx`; apt `calculix-ccx 2.21-1` | FE solver candidate after smoke test. |
| QGIS | `/usr/bin/qgis`, version `3.44.9-Solothurn` | GIS candidate; GUI/display caveats apply. |
| GDAL/OGR | `gdalinfo` / `ogrinfo` version `3.8.4` | Good for geospatial/data conversion tasks. |

Not detected in `PATH` during this probe:

- OrcaFlex / OrcaWave
- ANSYS Workbench / AQWA (`runwb2`, `ansysedt`)
- MATLAB
- Octave
- SALOME / Code_Aster (`salome`, `as_run`)

Interpretation: route Linux/open-source engineering tasks to `ace-linux-2` after smoke tests; do not assume proprietary licensed engineering software is available there.

## Required pre-delegation gate for #2519

Before delegating work to `ace-linux-2`, the Hermes control-plane on `ace-linux-1` should run a gate with these checks:

1. **Host reachability:** SSH BatchMode + ping/name resolution.
2. **Canonical root:** use `/mnt/local-analysis/workspace-hub`, not `/home/vamsee/workspace-hub`.
3. **Repo-specific readiness:** target repo exists, branch expected, clean status or approved dirty-file exception, remote ahead/behind acceptable, `.venv`/`uv.lock` state acceptable.
4. **Auth readiness:** `gh auth status` valid if the task needs GitHub mutation.
5. **Provider runtime readiness:** required AI CLI (`codex`, `claude`, `hermes`, `gemini`) exists and has valid auth/session if the worker is expected to consume that provider.
6. **Engineering software readiness:** required domain tool exists and passes a headless smoke test, not just package detection.
7. **GPU/display caveat:** do not assign GPU or GUI-dependent work unless driver/display/headless mode is explicitly validated.
8. **Dispatch ledger:** record probe timestamp, host, repo, provider, tool checks, pass/fail, and reason before launching.

## Current delegation recommendation

- `ace-linux-1`: primary control plane / orchestrator.
- `ace-linux-2`: candidate overflow worker for repo tasks and open-source engineering programs, but **blocked for direct AI-provider execution until GitHub auth and AI CLIs are fixed**.
- For the immediate Codex-expiry objective, do **not** assign Codex work to `ace-linux-2` until `codex` is installed/authenticated or Hermes on `ace-linux-1` can dispatch through an alternate mechanism that still consumes the intended Codex credit.
